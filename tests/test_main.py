#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

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

    def test_should_failed_when_sheet_column_and_field_is_not_match(self):
        class Serializer(serializers.ExcelSerializer):
            field_name_1 = serializers.CharField(max_length=10, verbose_name='Field name 1')

            class Meta:
                start_index = 1
                fields = ('field_name_1',)

        with self.assertRaises(ColumnNotEqualError):
            Serializer(self.worksheet)


class TestValidation(unittest.TestCase):

    def setUp(self):
        workbook = WorkbookTesting()
        self.worksheet = workbook.worksheet

    def test_something(self):
        order_serializer = OrderExcelSerializer(self.worksheet)
        order_serializer.is_valid()
        print(order_serializer.errors)
        print(order_serializer.cleaned_data)
