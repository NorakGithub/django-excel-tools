from collections import OrderedDict

import datetime

from .exceptions import ValidationError, ColumnNotEqualError, FieldNotExist
from .fields import BaseField, BASE_MESSAGE, DigitBaseField, BaseDateTimeField


class BaseSerializer(object):

    def __init__(self, worksheet):
        self._class_meta_validation()

        self.class_fields = [field for field in dir(self)
                             if not (field.startswith("__") or field.startswith("_"))
                             and not callable(getattr(self, field))]
        assert self.class_fields, 'There no fields added to class.'

        self.errors = []
        self.cleaned_data = []
        self.fields = OrderedDict()
        self.worksheet = worksheet

        self._set_fields()
        self._validate_column()

        if not self.errors:
            self._set_values()

    def _class_meta_validation(self):
        assert hasattr(self, 'Meta'), 'class Meta is required'

        assert hasattr(self.Meta, 'start_index'), 'Meta.start_index in class Meta is required.'
        assert type(self.Meta.start_index) is int, 'Meta.start_index type is int.'

        assert hasattr(self.Meta, 'fields'), 'Meta.fields in class Meta is required'
        fields_is_list_or_tuple = type(self.Meta.fields) is list or type(self.Meta.fields) is tuple
        assert fields_is_list_or_tuple, 'Meta.fields type must be list or tuple'

        self.field_names = self.Meta.fields
        self.start_index = self.Meta.start_index

    def _set_fields(self):
        for field_name in self.field_names:
            try:
                self.fields[field_name] = getattr(self, field_name)
            except AttributeError:
                raise FieldNotExist(message='{} is not defined in class field.'.format(field_name))

    def _validate_column(self):
        if self.worksheet.max_column != len(self.fields):
            raise ColumnNotEqualError(message='{} has {} fields while sheet has {}, field should be the same.'.format(
                self.__class__.__name__,
                len(self.fields),
                self.worksheet.max_column,
            ))

    def _set_values(self):
        for row_index, row in enumerate(self.worksheet.rows):
            if row_index < self.start_index:
                continue

            for index, cell in enumerate(row):
                key = self.field_names[index]
                self.fields[key].value = cell.value
                try:
                    self.fields[key].validate(index=row_index + 1)
                except ValidationError as error:
                    self.errors.append(error.message)

            self._set_cleaned_values(self.fields)

    def _set_cleaned_values(self, validated_fields):
        cleaned_row = {}
        for key in validated_fields:
            cleaned_row[key] = validated_fields[key].cleaned_value
        self.cleaned_data.append(cleaned_row)


class ExcelSerializer(BaseSerializer):

    def is_valid(self):
        if self.errors:
            self.invalided(self.errors)
        self.validated(self.cleaned_data)

        return False if self.errors else True

    def validated(self, cleaned_data):
        pass

    def invalided(self, errors):
        pass


class CharField(BaseField):

    def __init__(self, max_length, verbose_name, convert_number=False, allow_blank=False):
        super(CharField, self).__init__(verbose_name, allow_blank)
        self.max_length = max_length
        self.convert_number = convert_number

    def data_type_validate(self, index):
        super(CharField, self).data_type_validate(index)

        value = self.value
        if self.convert_number:
            value = str(value)

        if type(value) is not str and type(value) is not unicode:
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message='must be text.'
            ))

        if len(value) > self.max_length:
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message='cannot be more than {} characters.'.format(self.max_length)
            ))

        self.cleaned_value = value


class IntegerField(DigitBaseField):

    def data_type_validate(self, index):
        super(IntegerField, self).data_type_validate(index)

        value = self.value
        if self.convert_str:
            try:
                value = int(value)
            except ValueError:
                raise ValidationError(message=BASE_MESSAGE.format(
                    index=index,
                    verbose_name=self.verbose_name,
                    message='cannot convert {} to number.'.format(value)
                ))

        self._data_type_validation_helper(
            index=index,
            value=value,
            data_type=int,
            error_message='expected type is number but received {}.'.format(type(value).__name__)
        )

        self.cleaned_value = value


class DateField(BaseDateTimeField):

    def data_type_validate(self, index):
        super(DateField, self).data_type_validate(index)

        value = self.value
        if type(value) is str or type(value) is unicode:
            try:
                date = datetime.datetime.strptime(value, self.date_format).date()
                value = date
            except ValueError:
                raise ValidationError(message=BASE_MESSAGE.format(
                    index=index,
                    verbose_name=self.verbose_name,
                    message='"{}" is incorrect format, it should be "{}".'.format(value, self.date_format_verbose)
                ))
        elif type(value) is datetime.datetime:
            value = value.date()

        self._data_type_validation_helper(
            index=index,
            value=value,
            data_type=datetime.date,
            error_message='expected type is date but received {}.'.format(type(value).__name__)
        )

        self.cleaned_value = value


class DateTimeField(BaseDateTimeField):

    def data_type_validate(self, index):
        super(DateTimeField, self).data_type_validate(index)

        value = self.value
        if type(value) is str or type(value) is unicode:
            try:
                time = datetime.datetime.strptime(value, self.date_format)
                value = time
            except ValueError:
                raise ValidationError(message=BASE_MESSAGE.format(
                    index=index,
                    verbose_name=self.verbose_name,
                    message='"{}" is incorrect format, it should be "{}"'.format(value, self.date_format_verbose)
                ))

        self._data_type_validation_helper(
            index=index,
            value=value,
            data_type=datetime.datetime,
            error_message='expected type is datetime but received {}.'.format(type(value).__name__)
        )

        self.cleaned_value = value
