# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 Peter Magnusson <peter@kmpm.se>

from platform import system
from os import environ
from serial.tools import list_ports


def default_port(sysname=system(), detect=True):
    """This returns the default port used for different systems if SERIALPORT env variable is not set"""
    system_default = {
        'Windows': 'COM1',
        'Darwin': '/dev/tty.SLAB_USBtoUART'
    }.get(sysname, '/dev/ttyUSB0')
    # if SERIALPORT is set then don't even waste time detecting ports
    if 'SERIALPORT' not in environ and detect:
        try:
            ports = list_ports.comports(include_links=False)
            if len(ports) == 1:
                return ports[0].device
            else:
                # clever guessing, sort of
                # vid/pid
                # 4292/60000 adafruit huzzah
                for p in ports:
                    if p.vid == 4292 and p.pid == 60000:
                        return p.device
                # use last port as fallback
                return ports[-1].device
        except Exception:
            pass

    return environ.get('SERIALPORT', system_default)
