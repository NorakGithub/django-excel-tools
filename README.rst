==================
Django Excel Tools
==================


.. image:: https://badge.fury.io/py/django-excel-tools.svg
        :target: https://badge.fury.io/py/django-excel-tools

.. image:: https://travis-ci.org/NorakGithub/django-excel-tools.svg?branch=master
        :target: https://travis-ci.org/NorakGithub/django-excel-tools


Common function when working with excel.

Requirements
------------
- Django_ (1.8 or higher version)
- openpyxl_


Installations
-------------
Install ``django-excel-tools``

.. code-block:: bash

    pip install django-excel-tools

Usage
-----
Class declaration

.. code-block:: python

    from django_excel_tools import serializers


    class OrderExcelSerializer(serializers.ExcelSerializers):
        REGION_CHOICES = ('Central', 'North', 'East', 'West', 'South')
        product_name = serializers.CharField(max_length=100, verbose_name='Product Name')
        quantity = serializers.IntegerField(verbose_name='Quantity', blank=True, default=0)
        price = serializers.IntegerField(verbose_name='Price')
        region = serializers.CharField(max_length=10, verbose_name='Region', choices=REGION_CHOICES)
        transaction_date = serializers.DateField(date_format='%Y-%m-%d', date_format_verbose='YYYY-MM-DD',
                                                 verbose_name='Transaction Date')

        class Meta:
            start_index = 1
            fields = ('product_name', 'quantity', 'price', 'region', 'transaction_date')

Class initialization

.. code-block:: python

    from openpyxl import load_workbook


    def import_order():
        workbook = load_workbook(file)  # Create workbook from file. Used openpyxl
        worksheet = workbook.worksheets[0]
        serializer = OrderExcelSerializer(worksheet=worksheet, **kwargs)

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _openpyxl: http://openpyxl.readthedocs.io/en/default/
.. _Django: https://docs.djangoproject.com
