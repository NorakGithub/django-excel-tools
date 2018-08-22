#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

import datetime

from .exceptions import ValidationError, SerializerConfigError

BASE_MESSAGE = u'[Row {index}] {verbose_name} {message}'


class BaseField(object):

    def __init__(self, verbose_name, blank=False, default=None):
        self.verbose_name = verbose_name
        self.blank = blank
        self.default = default
        self.value = None
        self.cleaned_value = None

    def reset(self):
        self.value = None
        self.cleaned_value = None

    def validate(self, index):
        validating_value = self.strip_value_space()
        validating_value = self.validate_blank(validating_value, index)
        if validating_value in ['', None]:
            self.cleaned_value = validating_value
        else:
            validating_value = self.validate_specific_data_type(validating_value, index)
            self.cleaned_value = validating_value

    def validate_blank(self, validating_value, index):
        blank_values = ['', None]
        if not self.blank and validating_value in blank_values:
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message='is not allow to be blank.'
            ))

        if self.blank and validating_value in blank_values and self.default is not None:
            return self.default

        return validating_value

    def strip_value_space(self):
        str_types = [str]
        if sys.version_info < (3, 0):
            str_types.append(unicode)
        if type(self.value) in str_types:
            return self.value.strip()
        return self.value

    def validate_specific_data_type(self, validating_value, index):
        pass

    def validate_default(self, validating_value):
        if self.default is not None and validating_value is None:
            return self.default
        return validating_value

    def data_type_validate(self, index):
        if type(self.value) is str:
            self.value = self.value.strip()

    def _data_type_validation_helper(self, index, value, data_type, error_message):
        if type(value) is not data_type and not self.blank:
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message=error_message
            ))

    def _choice_validation_helper(self, index, value, choices, case_sensitive=True):
        # Check if choices has duplication
        if len(choices) != len(set(choices)):
            raise SerializerConfigError(message='Choice has duplication.')

        if not case_sensitive:
            value = value.lower()
            choices = [choice.lower() for choice in choices]

        if value not in choices:
            choices = u', '.join(choices)
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message=u'{} is not correct, it must has one of these {}.'.format(value, choices)
            ))

    def __repr__(self):
        return '<{}- {}>'.format(self.__class__.__name__, str(self))

    def __str__(self):
        return self.value


class DigitBaseField(BaseField):

    def __init__(self, verbose_name, default=None, convert_str=True, blank=False, choices=None):
        super(DigitBaseField, self).__init__(verbose_name, blank)
        self.convert_str = convert_str
        self.default = default
        self.choices = choices


class BaseDateTimeField(BaseField):

    def __init__(self, date_format, date_format_verbose, verbose_name, blank=False):
        super(BaseDateTimeField, self).__init__(verbose_name, blank)
        self.date_format = date_format
        self.date_format_verbose = date_format_verbose

    def convert_datetime(self, validating_value, index):
        if self.blank and validating_value in ['', None]:
            return None

        try:
            return datetime.datetime.strptime(validating_value, self.date_format)
        except ValueError:
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message='"{}" is incorrect format, it should be "{}".'.format(validating_value, self.date_format)
            ))

    @staticmethod
    def convert_int_to_str(validating_value):
        if type(validating_value) is int:
            str_type = str if sys.version_info >= (3, 0) else unicode
            return str_type(validating_value)
        return validating_value
