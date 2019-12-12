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
    level=logging.INFO,
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
        log.info("setUp")
        self.uploader = Uploader(SERIALPORT)

    def tearDown(self):
        log.info("tearDown")
        if is_real():
            self.uploader.node_restart()
        self.uploader.close()
        time.sleep(1)

    def task_upload_verify_compile(self):
        """Upload lua code, verify and compile"""
        log.info('upload-verify-compile')
        self.assertTrue(self.uploader.prepare())
        dests = operation_upload(self.uploader, "tests/fixtures/*.lua", 'sha1', True, False, False)
        return len(dests)

    def task_upload_verify(self):
        """Upload some text files and verify"""
        log.info('upload-verify')
        dests = operation_upload(self.uploader, "tests/fixtures/*_file.txt", 'sha1', False, False, False)
        return len(dests)

    def task_check_remote_files(self, wanted):
        """Check that the wanted number of files exists on the device"""
        lst = self.uploader.file_list()
        self.assertIsInstance(lst, type([]))
        self.assertEqual(len(lst), wanted)
        return lst

    def task_remove_all_files(self):
        """Remove all files on device"""
        log.info('remove all files')
        self.uploader.file_remove_all()

    def task_download_all_files(self, files):
        """Downloads all files on device and do a sha1 checksum"""
        log.info('download all files and verify. %s', files)
        dest = os.path.join('.', 'tmp')
        operation_download(self.uploader, files, dest=dest)
        for f in files:
            local = os.path.join(dest, f)
            self.assertTrue(os.path.isfile(local))
            self.uploader.verify_file(local, f, 'sha1')

    def task_remove_tmp(self):
        """Removes local tmp folder"""
        dest = os.path.join('.', 'tmp')
        if os.path.isdir(dest):
            shutil.rmtree(dest)

    def test_for_long_time(self):
        """Run a sequence of steps a number of times"""
        testcount = 10
        for x in range(testcount):
            print('test sequence {0}/{1}'.format(x+1, testcount))
            log.info('--- test sequence {0}/{1} ---'.format(x+1, testcount))
            self.task_remove_tmp()
            self.task_remove_all_files()
            self.task_check_remote_files(0)
            time.sleep(0.5)
            count = self.task_upload_verify_compile()
            self.assertEqual(count, 3)
            count += self.task_upload_verify()
            self.assertEqual(count, 6)
            files = self.task_check_remote_files(count)
            self.task_download_all_files(list(map(lambda x: x[0], files)))
