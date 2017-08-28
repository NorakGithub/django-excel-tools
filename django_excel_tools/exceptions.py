class BaseExcelError(Exception):

    def __init__(self, message):
        super(BaseExcelError, self).__init__()
        self.message = message


class ValidationError(BaseExcelError):
    pass


class ColumnNotEqualError(BaseExcelError):
    pass


class FieldNotExist(BaseExcelError):
    pass


class SerializerConfigError(BaseExcelError):
    pass
