import sqlite3
import mysql.connector
from .models import Field


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DBConnectionFactory(metaclass=SingletonMeta):
    def create_connection(self, config: dict, name: str):
        db_conf = config.get(name)
        engine = db_conf.get('ENGINE', 'mysql')
        if engine == 'sqlite':
            return sqlite3.connect(db_conf.get('DB'))
        elif engine == 'mysql':
            return mysql.connector.connect(
                host=db_conf.get('HOST'),
                port=db_conf.get('PORT'),
                user=db_conf.get('USER'),
                password=db_conf.get('PWD'),
                database=db_conf.get('DB'),
            )


class DataBaseORM:
    connection = None
    cursor = None

    def __init__(self, config: dict, name: str):
        self.name = name
        connection_factory = DBConnectionFactory()
        self.connection = connection_factory.create_connection(config, name=self.name)
        self.engine = config.get(name).get('ENGINE')
        self.db_name = config.get(name).get('DB')
        self.cursor = self.connection.cursor()

    def create_table(self, model_cls):
        table_name = model_cls.table_name
        primary_key_field = None
        id_ = model_cls.id
        fields = [
            f"{id_.verbose_name}{id_.get_sql_type()}{id_.get_sql_default()}{id_.get_sql_index()}{id_.get_sql_null()}"]
        for name, field in model_cls.__dict__.items():
            if isinstance(field, Field):
                field_definition = f"{name}{field.get_sql_type()}{field.get_sql_default()}{field.get_sql_index()}{field.get_sql_null()}"
                if field.primary_key:
                    primary_key_field = name
                fields.append(field_definition)
        fields_str = ", ".join(fields)
        if primary_key_field:
            primary_key_definition = f"PRIMARY KEY ({primary_key_field})"
            fields_str += ", " + primary_key_definition
        sql = f"CREATE TABLE {table_name} ({fields_str})"
        self.cursor.execute(sql)
        self.connection.commit()

    def insert(self, table_name, values: dict):
        columns = ', '.join(values.keys())
        placeholders = ', '.join([f'?' for _ in range(len(values))])
        sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, tuple(values.values()))
        self.connection.commit()

    def all(self, model_cls):
        table_name = model_cls.table_name
        sql = f"SELECT * FROM {table_name}"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        results = []
        for row in rows:
            instance = model_cls()
            for i, column in enumerate(self.cursor.description):
                setattr(instance, column[0], row[i])
            results.append(instance)
        return results

    def filter(self, model_cls, **kwargs):
        table_name = model_cls.table_name
        conditions = " AND ".join(f"{field} = '{value}'" for field, value in kwargs.items())
        sql = f"SELECT * FROM {table_name} WHERE {conditions}"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        results = []
        for row in rows:
            instance = model_cls()
            for i, column in enumerate(self.cursor.description):
                setattr(instance, column[0], row[i])
            results.append(instance)
        return results

    def get(self, model_cls, **kwargs):
        table_name = model_cls.table_name
        conditions = " AND ".join(f"{field} = '{value}'" for field, value in kwargs.items())
        sql = f"SELECT * FROM {table_name} WHERE {conditions} LIMIT 1"
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        if row:
            instance = model_cls()
            for i, column in enumerate(self.cursor.description):
                setattr(instance, column[0], row[i])
            return instance
        return None

    def delete(self, model_cls, **kwargs):
        table_name = model_cls.table_name
        conditions = " AND ".join(f"{field} = '{value}'" for field, value in kwargs.items())
        sql = f"DELETE FROM {table_name} WHERE {conditions}"
        self.cursor.execute(sql)
        self.connection.commit()

    def sync_table(self, model_cls):
        table_name = model_cls.table_name
        existing_columns = self.get_existing_columns(table_name)
        model_columns = self.get_model_columns(model_cls)
        migration_occurred = False
        if not existing_columns:
            self.create_table(model_cls)
            return f'数据库 {self.db_name} 中的数据表 {table_name} 创建成功'

        columns_to_add = model_columns - existing_columns
        columns_to_remove = existing_columns - model_columns

        for column in columns_to_add:
            if column == 'id':
                continue
            self.add_column(table_name, column, model_cls.__dict__.get(str(column)))
            migration_occurred = True
            print(f'向{table_name}表中增加字段', column)

        for column in columns_to_remove:
            if column == 'id':
                continue
            self.remove_column(table_name, column)
            migration_occurred = True
            print(f'向{table_name}表中减少字段', column)
        if migration_occurred:
            return f'数据库 {self.db_name} 中的数据表 {table_name} 迁移成功'
        else:
            return f'数据库 {self.db_name} 中的数据表 {table_name} 无任何改变'

    def get_existing_columns(self, table_name):
        try:
            sql = ''
            if self.engine == 'sqlite':
                sql = f"PRAGMA table_info({table_name})"
            elif self.engine == 'mysql':
                sql = f"SHOW COLUMNS FROM {table_name}"
            self.cursor.execute(sql)
            if self.engine == 'sqlite':
                return set(row[1] for row in self.cursor.fetchall())
            elif self.engine == 'mysql':
                return set(row[0] for row in self.cursor.fetchall())
            return set()
        except Exception:
            return set()

    def get_model_columns(self, model_cls):
        columns = set()
        for name, field in model_cls.__dict__.items():
            if isinstance(field, Field):
                columns.add(name)
        return columns

    def add_column(self, table_name, column_name, field):
        sql = ''
        if self.engine == 'sqlite':
            sql = f"ALTER TABLE {table_name} ADD COLUMN " \
                  f"{column_name}{field.get_sql_type()}{field.get_sql_default()}{field.get_sql_index()}{field.get_sql_null()}"
        elif self.engine == 'mysql':
            sql = f"ALTER TABLE {table_name} ADD " \
                  f"{column_name}{field.get_sql_type()}{field.get_sql_default()}{field.get_sql_index()}{field.get_sql_null()}"
        self.cursor.execute(sql)
        self.connection.commit()

    def remove_column(self, table_name, column_name):
        sql = ''
        if self.engine == 'sqlite':
            sql = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
        elif self.engine == 'mysql':
            sql = f"ALTER TABLE {table_name} DROP {column_name}"
        self.cursor.execute(sql)
        self.connection.commit()
