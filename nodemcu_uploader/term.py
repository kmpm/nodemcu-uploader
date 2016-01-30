#!/usr/bin/env python
# -*- coding: utf-8 -*-
from serial.tools import miniterm
import sys

from .utils import default_port

def terminal(port=default_port()):
    testargs = ['nodemcu-uploader', port]
    # TODO: modifying argv is no good 
    sys.argv = testargs
    # resuse miniterm on main function
    miniterm.main()  
    