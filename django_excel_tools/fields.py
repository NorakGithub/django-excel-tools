#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .exceptions import ValidationError


BASE_MESSAGE = '[Row {index}] {verbose_name} {message}'


class BaseField(object):

    def __init__(self, verbose_name, blank=False):
        self.verbose_name = verbose_name
        self.blank = blank
        self.value = None
        self.cleaned_value = None

    def validate(self, index):
        if not self.blank and not self.value:
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message='is not allow to be blank.')
            )

        self.data_type_validate(index)

    def data_type_validate(self, index):
        if type(self.value) is str:
            self.value = self.value.strip()

    def _data_type_validation_helper(self, index, value, data_type, error_message):
        if type(value) is not data_type:
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message=error_message
            ))

    def __repr__(self):
        return '<{}- {}>'.format(self.__class__.__name__, str(self))

    def __str__(self):
        return self.value


class DigitBaseField(BaseField):

    def __init__(self, verbose_name, default, convert_str=True, blank=False):
        super(DigitBaseField, self).__init__(verbose_name, blank)
        self.convert_str = convert_str
        self.default = default


class BaseDateTimeField(BaseField):

    def __init__(self, date_format, date_format_verbose, verbose_name, blank=False):
        super(BaseDateTimeField, self).__init__(verbose_name, blank)
        self.date_format = date_format
        self.date_format_verbose = date_format_verbose
