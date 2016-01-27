#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>

import time
import logging
import hashlib
import os
import serial

from .utils import default_port
from .luacode import DOWNLOAD_FILE, SAVE_LUA, LUA_FUNCTIONS, LIST_FILES, UART_SETUP

log = logging.getLogger(__name__)

__all__ = ['Uploader', 'default_port']


class Uploader(object):
    """Uploader is the class for communicating with the nodemcu and
    that will allow various tasks like uploading files, formating the filesystem etc.
    """
    BAUD = 9600
    TIMEOUT = 5
    PORT = default_port()

    def __init__(self, port=PORT, baud=BAUD):
        log.info('opening port %s with %s baud', port, baud)
        if port == 'loop://':
            self._port = serial.serial_for_url(port, baud, timeout=Uploader.TIMEOUT)
        else:
            self._port = serial.Serial(port, baud, timeout=Uploader.TIMEOUT)

        # Keeps things working, if following conections are made:
        ## RTS = CH_PD (i.e reset)
        ## DTR = GPIO0
        self._port.setRTS(False)
        self._port.setDTR(False)

        def sync():
            # Get in sync with LUA (this assumes that NodeMCU gets reset by the previous two lines)
            log.debug('getting in sync with LUA');
            self.clear_buffers()
            self.exchange(';') # Get a defined state
            self.writeln('print("%sync%");')
            self.expect('%sync%\r\n> ')
        sync()
        if baud != Uploader.BAUD:
            log.info('Changing communication to %s baud', baud)
            self.writeln(UART_SETUP.format(baud=baud))

            # Wait for the string to be sent before switching baud
            time.sleep(0.1)
            self.set_baudrate(baud)

            # Get in sync again
            sync()

        self.line_number = 0

    def set_baudrate(self, baud):
        try:
            self._port.setBaudrate(baud)
        except AttributeError:
            #pySerial 2.7
            self._port.baudrate = baud
    
    
    def clear_buffers(self):
        try:
            self._port.reset_input_buffer()
            self._port.reset_output_buffer()
        except AttributeError:
            #pySerial 2.7
            self._port.flushInput()
            self._port.flushOutput()
        

    def expect(self, exp='> ', timeout=TIMEOUT):
        """will wait for exp to be returned from nodemcu or timeout"""
        timer = self._port.timeout

        # Checking for new data every 100us is fast enough
        lt = 0.0001
        if self._port.timeout != lt:
            self._port.timeout = lt

        end = time.time() + timeout

        # Finish as soon as either exp matches or we run out of time (work like dump, but faster on success)
        data = ''
        while not data.endswith(exp) and time.time() <= end:
            data += self._port.read()
        
        if time.time() > end and not data.endswith(exp) and len(exp) > 0:
            raise Exception('Timeout expecting ' + exp)
        
        self._port.timeout = timer
        log.debug('expect returned: `{0}`'.format(data))
        return data

    def write(self, output, binary=False):
        """write data on the nodemcu port. If 'binary' is True the debug log
        will show the intended output as hex, otherwise as string"""
        if not binary:
            log.debug('write: %s', output)
        else:
            log.debug('write binary: %s', ':'.join(x.encode('hex') for x in output))
        self._port.write(output)
        self._port.flush()

    def writeln(self, output):
        """write, with linefeed"""
        self.write(output + '\n')

    def exchange(self, output):
        self.writeln(output)
        self._port.flush()
        return self.expect()

    def close(self):
        """restores the nodemcu to default baudrate and then closes the port"""
        try:
            self.writeln(UART_SETUP.format(baud=Uploader.BAUD))
            self._port.flush()
            self.clear_buffers()
        except serial.serialutil.SerialException:
            pass
        log.debug('closing port')
        self._port.close()

    def prepare(self):
        """
        This uploads the protocol functions nessecary to do binary
        chunked transfer
        """
        log.info('Preparing esp for transfer.')

        for fn in LUA_FUNCTIONS:
            d = self.exchange('print({0})'.format(fn))
            if d.find('function:') == -1:
                break
        else:
            log.debug('Found all required lua functions, no need to upload them')
            return True
            
        data = SAVE_LUA.format(baud=self._port.baudrate)
        ##change any \r\n to just \n and split on that
        lines = data.replace('\r', '').split('\n')

        #remove some unneccesary spaces to conserve some bytes
        for line in lines:
            line = line.strip().replace(', ', ',').replace(' = ', '=')

            if len(line) == 0:
                continue

            d = self.exchange(line)
            #do some basic test of the result
            if ('unexpected' in d) or ('stdin' in d) or len(d) > len(SAVE_LUA)+10:
                log.error('error in save_lua "%s"', d)
                return False
        return True

    def download_file(self, filename):
        chunk_size = 256
        bytes_read = 0
        data = ""
        while True:
            d = self.exchange(DOWNLOAD_FILE.format(filename=filename, bytes_read=bytes_read, chunk_size=chunk_size))
            cmd, size, tmp_data = d.split('\n', 2)
            data = data + tmp_data[0:chunk_size]
            bytes_read = bytes_read + chunk_size
            if bytes_read > int(size):
                break
        data = data[0:int(size)]
        return data

    def read_file(self, filename, destination=''):
        if not destination:
            destination = filename
        log.info('Transfering %s to %s', filename, destination)
        data = self.download_file(filename)
        with open(destination, 'w') as f:
            f.write(data)

    def write_file(self, path, destination='', verify='none'):
        filename = os.path.basename(path)
        if not destination:
            destination = filename
        log.info('Transfering %s as %s', path, destination)
        self.writeln("recv()")

        res = self.expect('C> ')
        if not res.endswith('C> '):
            log.error('Error waiting for esp "%s"', res)
            return
        log.debug('sending destination filename "%s"', destination)
        self.write(destination + '\x00', True)
        if not self.got_ack():
            log.error('did not ack destination filename')
            return

        f = open(path, 'rb')
        content = f.read()
        f.close()

        log.debug('sending %d bytes in %s', len(content), filename)
        pos = 0
        chunk_size = 128
        while pos < len(content):
            rest = len(content) - pos
            if rest > chunk_size:
                rest = chunk_size

            data = content[pos:pos+rest]
            if not self.write_chunk(data):
                d = self.expect()
                log.error('Bad chunk response "%s" %s', d, ':'.join(x.encode('hex') for x in d))
                return

            pos += chunk_size

        log.debug('sending zero block')
        #zero size block
        self.write_chunk('')

        if verify == 'standard':
            log.info('Verifying...')
            data = self.download_file(destination)
            if content != data:
                log.error('Verification failed.')
        elif verify == 'sha1':
            #Calculate SHA1 on remote file. Extract just hash from result
            data = self.exchange('shafile("'+destination+'")').splitlines()[1]
            log.info('Remote SHA1: %s', data)

            #Calculate hash of local data
            filehashhex = hashlib.sha1(content.encode()).hexdigest()
            log.info('Local SHA1: %s', filehashhex)
            if data != filehashhex:
                log.error('Verification failed.')

    def exec_file(self, path):
        filename = os.path.basename(path)
        log.info('Execute %s', filename)

        f = open(path, 'rt')

        res = '> '
        for line in f:
            line = line.rstrip('\r\n')
            retlines = (res + self.exchange(line)).splitlines()
            # Log all but the last line
            res = retlines.pop()
            for lin in retlines:
                log.info(lin)
        # last line
        log.info(res)
        f.close()

    def got_ack(self):
        log.debug('waiting for ack')
        res = self._port.read(1)
        log.debug('ack read %s', res.encode('hex'))
        return res == '\x06' #ACK


    def write_lines(self, data):
        lines = data.replace('\r', '').split('\n')

        for line in lines:
            self.exchange(line)

        return


    def write_chunk(self, chunk):
        log.debug('writing %d bytes chunk', len(chunk))
        data = '\x01' + chr(len(chunk)) + chunk
        if len(chunk) < 128:
            padding = 128 - len(chunk)
            log.debug('pad with %d characters', padding)
            data = data + (' ' * padding)
        log.debug("packet size %d", len(data))
        self.write(data)
        self._port.flush()
        return self.got_ack()


    def file_list(self):
        log.info('Listing files')
        res = self.exchange(LIST_FILES)
        log.info(res)
        return res

    def file_do(self, f):
        log.info('Executing '+f)
        res = self.exchange('dofile("'+f+'")')
        log.info(res)
        return res

    def file_format(self):
        log.info('Formating...')
        res = self.exchange('file.format()')
        if 'format done' not in res:
            log.error(res)
        else:
            log.info(res)
        return res

    def node_heap(self):
        log.info('Heap')
        res = self.exchange('print(node.heap())')
        log.info(res)
        return res

    def node_restart(self):
        log.info('Restart')
        res = self.exchange('node.restart()')
        log.info(res)
        return res

    def file_compile(self, path):
        log.info('Compile '+path)
        cmd = 'node.compile("%s")' % path
        res = self.exchange(cmd)
        log.info(res)
        return res

    def file_remove(self, path):
        log.info('Remove '+path)
        cmd = 'file.remove("%s")' % path
        res = self.exchange(cmd)
        log.info(res)
        return res

