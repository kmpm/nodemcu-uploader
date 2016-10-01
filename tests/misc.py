# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
import unittest
from nodemcu_uploader.utils import default_port
from nodemcu_uploader import __version__
import os

class MiscTestCase(unittest.TestCase):

    def test_version(self):
        self.assertEqual(__version__, '0.4.1')

    def test_default_port(self):
        if os.environ.get('SERIALPORT', 'none') != 'none':
            #SERIALPORT should override any system defaults
            self.assertEqual(default_port(), os.environ['SERIALPORT'])
        else:
            #Test as if it were given system
            self.assertEqual(default_port('Linux'), '/dev/ttyUSB0')
            self.assertEqual(default_port('Windows'), 'COM1')
            self.assertEqual(default_port('Darwin'), '/dev/tty.SLAB_USBtoUART')
