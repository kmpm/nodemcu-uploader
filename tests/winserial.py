# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
import unittest
import os
import serial
from lib.utils import default_port
import time

SERIALPORT = os.environ.get('SERIALPORT', default_port())

def expect(port, timeout, exp='> '):
    timer = port.timeout
    # lt = 0.0001
    # if port.timeout != lt:
    #     port.timeout = lt
    end = time.time() + timeout

    data = ''
    while not data.endswith(exp) and time.time() <= end:
        data += port.read()

    # port.timeout = timer

    return data



class WinSerialCase(unittest.TestCase):
    port = None
    def setUp(self):
        self.port = serial.serial_for_url(SERIALPORT, 9600, timeout=5)

    def tearDown(self):
        self.port.close()

    def test_sync(self):
        self.port.write('print("%self%");\n'.encode())
        expect(self.port, 3)

        for i in range(50):
            self.port.write('print("%self%");\n'.encode())
            res = expect(self.port, 1)
            self.assertEqual(res, 'print("%self%");\r\n%self%\r\n> ')
            time.sleep(0.2)


