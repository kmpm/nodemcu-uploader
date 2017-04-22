# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
"""Various utility functions"""

from platform import system
from os import environ
from wrapt import ObjectProxy

__all__ = ['default_port', 'system']


ENCODING = 'latin1'


def default_port(sysname=system()):
    """This returns the default port used for different systems if SERIALPORT env variable is not set"""
    system_default = {
        'Windows': 'COM1',
        'Darwin': '/dev/tty.SLAB_USBtoUART'
    }.get(sysname, '/dev/ttyUSB0')
    return environ.get('SERIALPORT', system_default)


def bytefy(x):
    return x if type(x) == bytes else x.encode(ENCODING)


def to_hex(x):
    return hex(x) if type(x) == bytes else hex(ord(x))


def hexify(byte_arr):
    return ':'.join((to_hex(x)[2:] for x in byte_arr))


def from_file(path):
    with open(path, 'rb') as f:
        content = f.read().decode(ENCODING)
    return content


class DecoderWrapper(ObjectProxy):
    def read(self, *args, **kwargs):
        return self.__wrapped__.read(*args, **kwargs).decode(ENCODING)

    def write(self, data):
        return self.__wrapped__.write(data.encode(ENCODING))


def wrap(x):
    return DecoderWrapper(x)
