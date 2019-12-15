# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 Peter Magnusson <peter@kmpm.se>
import unittest
from nodemcu_uploader.serialutils import default_port
from nodemcu_uploader import __version__
import os

from nodemcu_uploader import validate, exceptions


class MiscTestCase(unittest.TestCase):

    def test_version(self):
        self.assertEqual(__version__, '1.0.0')

    def test_default_port(self):
        if os.environ.get('SERIALPORT', 'none') != 'none':
            # SERIALPORT should override any system defaults
            self.assertEqual(default_port(), os.environ['SERIALPORT'])
        else:
            # Test as if it were given system
            self.assertEqual(default_port('Linux', False), '/dev/ttyUSB0')
            self.assertEqual(default_port('Windows', False), 'COM1')
            self.assertEqual(default_port('Darwin', False), '/dev/tty.SLAB_USBtoUART')

    def test_remote_path_validation(self):
        validate.remotePath("test/something/maximum/len.jpeg")
        validate.remotePath("a")

        def v(p):
            validate.remotePath(p)

        self.assertRaises(exceptions.ValidationException, (lambda: v("test/something/maximum/leng.jpeg")))
        self.assertRaises(exceptions.ValidationException, (lambda: v("")))
