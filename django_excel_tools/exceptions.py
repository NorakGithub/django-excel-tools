class BaseExcelError(Exception):

    def __init__(self, message):
        super(BaseExcelError, self).__init__()
        self.message = message


class ColumnNotEqualError(BaseExcelError):
    pass


class FieldNotExist(BaseExcelError):
    pass


class ImportOperationFailed(Exception):
    pass


class SerializerConfigError(BaseExcelError):
    pass


class ValidationError(BaseExcelError):
    pass
