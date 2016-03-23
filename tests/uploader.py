# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
import unittest
import os, time
from nodemcu_uploader import Uploader

LOOPPORT = 'loop://'

#on which port should the tests be performed
SERIALPORT = os.environ.get('SERIALPORT', LOOPPORT)

def is_real():
    if SERIALPORT.strip() == '':
        return False
    return str(SERIALPORT) != str(LOOPPORT)

class UploaderFakeTestCase(unittest.TestCase):
    def test_init(self):
        uploader = Uploader(SERIALPORT)
        uploader.close()

@unittest.skipUnless(is_real(), 'Needs a configured SERIALPORT')
class UploaderTestCase(unittest.TestCase):
    uploader = None
    def setUp(self):
        self.uploader = Uploader(SERIALPORT)

    def tearDown(self):
        if is_real():
            self.uploader.node_restart()
        self.uploader.close()
        time.sleep(1)


    def test_upload_and_verify_raw(self):
        self.uploader.prepare()
        self.uploader.write_file('tests/fixtures/big_file.txt', verify='raw')


    def test_upload_and_verify_sha1(self):
        self.uploader.prepare()
        self.uploader.write_file('tests/fixtures/big_file.txt', verify='sha1')


    def test_upload_strange_file(self):
        self.uploader.prepare()
        self.uploader.write_file('tests/fixtures/testuploadfail.txt', verify='raw')

