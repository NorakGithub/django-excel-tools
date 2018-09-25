#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict

import datetime

import sys

from .exceptions import ValidationError, ColumnNotEqualError, FieldNotExist, ImportOperationFailed, \
    SerializerConfigError
from .fields import BaseField, BASE_MESSAGE, DigitBaseField, BaseDateTimeField


class BaseSerializer(object):

    def __init__(self, worksheet, **kwargs):
        self.kwargs = kwargs
        self._class_meta_validation()

        self.class_fields = [field for field in dir(self)
                             if not (field.startswith("__") or field.startswith("_"))
                             and not callable(getattr(self, field))]
        assert self.class_fields, 'There no fields added to class.'

        self.errors = []
        self.operation_errors = []
        self.cleaned_data = []
        self.fields = OrderedDict()
        self.worksheet = worksheet

        self._set_fields()

        try:
            self._validate_column()
        except ColumnNotEqualError as e:
            self.errors.append(e.message)
            self.invalid([e.message])
            return

        self._set_values()
        if not self.errors:
            self.validated()
            self._start_operation()
        else:
            self.invalid(self.errors)

    def _class_meta_validation(self):
        assert hasattr(self, 'Meta'), 'class Meta is required'

        assert hasattr(self.Meta, 'start_index'), 'Meta.start_index in class Meta is required.'
        assert type(self.Meta.start_index) is int, 'Meta.start_index type is int.'

        assert hasattr(self.Meta, 'fields'), 'Meta.fields in class Meta is required.'
        fields_is_list_or_tuple = type(self.Meta.fields) is list or type(self.Meta.fields) is tuple
        assert fields_is_list_or_tuple, 'Meta.fields type must be either list or tuple.'

        if hasattr(self.Meta, 'enable_django_transaction'):
            assert type(self.Meta.enable_django_transaction) is bool, 'Meta.enable_django_transaction is bool type.'
            self.enable_django_transaction = self.Meta.enable_django_transaction
        else:
            self.enable_django_transaction = True

        self.field_names = self.Meta.fields
        self.start_index = self.Meta.start_index

    def _set_fields(self):
        for field_name in self.field_names:
            try:
                self.fields[field_name] = getattr(self, field_name)
            except AttributeError:
                raise FieldNotExist(message='{} is not defined in class field.'.format(field_name))

    def _get_max_column(self):
        max_column = 0
        row = 1
        for col in self.worksheet[row]:
            if col.value == '':
                continue
            max_column += 1

        return max_column

    def _get_max_row(self):
        max_row = 0
        for row in self.worksheet.rows:
            values = [cell.value for cell in row]
            if all(value == '' or value is None for value in values):
                break
            max_row += 1
        return max_row

    def _validate_column(self):
        max_column = self._get_max_column()
        if max_column != len(self.fields):
            message = ('Required {} fields, but given excel has {} fields, '
                       'amount of field should be the same. [Tip] You might '
                       'select the wrong excel format.'
                       ''.format(len(self.fields), max_column))
            raise ColumnNotEqualError(message=message)

    def _set_values(self):
        max_row = self._get_max_row()
        max_colum = self._get_max_column()
        for row_index, row in enumerate(self.worksheet.iter_rows(max_row=max_row)):
            if row_index < self.start_index:
                continue

            for index, cell in enumerate(row):
                if index+1 > max_colum:
                    break
                key = self.field_names[index]
                self.fields[key].value = cell.value
                try:
                    self.fields[key].validate(index=row_index + 1)
                    self.extra_clean_validate(key)
                except ValidationError as error:
                    message = BASE_MESSAGE.format(
                        index=row_index + 1,
                        verbose_name=self.fields[key].verbose_name,
                        message=error.message
                    )
                    self.errors.append(message)
            cleaned_row = self._set_cleaned_values(self.fields)
            try:
                self.row_extra_validation(row_index + 1, cleaned_row)
            except ValidationError as error:
                self.errors.append(error.message)

            self._reset_fields_value()

    def extra_clean_validate(self, key):
        try:
            extra_clean = 'extra_clean_{}'.format(key)
            extra_clean_def = getattr(self, extra_clean)
            if callable(extra_clean_def):
                validated_field = self.fields[key]
                cleaned_value = validated_field.cleaned_value
                self.fields[key].cleaned_value = extra_clean_def(cleaned_value)
        except AttributeError:
            pass

    def _reset_fields_value(self):
        for key in self.field_names:
            self.fields[key].reset()

    def _set_cleaned_values(self, validated_fields):
        cleaned_row = {}
        for key in validated_fields:
            cleaned_value = validated_fields[key].cleaned_value
            cleaned_row[key] = cleaned_value
        self.cleaned_data.append(cleaned_row)
        return cleaned_row

    def _start_operation(self):
        if self.enable_django_transaction:
            try:
                self.import_operation(self.cleaned_data)
                self.operation_success()
            except ImportOperationFailed:
                self.operation_failed(self.operation_errors)
            return

        try:
            from django.db import transaction
        except ImportError:
            raise SerializerConfigError(message='Django is required, please make sure you installed Django via pip.')

        try:
            with transaction.atomic():
                self.import_operation(self.cleaned_data)
            self.operation_success()
        except ImportOperationFailed:
            self.operation_failed(self.operation_errors)

    def import_operation(self, cleaned_data):
        pass

    def validated(self):
        pass

    def invalid(self, errors):
        pass

    def operation_failed(self, errors):
        pass

    def operation_success(self):
        pass

    def row_extra_validation(self, index, cleaned_row):
        pass


