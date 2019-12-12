# -*- coding: utf-8 -*-
import unittest
import logging
import time
import os
from nodemcu_uploader import Uploader
from nodemcu_uploader.main import operation_download, operation_upload
import shutil

log = logging.getLogger(__name__)
logging.basicConfig(
    filename='test.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(module)s.%(funcName)s %(message)s')

LOOPPORT = 'loop://'

# on which port should the tests be performed
SERIALPORT = os.environ.get('SERIALPORT', LOOPPORT)


def is_real():
    if SERIALPORT.strip() == '':
        return False
    return str(SERIALPORT) != str(LOOPPORT)


@unittest.skipUnless(is_real(), 'Needs a configured SERIALPORT')
class TestTorture(unittest.TestCase):
    uploader = None

    def setUp(self):
        self.uploader = Uploader(SERIALPORT)

    def tearDown(self):
        if is_real():
            self.uploader.node_restart()
        self.uploader.close()
        time.sleep(1)

    def task_upload_verify_compile(self):
        print('upload-verify-compile')
        self.assertTrue(self.uploader.prepare())
        pattern = os.path.join('tests', 'fixtures', '*.lua')
        self.assertEqual(pattern, "tests\\fixtures\\*.lua")
        dests = operation_upload(self.uploader, "tests/fixtures/*.lua", 'sha1', True, False, False)
        return len(dests)

    def task_check_remote_files(self, wanted):
        lst = self.uploader.file_list()
        self.assertIsInstance(lst, type([]))
        self.assertEqual(len(lst), wanted)
        return lst

    def task_remove_all_files(self):
        print('remove all files')
        self.uploader.file_remove_all()

    def task_download_all_files(self, files):
        print('download all files', files)
        dest = os.path.join('.', 'tmp')
        operation_download(self.uploader, files, dest=dest)
        for f in files:
            self.assertTrue(os.path.isfile(os.path.join(dest, f)))

    def task_remove_tmp(self):
        dest = os.path.join('.', 'tmp')
        if os.path.isdir(dest):
            shutil.rmtree(dest)

    def test_for_long_time(self):
        for x in range(20):
            print('{x} test sequence'.format(x=x+1))
            self.task_remove_tmp()
            self.task_remove_all_files()
            self.task_check_remote_files(0)
            time.sleep(0.5)
            count = self.task_upload_verify_compile()
            self.assertEqual(count, 3)
            files = self.task_check_remote_files(count)
            self.task_download_all_files(list(map(lambda x: x[0], files)))
