# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
"""Setup for nodemcu-uploader"""

from setuptools import setup

exec(open('nodemcu_uploader/version.py').read()) #pylint: disable=W0122

setup(name='nodemcu-uploader',
      version=__version__, #pylint: disable=E0602
      install_requires=[
          'pyserial>=2.7'
      ],
      packages=['nodemcu_uploader'],
      #package_dir={'nodemcu_uploader': 'lib'},
      url='https://github.com/kmpm/nodemcu-uploader',
      author='kmpm',
      author_email='peter@birchroad.net',
      description='tool for uploading files to the filesystem of an ESP8266 running NodeMCU.',
      keywords=['esp8266', 'upload', 'nodemcu'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2.7'
      ],
      license='MIT',
      test_suite="tests.get_tests",
      entry_points={
          'console_scripts': [
              'nodemcu-uploader=nodemcu_uploader.main:main_func'
          ]
      },
      zip_safe=False
     )
