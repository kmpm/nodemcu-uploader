# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
import unittest
from lib import Uploader, __version__

#on which port should the tests be performed
PORT = 'loop://'

#which speed should the tests use
BAUD = 115200

class UploaderTestCase(unittest.TestCase):



    def test_initialize(self):
        uploader = Uploader(PORT, BAUD)
