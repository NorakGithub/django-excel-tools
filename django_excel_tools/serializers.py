#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict

from django_excel_tools import exceptions
from django_excel_tools.fields import (
    BooleanField, CharField, IntegerField, DateField,
    DateTimeField
)
from django_excel_tools.utils import error_trans

try:
    import django

    major, feature, minor, a, b = django.VERSION
    if major >= 2:
        from django.utils.translation import gettext as _
    else:
        from django.utils.translation import ugettext as _
except ImportError:
    raise exceptions.SerializerConfigError(
        'Django is required. Please make sure you have install via pip.'
    )


log = logging.getLogger(__name__)


class SerializerMeta:

    def __init__(self, meta):
        assert meta is not None, 'Meta cannot be None.'

        assert hasattr(meta, 'start_index'), 'Meta.start_index is required.'
        assert meta.start_index is not None, 'Must not be None.'
        assert type(meta.start_index) is int, 'Must be int.'
        self.start_index = meta.start_index

        assert hasattr(meta, 'fields'), 'Meta.fields is required.'
        assert meta.fields, 'Must not empty or None.'
        assert type(meta.fields) in [list, tuple], 'Must be iteratable type list or tuple.'
        self.fields = meta.fields

        if hasattr(meta, 'enable_transaction'):
            assert type(meta.enable_transaction) in [None, bool], 'Type must be bool.'
        self.enable_transaction = getattr(meta, 'enable_transaction', True)


class BaseSerializer(object):

    def __init__(self, worksheet, **kwargs):
        self.kwargs = kwargs
        self.meta = SerializerMeta(getattr(self, 'Meta', None))

        self.field_names = self.meta.fields
        self.start_index = self.meta.start_index
        self.class_fields = self._get_class_fields()
        self.fields = self._get_fields()

        self.operation_errors = []
        self.worksheet = worksheet
        self.validation_errors = self._validate_columns_less_than_fields()

        if not self.validation_errors:
            validation_errors, cleaned_data = self._proceed_serialize_excel_data()
            self.validation_errors = validation_errors
            self.cleaned_data = cleaned_data

        if self.validation_errors:
            self.invalid(self.validation_errors)
        else:
            self.validated()
            self._start_operation()

    def _get_class_fields(self):
        """
        Get all class field (variable) defined
        :return:
        """
        fields = [
            field for field in dir(self)
            if not (field.startswith("__") or field.startswith("_"))
            and not callable(getattr(self, field))
        ]
        assert fields, 'There is no fields added to class'
        return fields

    def _get_fields(self):
        """
        Assigning class object to dictionary
        :return:
        """
        fields = OrderedDict()
        for name in self.field_names:
            try:
                fields[name] = getattr(self, name)
            except AttributeError:
                message = '{} is not defined in class field'.format(name)
                raise exceptions.FieldNotExist(message=message)
        return fields

    def _validate_columns_less_than_fields(self):
        if self.worksheet.max_column < len(self.fields):
            data = {
                'required_num': len(self.fields),
                'excel_num': self.worksheet.max_column
            }
            return [_('This import required %(required_num)s columns but excel'
                      ' only has %(excel_num)s columns.') % data]
        return []

    def _proceed_serialize_excel_data(self):
        max_column = len(self.fields)
        validation_errors = []
        cleaned_data = []
        for row_index, row in enumerate(self.worksheet):
            # Ignore row that not yet start data gathering
            if row_index < self.start_index:
                continue
            if self._is_last_row(row, max_column):
                break
            cleaned_row = {}

            for col_index, cell in enumerate(row):
                if col_index >= max_column:
                    continue
                key = self.field_names[col_index]
                field_object = self.fields[key]
                field_object.value = cell.value
                try:
                    field_object.validate(index=row_index + 1)
                    extra_clean_value = self._extra_clean_validate(key)
                    if extra_clean_value is not None:
                        field_object.cleaned_value = extra_clean_value
                except exceptions.ValidationError as error:
                    validation_errors.append(error.message)
                    field_object.reset()
                    continue

                cleaned_row[key] = field_object.cleaned_value
                field_object.reset()

            if validation_errors:
                continue

            try:
                self.row_extra_validation(row_index, cleaned_row)
            except exceptions.ValidationError as error:
                message = error_trans(
                    index=row_index + 1,
                    verbose_name='',
                    message=error.message
                )
                validation_errors.append(message)
                continue

            cleaned_data.append(cleaned_row)

        return validation_errors, cleaned_data

    def _is_last_row(self, row, max_column):
        none_cell = []
        for index, cell in enumerate(row):
            if index + 1 > max_column:
                break
            if cell.value is None:
                none_cell.append(cell)
                continue
            if isinstance(cell.value, str) and not cell.value.strip():
                none_cell.append(cell)
                continue
            if not cell.value:
                none_cell.append(cell)
        return len(none_cell) >= max_column

    def _extra_clean_validate(self, key):
        try:
            extra_clean = 'extra_clean_{}'.format(key)
            extra_clean_def = getattr(self, extra_clean)
        except AttributeError:
            return

        if not callable(extra_clean_def):
            return

        validated_field = self.fields[key]
        cleaned_value = validated_field.cleaned_value
        return extra_clean_def(cleaned_value)

    def _start_operation(self):
        if self.meta.enable_transaction:
            try:
                self.import_operation(self.cleaned_data)
                self.operation_success()
            except exceptions.ImportOperationFailed:
                self.operation_failed(self.operation_errors)
            return

        try:
            from django.db import transaction
        except ImportError:
            message = 'Django is required, please make sure you installed ' \
                      'Django via pip.'
            raise exceptions.SerializerConfigError(message=message)

        try:
            with transaction.atomic():
                self.import_operation(self.cleaned_data)
            self.operation_success()
        except exceptions.ImportOperationFailed:
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
        return _('[Row %(index)s] %(error)s') % {'index': sheet_index, 'error': error}
