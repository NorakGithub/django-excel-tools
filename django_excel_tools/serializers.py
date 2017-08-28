#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict

import datetime

import sys

from .exceptions import ValidationError, ColumnNotEqualError, FieldNotExist
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
            cleaned_value = validated_fields[key].cleaned_value
            try:
                extra_clean = 'extra_clean_{}'.format(key)
                extra_clean_def = getattr(self, extra_clean)
                if callable(extra_clean_def):
                    cleaned_value = extra_clean_def(cleaned_value)
            except AttributeError:
                pass
            cleaned_row[key] = cleaned_value
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

    def __init__(self, max_length, verbose_name, convert_number=True, blank=False, choices=None):
        super(CharField, self).__init__(verbose_name, blank)
        self.max_length = max_length
        self.convert_number = convert_number
        self.choices = choices

    def data_type_validate(self, index):
        super(CharField, self).data_type_validate(index)

        value = self.value
        if self.convert_number:
            if sys.version_info >= (3, 0):
                value = str(value).strip()
            else:
                value = unicode(value).strip()

        type_error_message = BASE_MESSAGE.format(
            index=index,
            verbose_name=self.verbose_name,
            message='must be text.'
        )

        if sys.version_info >= (3, 0):
            if type(value) is not str:
                raise ValidationError(message=type_error_message)
        else:
            if type(value) is not str and type(value) is not unicode:
                raise ValidationError(message=type_error_message)

        if len(value) > self.max_length:
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message='cannot be more than {} characters.'.format(self.max_length)
            ))

        if self.choices:
            self._choice_validation_helper(index, value, self.choices)

        self.cleaned_value = value


class IntegerField(DigitBaseField):

    def data_type_validate(self, index):
        super(IntegerField, self).data_type_validate(index)

        value = self.value
        if self.convert_str and type(value) is not int:
            try:
                value = int(value)
            except ValueError:
                raise ValidationError(message=BASE_MESSAGE.format(
                    index=index,
                    verbose_name=self.verbose_name,
                    message='cannot convert {} to number.'.format(value)
                ))

        elif self.default:
            value = self.default

        self._data_type_validation_helper(
            index=index,
            value=value,
            data_type=int,
            error_message='expected type is number but received {}.'.format(type(value).__name__)
        )

        if self.choices:
            self._choice_validation_helper(index, value, self.choices)

        self.cleaned_value = value


class DateField(BaseDateTimeField):

    def data_type_validate(self, index):
        super(DateField, self).data_type_validate(index)

        value = self.value
        type_error_message = BASE_MESSAGE.format(
                    index=index,
                    verbose_name=self.verbose_name,
                    message='"{}" is incorrect format, it should be "{}".'.format(value, self.date_format_verbose)
                )

        def convert_date():
            try:
                return datetime.datetime.strptime(value, self.date_format).date()
            except ValueError:
                raise ValidationError(message=type_error_message)

        if sys.version_info >= (3, 0):
            if type(value) is str:
                value = convert_date()
        else:
            if type(value) is str or type(value) is unicode:
                value = convert_date()

        if type(value) is datetime.datetime:
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
        type_error_message = BASE_MESSAGE.format(
                        index=index,
                        verbose_name=self.verbose_name,
                        message='"{}" is incorrect format, it should be "{}"'.format(value, self.date_format_verbose)
                    )

        def convert_date_time():
            try:
                return datetime.datetime.strptime(value, self.date_format)
            except ValueError:
                raise ValidationError(message=type_error_message)

        if sys.version_info >= (3, 0):
            if type(value) is str:
                value = convert_date_time()
        else:
            if type(value) is str or type(value) is unicode:
                value = convert_date_time()

        self._data_type_validation_helper(
            index=index,
            value=value,
            data_type=datetime.datetime,
            error_message='expected type is datetime but received {}.'.format(type(value).__name__)
        )

        self.cleaned_value = value
