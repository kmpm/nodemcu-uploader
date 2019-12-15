# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 Peter Magnusson <peter@kmpm.se>
"""Various utility functions"""

from platform import system

# from wrapt import ObjectProxy
from sys import version_info

__all__ = ['system', 'hexify', 'from_file', 'PY2', 'ENCODING']

PY2 = version_info.major == 2

if PY2:
    raise Exception("Python 2 is no longer supported")

ENCODING = 'latin1'


def to_hex(x):
    if isinstance(x, int):
        return hex(x)
    return hex(ord(x))


def hexify(byte_arr):
    if isinstance(byte_arr, int):
        return to_hex(byte_arr)[2:]
    else:
        return ':'.join((to_hex(x)[2:] for x in byte_arr))


def from_file(path):
    """Returns content of file as 'bytes'.
    """
    with open(path, 'rb') as f:
        content = f.read()
    return content
