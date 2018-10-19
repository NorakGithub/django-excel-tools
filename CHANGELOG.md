# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2018-10-19
### Breaking Change
- Meta.django_enable_transaction has changed to enable_transaction

### Changed
- Moved all fields class from `django_excel_tools.serializers` to `django_excel_tools.fields`
- Code refactored for `django_excel_tools.serializers.ExcelSerializer` to more readable and pure function that doesn't produce effect.

### Added
- More test coverage
