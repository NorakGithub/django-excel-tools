#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime

from .exceptions import ValidationError, SerializerConfigError

try:
    from django.utils.translation import ugettext as _
except ImportError:
    raise SerializerConfigError('Django is required. Please make sure you '
                                'have install via pip.')

BASE_MESSAGE = _('[Row %(index)s] %(verbose_name)s %(message)s')


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
            msg = BASE_MESSAGE % {
                "index": index,
                "verbose_name": self.verbose_name,
                "message": _('is not allow to be blank.')
            }
            raise ValidationError(message=msg)

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
            msg = _('%(value)s is not correct, it must has one of these %(choices)s.')
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message=msg % {'value': value, 'choices': choices}
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
            data = {'value': validating_value, 'verbose': self.date_format_verbose}
            message = _('"%(value)s" is incorrect format, it should be "%(date_format_verbose)s".')
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message=message % data
            ))

    @staticmethod
    def convert_int_to_str(validating_value):
        if type(validating_value) is int:
            str_type = str if sys.version_info >= (3, 0) else unicode
            return str_type(validating_value)
        return validating_value


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
            message=_('must be text.')
        )

        str_types = [str]
        if sys.version_info <= (3, 0):
            str_types.append(unicode)

        if type(validating_value) not in str_types:
            raise ValidationError(message=type_error_message)

        if len(validating_value) > self.max_length:
            msg = 'cannot be more than %(length)s character.'
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message=msg % {'length': self.max_length}
            ))

        if self.choices:
            self._choice_validation_helper(index, validating_value, self.choices, self.case_sensitive)

        return validating_value


class IntegerField(DigitBaseField):

    def validate_specific_data_type(self, validating_value, index):
        try:
            validating_value = int(validating_value)
        except ValueError:
            msg = _('cannot convert %(value)s to number.') % {'value': validating_value}
            raise ValidationError(message=BASE_MESSAGE.format(
                index=index,
                verbose_name=self.verbose_name,
                message=msg
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
