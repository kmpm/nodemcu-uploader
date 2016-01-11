#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>

from platform import system

def default_port():
    return {
        'Windows': 'COM1',
        'Darwin': '/dev/tty.SLAB_USBtoUART'
    }.get(system(), '/dev/ttyUSB0')