class ExcelSerializer(BaseSerializer):

    def gen_error(self, index, error):
        # + 1 to make it equal to sheet index
        sheet_index = self.start_index + index + 1
        return '[Row {sheet_index}] {error}'.format(sheet_index=sheet_index, error=error)


class BooleanField(BaseField):

    def __init__(self, verbose_name):
        super(BooleanField, self).__init__(verbose_name=verbose_name, blank=True, default=False)

    def validate_specific_data_type(self, validating_value, index):
        return True if validating_value else False


class CharField(BaseField):

    def __init__(self, max_length, verbose_name, convert_number=True, blank=False, choices=None, default=None, case_sensitive=True):
        super(CharField, self).__init__(verbose_name, blank, default)
        self.max_length = max_length
        self.convert_number = convert_number
        self.choices = choices
        self.case_sensitive = case_sensitive

    def validate_specific_data_type(self, validating_value, index):
        str_type = str if sys.version_info >= (3, 0) else unicode
        if self.convert_number:
            validating_value = str_type(validating_value)

        type_error_message = BASE_MESSAGE.format(
            index=index,
            verbose_name=self.verbose_name,
            message='must be text.'
        )

        str_types = [str]
        if sys.version_info <= (3, 0):
            str_types.append(unicode)

        if type(validating_value) not in str_types:
            raise ValidationError(message=type_error_message)

        if len(validating_value) > self.max_length:
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message='cannot be more than {} characters'.format(self.max_length)
            ))

        if self.choices:
            self._choice_validation_helper(index, validating_value, self.choices, self.case_sensitive)

        return validating_value


class IntegerField(DigitBaseField):

    def validate_specific_data_type(self, validating_value, index):
        try:
            validating_value = int(validating_value)
        except ValueError:
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message='cannot convert {} to number.'.format(validating_value)
            ))

        if self.choices:
            self._choice_validation_helper(index, validating_value, self.choices)

        return validating_value


class DateField(BaseDateTimeField):

    def validate_specific_data_type(self, validating_value, index):
        validating_value = self.convert_int_to_str(validating_value)
        if type(validating_value) is datetime.datetime:
            return validating_value.date()

        validating_value = self.convert_datetime(validating_value, index)
        return validating_value.date() if validating_value is not None else validating_value


class DateTimeField(BaseDateTimeField):

    def validate_specific_data_type(self, validating_value, index):
        validating_value = self.convert_int_to_str(validating_value)
        if type(validating_value) is datetime.datetime:
            return validating_value

        validating_value = self.convert_datetime(validating_value, index)
        return validating_value if validating_value is not None else validating_value
