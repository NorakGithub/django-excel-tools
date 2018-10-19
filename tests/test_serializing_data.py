#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

import datetime
from openpyxl import Workbook

from django_excel_tools import serializers


class OrderExcelSerializer(serializers.ExcelSerializer):
    QR_SCANNED_CHOICES = (u'有', u'無')
    ACTIVE_CHOICES = ('Yes', 'No')

    shop_name = serializers.CharField(max_length=10, verbose_name='Shop Name')
    order_number = serializers.CharField(max_length=20, verbose_name='Order Number')
    quantity = serializers.IntegerField(verbose_name='Quantity')
    sale_datetime = serializers.DateField(
        verbose_name='Sale Datetime', date_format='%Y-%m-%d', date_format_verbose='YYYY-MM-DD'
    )
    inspection_expired_date = serializers.DateField(
        verbose_name='Inspection Expired Date', date_format='%Y%m%d', date_format_verbose='YYYYMMDD'
    )
    registered_date = serializers.DateField(
        verbose_name='Expired Date', date_format='%Y%m', date_format_verbose='YYYYMM', blank=True
    )
    weight = serializers.IntegerField(verbose_name='Weight', blank=True, default=0)
    qr_scanned = serializers.CharField(max_length=2, verbose_name='QR Scanned', choices=QR_SCANNED_CHOICES)
    default_checked = serializers.BooleanField(verbose_name='Default Checked')
    address = serializers.CharField(max_length=100, blank=True, verbose_name='Address')
    active = serializers.CharField(
        max_length=5, blank=True, verbose_name='Active', choices=ACTIVE_CHOICES, case_sensitive=False
    )

    def extra_clean_active(self, cleaned_value):
        return True if cleaned_value == 'Yes' else False

    class Meta:
        start_index = 1
        fields = (
            'shop_name',
            'order_number',
            'sale_datetime',
            'quantity',
            'inspection_expired_date',
            'registered_date',
            'weight',
            'qr_scanned',
            'default_checked',
            'address',
            'active'
        )


class TestExpectedResult(unittest.TestCase):
    def setUp(self):
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.append([
            'Shop Name',
            'Order Number',
            'Sale Date',
            'Quantity',
            'Inspection Expired Date',
            'Registered Date',
            'Weight',
            'QR Scanned',
            'Default Checked',
            'Address',
            'Active'
        ])
        worksheet.append([
            'Shop A', '170707-001-00000-0', '2017-07-07', 100, '20180101',
            '201801', '100', u'無', 'AB', '123/Home', 'Yes'
        ])
        worksheet.append([
            'Shop B', '170707-001-00000-1', '2017-07-08', '1000',
            datetime.date(2017, 1, 1), '201802', 0, u'無', None, '', 'No'
        ])
        worksheet.append(['', '', '', ''])
        self.serializer = OrderExcelSerializer(worksheet)

    def test_result(self):
        self.assertEqual(self.serializer.validation_errors, [], self.serializer.validation_errors)
        data = self.serializer.cleaned_data
        first_row = data[0]
        self.assertEqual(first_row['shop_name'], 'Shop A')
        self.assertEqual(first_row['quantity'], 100)
        self.assertEqual(first_row['default_checked'], True)
        self.assertEqual(first_row['weight'], 100)
        self.assertEqual(first_row['address'], '123/Home')
        self.assertEqual(first_row['active'], True)

        second_row = data[1]
        self.assertEqual(second_row['shop_name'], 'Shop B')
        self.assertEqual(second_row['quantity'], 1000)
        self.assertEqual(second_row['default_checked'], False)
        self.assertEqual(second_row['weight'], 0)
        self.assertEqual(second_row['address'], '')
        self.assertEqual(second_row['active'], False)
