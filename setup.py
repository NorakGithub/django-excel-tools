#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as changelog_file:
    changelog = changelog_file.read()

setup(
    author="Khemanorak Khath",
    author_email='khath.khemanorak@gmail.com',
    url='https://github.com/NorakGithub/django-excel-tools',
    name='django_excel_tools',
    version_format='{tag}',
    description="Common function when working with excel.",
    long_description=readme + '\n\n' + changelog,
    long_description_content_type='text/markdown',
    packages=find_packages(include=['django_excel_tools']),
    include_package_data=True,
    license="MIT license",
    zip_safe=False,
    keywords='django, excel, tools',
    setup_requires=[
        'setuptools-git-version'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
