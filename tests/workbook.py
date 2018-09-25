#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from openpyxl import Workbook


from django_excel_tools import serializers


# Example Usage
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


class WorkbookTesting(object):

    def __init__(self):
        self.workbook = Workbook()
        self.worksheet = self.workbook.active
        self._generate_title()
        self.row_1 = ['Shop A', '170707-001-00000-0', '2017-07-07', 100, '20180101', '201801', '100', u'無', 'AB',
                      '123/Home', 'Yes']
        self.row_2 = ['Shop B', '170707-001-00000-1', '2017-07-08', '1000', datetime.date(2017, 1, 1), '201802', 0,
                      u'無', None, '', 'No']

    def _generate_title(self):
        self.worksheet.append([
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
