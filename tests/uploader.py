# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
import unittest
import os, time
from nodemcu_uploader import Uploader, __version__

LOOPPORT='loop://'

#on which port should the tests be performed
SERIALPORT = os.environ.get('SERIALPORT', LOOPPORT)


class UploaderTestCase(unittest.TestCase):
    uploader = None
    def setUp(self):
        self.uploader =  Uploader(SERIALPORT)

    def tearDown(self):
        self.uploader.node_restart()
        self.uploader.close()
        time.sleep(1)

    # def test_initialize(self):
    #     print SERIALPORT



    @unittest.skipUnless(SERIALPORT <>  LOOPPORT, 'Needs a configured SERIALPORT')
    def test_upload_and_verify_raw(self):
        self.uploader.prepare()
        self.uploader.write_file('tests/fixtures/big_file.txt', verify='raw')

