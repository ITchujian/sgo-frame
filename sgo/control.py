import importlib
import os
import inspect
from importlib import import_module
from .models import Field, Model
from .db import DataBaseORM
from .utils import *


class Control:
    def __init__(self):
        self.settings = import_module(os.environ.get('SGO_PROJECT_SETTINGS'))
        self.models = import_module(self.settings.MODELS)
        self.has_model_exception = False
        self.db = None

    def run(self):
        pass

    def shell(self):
        while True:
            try:
                ColorPrint.print(f"{self.settings.PROJECT_NAME}", "green", end='')
                command = input(f":~$：")
                if command == "exit":
                    break
                elif command == "checkmodel":
                    self.reload()
                    self.check_model_fields()
                elif command == "checkmodel no-reload" or command == "checkmodel no-update":
                    self.check_model_fields()
                elif command == "migrate":
                    self.migrate_database(self.settings.DATABASE_USE)
                elif command == 'update' or command == 'reload':
                    self.reload()
                elif command == 'exit' or command == 'quit':
                    break
                else:
                    ColorPrint.print("未知命令，请重新输入", 'red')
            except KeyboardInterrupt:
                ColorPrint.print('Stop!!', 'red')
                break
            except EOFError:
                ColorPrint.print('Stop!!', 'red')
                break
            except Exception as e:
                ColorPrint.print(e, color='red')

    def migrate_database(self, name):
        self.db = DataBaseORM(self.settings.DATABASE, name=name)
        models = self.get_all_models()
        for model in models:
            try:
                ColorPrint.print(self.db.sync_table(model), color='blue')
            except Exception as e:
                ColorPrint.print(e, color='red')

    def migrate_database_extend(self, command: str):
        commands = command.replace(' ', '').split('|', 1)
        if commands[0] == 'migrate' and len(commands) == 2:
            if commands[1] in self.settings.DATABASE:
                self.migrate_database(name=commands[1])

    def get_all_models(self):
        return [cls for cls in self.models.__dict__.values() if
                isinstance(cls, type) and issubclass(cls, Model) and cls != Model]

    def check_model_fields(self):
        self.has_model_exception = False
        model_classes = self.get_all_models()
        for model_class in model_classes:
            unexpected_fields = []
            none_fields = []
            for field_name, field_value in model_class.__dict__.items():
                if field_name.startswith('__') or field_name == 'Meta' or field_name == 'table_name':
                    continue
                if field_value is None:
                    none_fields.append(field_name)
                elif not isinstance(field_value, Field):
                    unexpected_fields.append(field_name)
            if unexpected_fields or none_fields:
                self.has_model_exception = True
                if unexpected_fields:
                    ColorPrint.print(f"在 {model_class.__name__} 类中出现了意外的字段：", end='')
                    ColorPrint.print('、'.join(unexpected_fields), 'red')
                if none_fields:
                    ColorPrint.print(f"在 {model_class.__name__} 类中出现了空值字段：", end='')
                    ColorPrint.print('、'.join(none_fields), 'red')

        if not self.has_model_exception:
            self.has_model_exception = False
            ColorPrint.print('你所定制的模型非常健康！', 'blue')

    def reload(self):
        importlib.reload(self.settings)
        importlib.reload(self.models)
