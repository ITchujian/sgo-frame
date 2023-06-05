class ModelFieldError(Exception):
    def __init__(self, field_name, message):
        self.field_name = field_name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ModelOverrideFieldError(ModelFieldError):
    def __init__(self, field_name):
        self.message = f'Cannot override reserved field: {field_name}'
        super().__init__(field_name, self.message)


if __name__ == '__main__':
    print(ModelOverrideFieldError('id'))
