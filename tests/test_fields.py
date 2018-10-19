from datetime import datetime
import unittest

from django_excel_tools import fields


class BooleanFieldTest(unittest.TestCase):
    def setUp(self):
        self.field = fields.BooleanField(verbose_name='Test')

    def test_empty_data_should_become_false(self):
        self.field.validate(index=0)
        self.assertFalse(self.field.cleaned_value)

    def test_value_inserted(self):
        self.field.value = 'Y'
        self.field.validate(index=0)
        self.assertTrue(self.field.cleaned_value)


class CharFieldTest(unittest.TestCase):
    def setUp(self):
        self.field = fields.CharField(max_length=4, verbose_name='Field')

    def test_blank_false(self):
        with self.assertRaises(fields.ValidationError):
            self.field.validate(index=0)

    def test_max_length(self):
        self.field.value = 'Tester'
        with self.assertRaises(fields.ValidationError):
            self.field.validate(index=0)

    def test_default(self):
        default_value = 'hello'
        field = fields.CharField(
            max_length=10,
            verbose_name='field',
            default=default_value,
            blank=True
        )
        field.validate(index=0)
        self.assertEqual(field.cleaned_value, default_value)

        field.value = 'world'
        field.validate(index=0)
        self.assertEqual(field.cleaned_value, 'world')

    def test_convert_number(self):
        self.field.value = 1000
        self.field.validate(index=0)
        self.assertEqual(self.field.cleaned_value, '1000')

    def test_choices(self):
        field = fields.CharField(
            max_length=6, verbose_name='Field', choices=['Hello', 'World']
        )
        field.value = 'Test'
        with self.assertRaises(fields.ValidationError):
            field.validate(index=0)

        # Should not raise exception
        field.value = 'Hello'
        field.validate(index=0)

    def test_case_sensitive_false(self):
        field = fields.CharField(
            max_length=6,
            verbose_name='field',
            choices=['Hello', 'World'],
            case_sensitive=False
        )
        field.value = 'heLLo'
        field.validate(index=0)
        self.assertEqual(field.cleaned_value, 'heLLo')

        field.value = 'WorLD'
        field.validate(index=0)
        self.assertEqual(field.cleaned_value, 'WorLD')


class IntegerFieldTest(unittest.TestCase):
    def test_blank(self):
        field = fields.IntegerField(verbose_name='field', blank=True)
        field.validate(index=0)
        self.assertIsNone(field.cleaned_value)

    def test_default_value(self):
        field = fields.IntegerField(verbose_name='field', blank=True, default=0)
        field.validate(index=0)
        self.assertEqual(field.cleaned_value, 0)

        field.value = 100
        field.validate(index=0)
        self.assertEqual(field.cleaned_value, 100)

    def test_convert_str_to_int(self):
        field = fields.IntegerField(verbose_name='field')
        field.value = '1000'
        field.validate(index=0)
        self.assertEqual(field.cleaned_value, 1000)

    def test_failed_convert_str_to_int(self):
        field = fields.IntegerField(verbose_name='field')
        field.value = 'hello'
        with self.assertRaises(fields.ValidationError):
            field.validate(index=0)


class DateFieldTest(unittest.TestCase):
    def test_from_str_to_date(self):
        field = fields.DateField(
            date_format='%Y-%m-%d',
            date_format_verbose='YYYY-MM-DD',
            verbose_name='field'
        )
        field.value = '2018-01-01'
        field.validate(index=0)
        self.assertEqual(field.cleaned_value, datetime(2018, 1, 1).date())

    def test_from_int_to_date(self):
        field = fields.DateField(
            date_format='%Y%m%d',
            date_format_verbose='YYYY-MM-DD',
            verbose_name='field'
        )
        field.value = 20180101
        field.validate(index=0)
        self.assertEqual(field.cleaned_value, datetime(2018, 1, 1).date())


class DateTimeTest(unittest.TestCase):
    def setUp(self):
        self.field = fields.DateTimeField(
            date_format='%Y-%m-%d %H:%M:%S',
            date_format_verbose='YYYY-MM-DD hh:mm:ss',
            verbose_name='field'
        )

    def test_from_str_to_datetime(self):
        self.field.value = '2018-01-01 09:00:00'
        self.field.validate(index=0)
        self.assertEqual(self.field.cleaned_value, datetime(2018, 1, 1, 9))

    def test_from_int_to_datetime(self):
        field = fields.DateTimeField(
            date_format='%Y%m%d%H%M%S',
            date_format_verbose='YYYYMMDDhhmmss',
            verbose_name='field'
        )
        field.value = 20180101090000
        field.validate(index=0)
        self.assertEqual(field.cleaned_value, datetime(2018, 1, 1, 9))
