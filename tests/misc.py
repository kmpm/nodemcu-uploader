# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
import unittest
from lib.utils import default_port
from lib import __version__

class MiscTestCase(unittest.TestCase):

    def test_version(self):
        self.assertEqual(__version__, '0.2.0')

    def test_default_port(self):
        #Test as if it were given system
        self.assertEqual(default_port('Linux'), '/dev/ttyUSB0')
        self.assertEqual(default_port('Windows'), 'COM1')
        self.assertEqual(default_port('Darwin'), '/dev/tty.SLAB_USBtoUART')

        self.assertTrue(len(default_port()) >= 3)
