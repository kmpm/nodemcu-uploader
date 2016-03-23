# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
"""Various utility functions"""

from platform import system
from os import environ

__all__ = ['default_port', 'system']

def default_port(sysname=system()):
    """This returns the default port used for different systems if SERIALPORT env variable is not set"""
    system_default = {
        'Windows': 'COM1',
        'Darwin': '/dev/tty.SLAB_USBtoUART'
    }.get(sysname, '/dev/ttyUSB0')
    return environ.get('SERIALPORT', system_default)

