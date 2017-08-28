import datetime
from openpyxl import Workbook


from django_excel_tools import serializers


# Example Usage
class OrderExcelSerializer(serializers.ExcelSerializer):
    shop_name = serializers.CharField(max_length=100, verbose_name='Shop Name')
    order_number = serializers.CharField(max_length=100, verbose_name='Order Number')
    quantity = serializers.IntegerField(verbose_name='Quantity')
    sale_datetime = serializers.DateField(
        verbose_name='Sale Datetime', date_format='%Y-%m-%d', date_format_verbose='YYYY-MM-DD'
    )
    inspection_expired_date = serializers.DateField(
        verbose_name='Inspection Expired Date', date_format='%Y%m%d', date_format_verbose='YYYYMMDD'
    )
    registered_date = serializers.DateField(
        verbose_name='Expired Date', date_format='%Y%m', date_format_verbose='YYYYMM'
    )
    weight = serializers.IntegerField(verbose_name='Weight', blank=True)

    class Meta:
        start_index = 1
        fields = (
            'shop_name',
            'order_number',
            'sale_datetime',
            'quantity',
            'inspection_expired_date',
            'registered_date',
            'weight'
        )

    def validated(self, cleaned_data):
        pass

    def invalided(self, errors):
        pass


class WorkbookTesting(object):

    def __init__(self):
        self.workbook = Workbook()
        self.worksheet = self.workbook.active
        self._generate_title()
        self._generate_data()

    def _generate_title(self):
        self.worksheet['A1'] = 'Shop Name'
        self.worksheet['B1'] = 'Order Number'
        self.worksheet['C1'] = 'Sale Date'
        self.worksheet['D1'] = 'Quantity'
        self.worksheet['E1'] = 'Inspection Expired Date'
        self.worksheet['F1'] = 'Registered Date'
        self.worksheet['G1'] = 'Weight'

    def _generate_data(self):
        self.worksheet['A2'] = 'Shop A'
        self.worksheet['B2'] = '170707-001-00000-0'
        self.worksheet['C2'] = '2017-07-07'
        self.worksheet['D2'] = 100
        self.worksheet['E2'] = '20180101'
        self.worksheet['F2'] = '201801'
        self.worksheet['G2'] = None

        self.worksheet['A3'] = 'Shop B'
        self.worksheet['B3'] = '170707-001-00000-1'
        self.worksheet['C3'] = '2017-07-08'
        self.worksheet['D3'] = 1000
        self.worksheet['E3'] = datetime.date(2017, 1, 1)
        self.worksheet['F3'] = '201802'
        self.worksheet['G3'] = '1000'
