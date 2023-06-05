import os
from importlib import import_module




class Field:
    def __init__(self, verbose_name, indexed=False, primary_key=False, unique=False, null=False):
        self.verbose_name = verbose_name
        self.indexed = indexed
        self.primary_key = primary_key
        self.unique = unique
        self.null = null

    def get_sql_type(self):
        raise NotImplementedError()

    def get_sql_index(self):
        if self.primary_key:
            return " PRIMARY KEY"
        elif self.unique:
            return " UNIQUE"
        elif self.indexed:
            return " INDEX"
        else:
            return ""

    def get_sql_default(self):
        return ""

    def get_sql_null(self):
        if self.null:
            return " NULL"
        else:
            return " NOT NULL"


class CharField(Field):
    def __init__(self, verbose_name, max_length, indexed=False, primary_key=False, unique=False, null=False):
        super().__init__(verbose_name, indexed, primary_key, unique, null=null)
        self.max_length = max_length

    def get_sql_type(self):
        return f" VARCHAR({self.max_length})"

    def get_sql_default(self):
        return ""


class DateTimeField(Field):
    def __init__(self, verbose_name, auto_now_add=False, auto_now=False, null=False):
        super().__init__(verbose_name, null=null)
        self.auto_now_add = auto_now_add
        self.auto_now = auto_now

    def get_sql_type(self):
        return " DATETIME"

    def get_sql_default(self):
        if self.auto_now_add:
            return " DEFAULT CURRENT_TIMESTAMP"
        elif self.auto_now:
            return " DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        else:
            return ""


class IntegerField(Field):
    def __init__(self, verbose_name, default=None, indexed=False, primary_key=False, auto_increment=False,
                 null=False):
        super().__init__(verbose_name, indexed, primary_key, null=null)
        self.default = default
        self.auto_increment = auto_increment

    def get_sql_type(self):
        sql_type = " INT"
        if self.auto_increment:
            sql_type += " AUTO_INCREMENT"
        return sql_type

    def get_sql_default(self):
        if self.default:
            return f" DEFAULT {self.default}"
        return ""


class BooleanField(Field):
    def __init__(self, verbose_name, default=None, null=False):
        super().__init__(verbose_name, null=null)
        self.default = default

    def get_sql_type(self):
        return " BOOLEAN"

    def get_sql_default(self):
        if self.default is True:
            return " DEFAULT TRUE"
        elif self.default is False:
            return " DEFAULT FALSE"
        return ""


class DateField(Field):
    def __init__(self, verbose_name, default=None, null=False):
        super().__init__(verbose_name, null=null)
        self.default = default

    def get_sql_type(self):
        return " DATE"

    def get_sql_default(self):
        if self.default is not None:
            return f" DEFAULT '{self.default}'"
        return ""


class DecimalField(Field):
    def __init__(self, verbose_name, precision=None, scale=None, default=None, null=False):
        super().__init__(verbose_name, null=null)
        self.precision = precision
        self.scale = scale
        self.default = default

    def get_sql_type(self):
        return f" DECIMAL({self.precision},{self.scale})"

    def get_sql_default(self):
        if self.default is not None:
            return f" DEFAULT {self.default}"
        return ""


class TextField(Field):
    def __init__(self, verbose_name, null=False):
        super().__init__(verbose_name, null=null)

    def get_sql_type(self):
        return " TEXT"

    def get_sql_default(self):
        return ""


class QuerySet:
    def __init__(self, model_cls):
        self.model_cls = model_cls

    def all(self):
        return self.model_cls.get_all()

    def filter(self, **kwargs):
        return self.model_cls.filter(**kwargs)

    def get(self, **kwargs):
        return self.model_cls.get(**kwargs)

    def delete(self, **kwargs):
        return self.model_cls.delete(**kwargs)

from .db import DataBaseORM

SETTINGS = import_module(os.environ.get('SGO_PROJECT_SETTINGS'))


class ModelMeta(type):

    def __init__(cls, name: str, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.table_name = name.lower()
        cls.objects = QuerySet(cls)
        if hasattr(cls, 'Meta'):
            meta_class = cls.Meta
            if hasattr(meta_class, 'table_name'):
                if meta_class.table_name:
                    cls.table_name = meta_class.table_name

    @classmethod
    def all(cls):
        db_orm = DataBaseORM(SETTINGS.DATABASE, SETTINGS.DATABASE_USE)
        return db_orm.all(cls)

    @classmethod
    def filter(cls, **kwargs):
        db_orm = DataBaseORM(SETTINGS.DATABASE, SETTINGS.DATABASE_USE)
        return db_orm.filter(cls, **kwargs)

    @classmethod
    def get(cls, **kwargs):
        db_orm = DataBaseORM(SETTINGS.DATABASE, SETTINGS.DATABASE_USE)
        return db_orm.get(cls, **kwargs)

    @classmethod
    def delete(cls, **kwargs):
        db_orm = DataBaseORM(SETTINGS.DATABASE, SETTINGS.DATABASE_USE)
        return db_orm.delete(cls, **kwargs)


class Model(metaclass=ModelMeta):
    table_name = None
    id = IntegerField("id", primary_key=True, auto_increment=True)

    class Meta:
        table_name = None
