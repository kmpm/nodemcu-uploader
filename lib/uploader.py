#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>

import time
import logging
import hashlib
import os
import serial

from .exceptions import CommunicationTimeout, DeviceNotFoundException, BadResponseException
from .utils import default_port, system
from .luacode import DOWNLOAD_FILE, RECV_LUA, SEND_LUA, LUA_FUNCTIONS, LIST_FILES, UART_SETUP, PRINT_FILE

log = logging.getLogger(__name__)

__all__ = ['Uploader', 'default_port']

SYSTEM = system()

BLOCK_START='\x01';
NUL = '\x00';
ACK = '\x06';

class Uploader(object):
    """Uploader is the class for communicating with the nodemcu and
    that will allow various tasks like uploading files, formating the filesystem etc.
    """
    BAUD = 115200
    START_BAUD = 9600
    TIMEOUT = 5
    PORT = default_port()

    def __init__(self, port=PORT, baud=BAUD, start_baud=START_BAUD):
        log.info('opening port %s with %s baud', port, start_baud)
        if port == 'loop://':
            self._port = serial.serial_for_url(port, start_baud, timeout=Uploader.TIMEOUT)
        else:
            self._port = serial.Serial(port, start_baud, timeout=Uploader.TIMEOUT)

        self.start_baud = start_baud
        self.baud = baud
        # Keeps things working, if following conections are made:
        ## RTS = CH_PD (i.e reset)
        ## DTR = GPIO0
        self._port.setRTS(False)
        self._port.setDTR(False)

        def sync():
            # Get in sync with LUA (this assumes that NodeMCU gets reset by the previous two lines)
            log.debug('getting in sync with LUA');
            self.clear_buffers()
            try:
                self.exchange(';') # Get a defined state
                self.writeln('print("%sync%");')
                self.expect('%sync%\r\n> ')
            except CommunicationTimeout:
                raise DeviceNotFoundException('Device not found or wrong port')

        sync()

        if baud != start_baud:
            self.set_baudrate(baud)

            # Get in sync again
            sync()

        self.line_number = 0

    def set_baudrate(self, baud):
        log.info('Changing communication to %s baud', baud)
        self.writeln(UART_SETUP.format(baud=baud))
        # Wait for the string to be sent before switching baud
        time.sleep(0.1)
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
        #do NOT set timeout on Windows
        if SYSTEM != 'Windows':
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

        log.debug('expect returned: `{0}`'.format(data))
        if time.time() > end:
            raise CommunicationTimeout('Timeout waiting for data', data)

        if not data.endswith(exp) and len(exp) > 0:
            raise BadResponseException('Bad response.', exp, data)

        if SYSTEM != 'Windows':
            self._port.timeout = timer

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

    def exchange(self, output, timeout=TIMEOUT):
        self.writeln(output)
        self._port.flush()
        return self.expect(timeout=timeout)


    def close(self):
        """restores the nodemcu to default baudrate and then closes the port"""
        try:
            if self.baud != self.start_baud:
                self.set_baudrate(self.start_baud)
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
            log.info('Preparation already done. Not adding functions again.')
            return True
        functions = RECV_LUA + '\n' + SEND_LUA
        data = functions.format(baud=self._port.baudrate)
        ##change any \r\n to just \n and split on that
        lines = data.replace('\r', '').split('\n')

        #remove some unneccesary spaces to conserve some bytes
        for line in lines:
            line = line.strip().replace(', ', ',').replace(' = ', '=')

            if len(line) == 0:
                continue

            d = self.exchange(line)
            #do some basic test of the result
            if ('unexpected' in d) or ('stdin' in d) or len(d) > len(functions)+10:
                log.error('error when preparing "%s"', d)
                return False
        return True

    def download_file(self, filename):
        res = self.exchange('send("{filename}")'.format(filename=filename))
        if ('unexpected' in res) or ('stdin' in res):
            log.error('Unexpected error downloading file', res)
            raise Exception('Unexpected error downloading file')

        #tell device we are ready to receive
        self.write('C')
        #we should get a NUL terminated filename to start with
        sent_filename = self.expect(NUL).strip()
        log.info('receiveing ' + sent_filename)

        #ACK to start download
        self.write(ACK, True);
        buffer = ''
        data = ''
        chunk, buffer = self.read_chunk(buffer)
        #read chunks until we get an empty which is the end
        while chunk != '':
            self.write(ACK,True);
            data = data + chunk
            chunk, buffer = self.read_chunk(buffer)
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

        if verify == 'raw':
            log.info('Verifying...')
            data = self.download_file(destination)
            if content != data:
                log.error('Verification failed.')
            else:
                log.info('Verification successfull. Contents are identical.')
        elif verify == 'sha1':
            #Calculate SHA1 on remote file. Extract just hash from result
            data = self.exchange('shafile("'+destination+'")').splitlines()[1]
            log.info('Remote SHA1: %s', data)

            #Calculate hash of local data
            filehashhex = hashlib.sha1(content.encode()).hexdigest()
            log.info('Local SHA1: %s', filehashhex)
            if data != filehashhex:
                log.error('Verification failed.')
            else:
                log.info('Verification successfull. Checksums match')

        elif verify != 'none':
            raise Exception(verify + ' is not a valid verification method.')


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
        data = BLOCK_START + chr(len(chunk)) + chunk
        if len(chunk) < 128:
            padding = 128 - len(chunk)
            log.debug('pad with %d characters', padding)
            data = data + (' ' * padding)
        log.debug("packet size %d", len(data))
        self.write(data)
        self._port.flush()
        return self.got_ack()


    def read_chunk(self, buffer):
        log.debug('reading chunk')
        timeout = self._port.timeout
        if SYSTEM != 'Windows':
            timer = self._port.timeout
            # Checking for new data every 100us is fast enough
            lt = 0.0001
            if self._port.timeout != lt:
                self._port.timeout = lt

        end = time.time() + timeout

        while len(buffer) < 130 and time.time() <= end:
            buffer = buffer + self._port.read()

        if buffer[0] != BLOCK_START or len(buffer) < 130:
            print 'buffer size:', len(buffer)
            log.debug('buffer binary: ', ':'.join(x.encode('hex') for x in buffer))
            raise Exception('Bad blocksize or start byte')

        chunk_size = ord(buffer[1])
        data = buffer[2:chunk_size+2]
        buffer = buffer[130:]
        return (data, buffer)


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
        log.info('Formating, can take up to 1 minute...')
        res = self.exchange('file.format()', timeout=60)
        if 'format done' not in res:
            log.error(res)
        else:
            log.info(res)
        return res

    def file_print(self, f):
        log.info('Printing ' + f)
        res = self.exchange(PRINT_FILE.format(filename=f))
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

