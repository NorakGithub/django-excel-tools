#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

import datetime
from openpyxl import Workbook

from django_excel_tools import serializers
from django_excel_tools.exceptions import ColumnNotEqualError, FieldNotExist
from tests.workbook import WorkbookTesting, OrderExcelSerializer


class TestSerializer(unittest.TestCase):

    def setUp(self):
        workbook = Workbook()
        self.worksheet = workbook.active
        self.worksheet['A1'] = 'Field name 1'
        self.worksheet['B2'] = 'Field name 2'
        self.worksheet['A2'] = 'value 1'
        self.worksheet['B2'] = 'value 2'

    def test_should_field_when_no_class_meta(self):
        class Serializer(serializers.ExcelSerializer):
            pass

        with self.assertRaises(AssertionError):
            Serializer(self.worksheet)

    def test_should_failed_when_not_adding_start_index(self):
        class Serializer(serializers.ExcelSerializer):
            class Meta:
                pass
        with self.assertRaises(AssertionError):
            Serializer(self.worksheet)

    def test_should_failed_when_not_adding_fields(self):
        class Serializer(serializers.ExcelSerializer):
            class Meta:
                start_index = 1

        with self.assertRaises(AssertionError):
            Serializer(self.worksheet)

    def test_should_failed_when_no_fields(self):
        class Serializer(serializers.ExcelSerializer):
            class Meta:
                start_index = 1
        with self.assertRaises(AssertionError):
            Serializer(self.worksheet)

    def test_should_failed_when_fields_is_not_set(self):
        class Serializer(serializers.ExcelSerializer):
            field_name_1 = serializers.CharField(max_length=10, verbose_name='Field name 1')
            field_name_2 = serializers.CharField(max_length=10, verbose_name='Field name 2')

            class Meta:
                start_index = 1

        with self.assertRaises(AssertionError):
            Serializer(self.worksheet)

    def test_should_failed_when_field_is_not_defined_included(self):
        class Serializer(serializers.ExcelSerializer):
            field_name_1 = serializers.CharField(max_length=10, verbose_name='Field name 1')

            class Meta:
                start_index = 1
                fields = ('field_name_1', 'field_name')

        with self.assertRaises(FieldNotExist):
            Serializer(self.worksheet)


class TestField(unittest.TestCase):

    def setUp(self):
        workbook = WorkbookTesting()
        self.worksheet = workbook.worksheet
        self.basic_data = ['Shop', '10', '2017-07-07', 100, '20180101', 201801, '100', u'無', 'AB', '123/Home']

    def test_allow_blank_with_empty_string(self):
        self.basic_data[9] = ''
        self.worksheet.append(self.basic_data)
        serializer = OrderExcelSerializer(self.worksheet)
        self.assertFalse(serializer.errors)

    def test_allow_blank_but_there_is_data(self):
        self.worksheet.append(self.basic_data)
        serializer = OrderExcelSerializer(self.worksheet)
        self.assertFalse(serializer.errors)
        self.assertEqual(serializer.cleaned_data[0]['shop_name'], 'Shop')

    def test_not_allow_blank_with_empty_string(self):
        self.basic_data[0] = '  '  # Set shop field to blank
        self.worksheet.append(self.basic_data)
        serializer = OrderExcelSerializer(self.worksheet)
        self.assertTrue(serializer.errors)

    def test_not_allow_blank_with_zero(self):
        self.basic_data[0] = 0
        self.worksheet.append(self.basic_data)
        serializer = OrderExcelSerializer(self.worksheet)
        self.assertFalse(serializer.errors)
        self.assertEqual(serializer.cleaned_data[0]['shop_name'], '0')

    def test_max_length(self):
        self.basic_data[0] = '123456789010'
        self.worksheet.append(self.basic_data)
        serializer = OrderExcelSerializer(self.worksheet)
        self.assertTrue(serializer.errors)

    def test_default_int(self):
        self.basic_data[6] = ''
        self.worksheet.append(self.basic_data)
        serializer = OrderExcelSerializer(self.worksheet)
        self.assertFalse(serializer.errors)

    def test_datetime_field(self):
        self.worksheet.append(self.basic_data)
        serializer = OrderExcelSerializer(self.worksheet)
        self.assertFalse(serializer.errors)

        date = datetime.datetime(year=2018, month=1, day=1).date()
        self.assertEqual(serializer.cleaned_data[0]['registered_date'], date)


class TestResult(unittest.TestCase):

    def setUp(self):
        workbook = WorkbookTesting()
        self.worksheet = workbook.worksheet
        self.worksheet.append(workbook.row_1)
        self.worksheet.append(workbook.row_2)

    def test_result(self):
        order_serializer = OrderExcelSerializer(self.worksheet)
        data = order_serializer.cleaned_data
        first_row = data[0]
        self.assertEqual(first_row['shop_name'], 'Shop A')
        self.assertEqual(first_row['quantity'], 100)
        self.assertEqual(first_row['default_checked'], True)
        self.assertEqual(first_row['weight'], 100)
        self.assertEqual(first_row['address'], '123/Home')

        second_row = data[1]
        self.assertEqual(second_row['shop_name'], 'Shop B')
        self.assertEqual(second_row['quantity'], 1000)
        self.assertEqual(second_row['default_checked'], False)
        self.assertEqual(second_row['weight'], 0)
        self.assertEqual(second_row['address'], '')
