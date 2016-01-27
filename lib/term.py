#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .utils import default_port
try:
    from serial.tools.miniterm import Miniterm, NEWLINE_CONVERISON_MAP
    import serial
    MINITERM_AVAILABLE=True
except ImportError:
    MINITERM_AVAILABLE=False
    
try:
    from serial.tools.miniterm import console
    CONSOLE_AVAILABLE=True
except ImportError:
    CONSOLE_AVAILABLE=False


class McuMiniterm(Miniterm):
    def __init__(self, serial):
        if not MINITERM_AVAILABLE:
            print "Miniterm is not available on this system"
            return
        self.serial = serial
        self.echo = False
        self.convert_outgoing = 2
        self.repr_mode = 1
        self.newline = NEWLINE_CONVERISON_MAP[self.convert_outgoing]
        self.dtr_state = True
        self.rts_state = True
        self.break_state = False


def terminal(port=default_port()):
    if not MINITERM_AVAILABLE:
        print "Miniterm is not available on this system"
        return False
    sp = serial.Serial(port, 9600)
    
    # Keeps things working, if following conections are made:
    ## RTS = CH_PD (i.e reset)
    ## DTR = GPIO0
    sp.setRTS(False)
    sp.setDTR(False)
    miniterm = McuMiniterm(sp)

    log.info('Started terminal. Hit ctrl-] to leave terminal')
    if CONSOLE_AVAILABLE:
        console.setup()
    miniterm.start()
    try:
        miniterm.join(True)
    except KeyboardInterrupt:
        pass
    miniterm.join()
    sp.close()