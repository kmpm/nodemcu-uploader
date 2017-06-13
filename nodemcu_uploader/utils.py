# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
"""Various utility functions"""

from platform import system
from os import environ
from wrapt import ObjectProxy
from sys import version_info

__all__ = ['default_port', 'system', 'hexify', 'from_file', 'wrap', 'PY2', 'ENCODING']

PY2 = version_info.major == 2

ENCODING = 'latin1'


def default_port(sysname=system()):
    """This returns the default port used for different systems if SERIALPORT env variable is not set"""
    system_default = {
        'Windows': 'COM1',
        'Darwin': '/dev/tty.SLAB_USBtoUART'
    }.get(sysname, '/dev/ttyUSB0')
    return environ.get('SERIALPORT', system_default)


def to_hex(x):
    return hex(ord(x))


def hexify(byte_arr):
    return ':'.join((to_hex(x)[2:] for x in byte_arr))


def from_file(path):
    with open(path, 'rb') as f:
        content = f.read()
    return content if PY2 else content.decode(ENCODING)


class DecoderWrapper(ObjectProxy):
    def read(self, *args, **kwargs):
        res = self.__wrapped__.read(*args, **kwargs)
        return res if PY2 else res.decode(ENCODING)

    def write(self, data):
        data = data if PY2 else data.encode(ENCODING)
        return self.__wrapped__.write(data)


def wrap(x):
    return DecoderWrapper(x)
