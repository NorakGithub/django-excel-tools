#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict

from django_excel_tools import exceptions
from django_excel_tools.fields import (
    BASE_MESSAGE, BooleanField, CharField, IntegerField, DateField,
    DateTimeField
)


log = logging.getLogger(__name__)


class SerializerMeta:

    def __init__(self, meta):
        assert meta is not None, 'Meta cannot be None.'

        assert hasattr(meta, 'start_index'), 'Meta.start_index is required.'
        assert meta.start_index, 'Value cannot be int positive.'
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

        validation_errors, cleaned_data = self._proceed_serialize_excel_data()
        self.validation_errors = validation_errors
        self.cleaned_data = cleaned_data
        if validation_errors:
            self.invalid(validation_errors)
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
                    message = BASE_MESSAGE.format(
                        index=row_index + 1,
                        verbose_name=self.fields[key].verbose_name,
                        message=error.message,
                    )
                    validation_errors.append(message)
                    field_object.reset()
                    continue

                cleaned_row[key] = field_object.cleaned_value
                field_object.reset()

            if validation_errors:
                continue

            try:
                self.row_extra_validation(row_index, cleaned_row)
            except exceptions.ValidationError as error:
                message = BASE_MESSAGE.format(
                    index=row_index + 1,
                    verbose_name='',
                    error=error.message,
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
            if cell.value in [None, u'', '']:
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
        return '[Row {sheet_index}] {error}'.format(
            sheet_index=sheet_index,
            error=error
        )
