#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
log = logging.getLogger(__name__)
from .utils import default_port
import serial


try:
    from serial.tools.miniterm import Miniterm
    MINITERM_AVAILABLE=True
except ImportError as ex:
    log.warn(ex)
    MINITERM_AVAILABLE=False

# try:
#     from serial.tools.miniterm import console
#     CONSOLE_AVAILABLE=True
# except ImportError:
#     CONSOLE_AVAILABLE=False

# try:
#     raw_input
# except NameError:
#     raw_input = input   # in python3 it's "raw"
#     unichr = chr



class McuMiniterm(Miniterm):
    def __init__(self, serial):
        
        super(McuMiniterm, self).__init__(serial, echo=False)
        # self.serial = serial
        # self.echo = False
        # self.convert_outgoing = 2
        # self.repr_mode = 1
        # self.newline = NEWLINE_CONVERISON_MAP[self.convert_outgoing]
        # self.dtr_state = True
        # self.rts_state = True
        # self.break_state = False
        # self.exit_character = unichr(args.exit_char)
        # self.menu_character = unichr(args.menu_char)
        self.raw = False
        self.set_rx_encoding('UTF-8')
        self.set_tx_encoding('UTF-8')


def terminal(port=default_port()):
    if not MINITERM_AVAILABLE:
        print "Miniterm is not available on this system"
        return False
    sp = serial.Serial(port, 9600)
    
    # sp = serial.serial_for_url('loop://', 9600)

    # Keeps things working, if following conections are made:
    ## RTS = CH_PD (i.e reset)
    ## DTR = GPIO0
    sp.setRTS(False)
    sp.setDTR(False)
    miniterm = McuMiniterm(sp)
    log.info('--- Miniterm on {p.name}  {p.baudrate},{p.bytesize},{p.parity},{p.stopbits} ---\n'.format(
                p=miniterm.serial))

    log.info('Started terminal. Hit ctrl-] to leave terminal')
    # if CONSOLE_AVAILABLE:
    #     console.setup()
    miniterm.start()
    try:
        miniterm.join(True)
    except KeyboardInterrupt:
        pass
    miniterm.join()
    sp.close()