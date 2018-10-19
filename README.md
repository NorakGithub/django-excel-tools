# Django Excel Tools

[![pipy](https://badge.fury.io/py/django-excel-tools.svg)](https://badge.fury.io/py/django-excel-tools)
[![travis](https://travis-ci.org/NorakGithub/django-excel-tools.svg?branch=master)](https://travis-ci.org/NorakGithub/django-excel-tools)

Serializing excel data to python format for easier to manage.

## Requirements
- Django (1.8 or higher version)
- OpenPYXL

## Installation
Install via pip

```bash
pip install django-excel-tools
```

## Documentation
- [Serializer Overridable Functions](#serializer-overridable-functions)
- [Fields References](#fields-references)
    - [Common Argument](#common-argument)
    - [BooleanField](#booleanfield)
    - [CharField](#charfield)
    - [IntegerField](#integerfield)
    - [DateField](#datefield)
    - [DateTimeField](#datetimefield)
- [Example Usage](#example-usage)

### Serializer Overridable Functions

`row_extra_validation`
This function will call each time a row has been validated.
This is for the case where you want a row of excel data that has been
validated and then you want to add your own validation.

`extra_clean_{field name}`
This function will be call when a column cell is validated and you would like to add custom validation. **field name** must be match with field name defined in `Meta.fields`.

`validated`
This function will be call when all data in excel is validated.

`invalid`
This function will be call when there are one or more errors happen during data validation. Simply put `validation_errors` is not empty.

`operation_failed`
This function will be call when there are one or more errors happen during import operation. Simply put `operation_errors` is not empty.

`operation_success`
This function will be call when there is no error happen during import operation. Simply put `operation_errors` is empty.

`import_operation`
This function will be call after all data in excel is validated, and this is also the place where you add your function of how you gonna insert all the cleaned excel data to your database. Check usage below for the example code.

### Fields References
#### Common Argument
`verbose_name`

This field will be used in case of error, so we know exactly which column fix.

#### BooleanField
Required argument:
`verbose_name`

Corresponds to `django_excel_tools.fields.BooleanField`

#### CharField
Required arguments:
`max_length` The max length of text that is acceptable.
`verbose_name` This field will be used in case of error, so we know exactly which column fix.

Optional arguments:
`convert_number` automatically convert int or number to string. Default `True`.
`choices` only accept value in choices if not match `ValidationError` will raise. Default `None`.
`default` this value will be used when excel is blank. Default `None`.
`case_sensitive` this is used in case of choices are set, comparing choices with case sensitive or not. Default `True`.

Corresponds to `django_excel_tools.fields.CharField`

#### IntegerField
Required arguments:
`verbose_name`

Optional arguments:
`default` this value will be used when excel is blank. Default is `None`
`convert_str` this value will be used to convert string to int, if failed `ValidationError` will be raised. Default is `True`.
`blank` this tell the field is allowed to blank or not. Default is `False`.
`choices` this tell the field is only accept value from choices, otherwise `ValidationError` will be raised. Default is `None`.

Corresponds to `django_excel_tools.fields.IntegerField`

#### DateField
Required arguments:
`date_format` This will be use for string formatting date from string.
`date_format_verbose` This will be used when error occurred, so that user may know how to change to the correct format.
`verbose_name`

Optional Arguments:
`blank` this tell the field is allowed to blank or not. Default is `False`.

Corresponds to `django_excel_tools.fields.DateField`
#### DateTimeField
Required arguments:
`date_format` This will be use for string formatting date from string.
`date_format_verbose` This will be used when error occurred, so that user may know how to change to the correct format.
`verbose_name`

Optional Arguments:
`blank` this tell the field is allowed to blank or not. Default is `False`.

Corresponds to `django_excel_tools.fields.DateTimeField`

### Example Usage
**Class Excel Serializer**
```python
from django_excel_tools import serializers


class StaffExcelSerializer(serializers.ExcelSerializer)
    GENDER_CHOICES = ['male', 'female']

    code = serializers.IntegerField(verbose_name='Code')
    name = serializers.CharField(max_length=100, verbose_name='Name')
    gender = serializers.CharField(
        max_length=5,
        verbose_name='GENDER',
        choices=GENDER_CHOICES
    )
    date_of_birth = serializers.DateField(
        blank=True,
        date_format='%Y-%m-%d',
        date_format_verbose='YYYY-MM-DD',
        verbose='Date of Birth'
    )

    class Meta:
        start_index = 1
        fields = ('code', 'name', 'gender', 'date_of_birth')
        enable_transaction = True  # Default is True

    def row_extra_validation(self, index, cleaned_row):
        # Code 100 must be female
        code = cleaned_row['code']
        gender = clenaed_row['gender']

        if code != 100:
            return cleaned_row
        if gender != 'female':
            raise serializers.exceptions.ValidationError(
                message='[Row {index}] {message}'.format(
                    index=index,
                    message='Code 100 cannot be other than female'
                )
        return cleaned_row

    def extra_clean_name(self, cleaned_value):
        return 'Hello {}'.format(cleaned_value)

    def validated(self):
        # Notified that excel is successfully validated

    def invalid(self, errors):
        # Notify that excel format is not valid and errors argument is
        # the list of errors message

    def operation_failed(self, errors):
        # Error during import operation

    def operation_success(self):
        # Import operation success

    def import_operation(self, cleaned_data):
        for index, row in enumerate(cleaned_data):
            try:
                Staff.objects.create(**row)
            except Exception as e:
                self.operation_error.append(self.gen_error(index, str(e)))
                continue
```

**Usage**
```python
from openpyxl import load_workbook


def import_view(request):
    excel_file = request.files[0]
    workbook = load_workbook(file)
    worksheet = workbook.worksheets[0]
    serializer = StaffExcelSerializer(worksheet=worksheet)
    if serializer.validation_errors:
        return Response(data=serializer.validation_errors, status=400)
    if serializer.operation_errors:
        return Response(data=serializer.operation_errors, status=400
    return Response(status=201)
```


## License
MIT License

Copyright (c) 2017, Khemanorak Khath

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
