#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2020 Peter Magnusson <me@kmpm.se>
"""Setup for nodemcu-uploader"""

from setuptools import setup

exec(open('nodemcu_uploader/version.py').read())  # pylint: disable=W0122

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name='nodemcu-uploader',
    version=__version__,  # noqa: F821
    python_requires='>=3.5',
    install_requires=[
        'pyserial>=3.4'
    ],
    packages=['nodemcu_uploader'],
    # package_dir={'nodemcu_uploader': 'lib'},
    url='https://github.com/kmpm/nodemcu-uploader',
    author='kmpm',
    author_email='me@kmpm.se',
    description='tool for uploading files to the filesystem of an ESP8266 running NodeMCU.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['esp8266', 'upload', 'nodemcu'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ],
    license='MIT',
    test_suite="tests.get_tests",
    entry_points={
        'console_scripts': [
            'nodemcu-uploader=nodemcu_uploader.main:main_func'
        ]
    },
    zip_safe=False,
)
