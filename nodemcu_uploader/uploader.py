# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 Peter Magnusson <peter@kmpm.se>
"""Main functionality for nodemcu-uploader"""

# Not sure about it, because UnicodeEncodeError throws anyway
# from __future__ import unicode_literals


import time
import logging
import hashlib
import os
import errno
import serial

from . import validate
from .serialutils import default_port
from .exceptions import CommunicationTimeout, DeviceNotFoundException, \
    BadResponseException, VerificationError, NoAckException
from .utils import system, hexify, from_file, ENCODING
from .luacode import RECV_LUA, SEND_LUA, LUA_FUNCTIONS, \
    LIST_FILES, UART_SETUP, PRINT_FILE, INFO_GROUP, REMOVE_ALL_FILES


log = logging.getLogger(__name__)  # pylint: disable=C0103

__all__ = ['Uploader', 'default_port']

SYSTEM = system()


MINIMAL_TIMEOUT = 0.001
BLOCK_START = b'\x01'
NUL = b'\x00'
ACK = b'\x06'


class Uploader(object):
    """Uploader is the class for communicating with the nodemcu and
    that will allow various tasks like uploading files, formating the filesystem etc.
    """
    BAUD = 115200
    START_BAUD = 115200
    TIMEOUT = 5
    AUTOBAUD_TIME = 0.3
    PORT = default_port()

    def __init__(self, port=PORT, baud=BAUD, start_baud=START_BAUD, timeout=TIMEOUT, autobaud_time=AUTOBAUD_TIME):
        self._timeout = Uploader.TIMEOUT
        self.set_timeout(timeout)
        log.info('opening port %s with %s baud', port, start_baud)
        if port == 'loop://':
            self._port = serial.serial_for_url(port, start_baud, timeout=timeout)
        else:
            self._port = serial.Serial(port, start_baud, timeout=timeout)

        # black magic aka proxifying
        # self._port = wrap(self._port)

        self.start_baud = start_baud
        self.baud = baud
        self.autobaud_time = autobaud_time
        # Keeps things working, if following connections are made:
        # RTS = CH_PD (i.e reset)
        # DTR = GPIO0
        self._port.setRTS(False)
        self._port.setDTR(False)

        def __sync():
            """Get in sync with LUA (this assumes that NodeMCU gets reset by the previous two lines)"""
            log.debug('getting in sync with LUA')
            self.__clear_buffers()
            try:
                self.__writeln('UUUUUUUUUUUU')  # Send enough characters for auto-baud
                self.__clear_buffers()
                time.sleep(self.autobaud_time)  # Wait for autobaud timer to expire
                self.__exchange(';')  # Get a defined state
                self.__writeln('print("%sync%");')
                self.__expect('%sync%\r\n> ')
            except CommunicationTimeout:
                raise DeviceNotFoundException('Device not found or wrong port')

        __sync()

        if baud != start_baud:
            self.__set_baudrate(baud)

            # Get in sync again
            __sync()

        self.line_number = 0

    def __set_baudrate(self, baud):
        """setting baudrate if supported"""
        log.info('Changing communication to %s baud', baud)
        self.__writeln(UART_SETUP.format(baud=baud))
        # Wait for the string to be sent before switching baud
        time.sleep(0.1)
        try:
            self._port.setBaudrate(baud)
        except AttributeError:
            # pySerial 2.7
            self._port.baudrate = baud

    def set_timeout(self, timeout):
        """Set the timeout for the communication with the device."""
        timeout = int(timeout)  # will raise on Error
        self._timeout = timeout == 0 and 999999 or timeout

    def __clear_buffers(self):
        """Clears the input and output buffers"""
        try:
            self._port.reset_input_buffer()
            self._port.reset_output_buffer()
        except AttributeError:
            #  pySerial 2.
            self._port.flushInput()
            self._port.flushOutput()

    def __expect(self, exp='> ', timeout=None):
        """will wait for exp to be returned from nodemcu or timeout.
        Will use utils.ENCODING for encoding if not bytes.
        """
        timeout_before = self._port.timeout
        timeout = timeout or self._timeout
        # do NOT set timeout on Windows
        if SYSTEM != 'Windows':
            # Checking for new data every 100us is fast enough
            if self._port.timeout != MINIMAL_TIMEOUT:
                self._port.timeout = MINIMAL_TIMEOUT

        if not isinstance(exp, bytes):
            exp = bytes(exp, ENCODING)

        end = time.time() + timeout

        # Finish as soon as either exp matches or we run out of time (work like dump, but faster on success)
        data = bytes()
        while not data.endswith(exp) and time.time() <= end:
            data += self._port.read()
            # msg = data.decode(ENCODING, 'ignore')

        now = time.time()
        log.debug('expect returned: `{0}`. wants: {1}'.format(data, exp))
        if now > end:
            raise CommunicationTimeout('Timeout waiting for data', data)

        if not data.endswith(exp) and len(exp) > 0:
            raise BadResponseException('Bad response.', exp, data)

        if SYSTEM != 'Windows':
            self._port.timeout = timeout_before

        return str(data, ENCODING)

    def __write(self, output, binary=False):
        """write data on the nodemcu port. Strings will be converted to bytes using utils.ENCODING.
        If 'binary' is True the debug log will show the intended output as hex, otherwise as string"""
        if not binary:
            log.debug('write: %s', output)
        else:
            log.debug('write binary: %s', hexify(output))
        if isinstance(output, str):
            output = bytes(output, ENCODING)

        self._port.write(output)
        self._port.flush()

    def __writeln(self, output):
        """write, with linefeed"""
        self.__write(output + '\n')

    def __exchange(self, output, timeout=None):
        """Write output to the port and wait for response
        Expects a str as input"""
        if not isinstance(output, str):
            raise TypeError("output should be a str")
        self.__writeln(output)
        self._port.flush()
        return self.__expect(timeout=timeout or self._timeout)

    def close(self):
        """restores the nodemcu to default baudrate and then closes the port"""
        try:
            if self.baud != self.start_baud:
                self.__set_baudrate(self.start_baud)
            self._port.flush()
            self.__clear_buffers()
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

        for func in LUA_FUNCTIONS:
            detected = self.__exchange('print({0})'.format(func))
            if detected.find('function:') == -1:
                break
        else:
            log.info('Preparation already done. Not adding functions again.')
            return True
        functions = RECV_LUA + '\n' + SEND_LUA
        data = functions.format(baud=self._port.baudrate)
        # change any \r\n to just \n and split on that
        lines = data.replace('\r', '').split('\n')
        # remove some unneccesary spaces to conserve some bytes
        # TODO: a good minifier for lua
        for line in lines:
            line = line.strip().replace(', ', ',').replace(' = ', '=')

            if len(line) == 0:
                continue

            resp = self.__exchange(line)
            # do some basic test of the result
            if ('unexpected' in resp) or ('stdin' in resp) or len(resp) > len(functions)+10:
                log.error('error when preparing "%s"', resp)
                return False
        return True

    def download_file(self, filename):
        """Download a file from device to RAM
        Return 'bytes' of the full content
        """
        validate.remotePath(filename)
        res = self.__exchange('send("{filename}")'.format(filename=filename))
        if ('unexpected' in res) or ('stdin' in res):
            log.error('Unexpected error downloading file: %s', res)
            raise Exception('Unexpected error downloading file')

        # tell device we are ready to receive
        self.__write('C')
        # we should get a NUL terminated filename to start with
        sent_filename = self.__expect(NUL).strip()
        log.info('receiveing ' + sent_filename)

        # ACK to start download
        self.__write(ACK, True)
        buf = bytes()

        data = bytes()
        chunk, buf = self.__read_chunk(buf)
        # read chunks until we get an empty which is the end
        while len(chunk) > 0:
            self.__write(ACK, True)
            data = data + chunk
            chunk, buf = self.__read_chunk(buf)
        return data

    def read_file(self, filename, destination=''):
        """Downloading data from remote device into local file using the transfer protocol.
        """
        if not destination:
            destination = filename
        log.info('Transferring %s to %s', filename, destination)
        data = self.download_file(filename)

        # Just in case, the filename may contain folder, so create it if needed.
        log.info(destination)
        dirpath1 = os.path.dirname(destination)
        if len(dirpath1) > 0 and not os.path.exists(dirpath1):
            try:
                os.makedirs(os.path.dirname(destination))
            except OSError as e:  # Guard against race condition
                if e.errno != errno.EEXIST:
                    raise
        with open(destination, 'wb') as fil:
            try:
                fil.write(data)
            except Exception as e:
                log.error("Unexpected error writing file", e)
                raise

    def write_file(self, path, destination='', verify='none'):
        """Uploads a file to the remote device using the transfer protocol"""
        filename = os.path.basename(path)
        if not destination:
            destination = filename

        validate.remotePath(destination)
        log.info('Transferring %s as %s', path, destination)
        self.__writeln("recv()")

        res = self.__expect('C> ')
        if not res.endswith('C> '):
            log.error('Error waiting for esp "%s"', res)
            raise CommunicationTimeout('Error waiting for device to start receiving', res)

        log.debug('sending destination filename "%s"', destination)
        self.__write(destination + '\x00', True)
        if not self.__got_ack():
            log.error('did not ack destination filename')
            raise NoAckException('Device did not ACK destination filename')

        content = from_file(path)

        log.debug('sending %d bytes in %s', len(content), filename)
        pos = 0
        chunk_size = 128
        while pos < len(content):
            rest = len(content) - pos
            if rest > chunk_size:
                rest = chunk_size

            data = content[pos:pos+rest]
            if not self.__write_chunk(data):
                resp = self.__expect()
                log.error('Bad chunk response "%s" %s', resp, hexify(resp))
                raise BadResponseException('Bad chunk response', ACK, resp)

            pos += chunk_size

        log.debug('sending zero block')
        # zero size block
        self.__write_chunk()
        if verify != 'none':
            self.verify_file(path, destination, verify)

    def verify_file(self, local, remote, verify='none'):
        """Tries to verify if local has same checksum as remote.
            Valid options for verify is 'raw', 'sha1' or 'none'
        """
        # get the local file contents
        self.__writeln(';')
        self.__expect('> ')
        content = from_file(local)
        log.info('Verifying using %s...' % verify)
        if verify == 'raw':
            data = self.download_file(remote)
            if content != data:
                log.error('Raw verification failed.')
                raise VerificationError('Verification failed.')
            else:
                log.info('Verification successful. Contents are identical.')
        elif verify == 'sha1':
            # Calculate SHA1 on remote file. Extract just hash from result
            data = self.__exchange('shafile("'+remote+'")').splitlines()[1]
            log.info('Remote SHA1: %s', data)

            # Calculate hash of local data
            filehashhex = hashlib.sha1(content).hexdigest()
            log.info('Local SHA1: %s', filehashhex)
            if data != filehashhex:
                log.error('SHA1 verification failed.')
                raise VerificationError('SHA1 Verification failed.')
            else:
                log.info('Verification successful. Checksums match')

        elif verify != 'none':
            raise Exception(verify + ' is not a valid verification method.')

    def exec_file(self, path):
        """execute the lines in the local file 'path'"""
        filename = os.path.basename(path)
        log.info('Execute %s', filename)

        content = from_file(path).replace('\r', '').split('\n')

        res = '> '
        for line in content:
            line = line.rstrip('\n')
            retlines = (res + self.__exchange(line)).splitlines()
            # Log all but the last line
            res = retlines.pop()
            for lin in retlines:
                log.info(lin)
        # last line
        log.info(res)

    def __got_ack(self):
        """Returns true if ACK is received"""
        log.debug('waiting for ack')
        res = self._port.read(1)
        acked = res == ACK
        log.debug('ack read %s, comparing with %s. %s', hexify(res), hexify(ACK), acked)
        return acked

    def write_lines(self, data):
        """write lines, one by one, separated by \n to device"""
        lines = data.replace('\r', '').split('\n')
        for line in lines:
            self.__exchange(line)

    def __write_chunk(self, chunk=bytes()):
        """formats and sends a chunk of data to the device according to transfer protocol.
        Return result of ack check"""
        if not isinstance(chunk, bytes):
            raise TypeError()
        log.debug('writing %d bytes chunk', len(chunk))
        data = BLOCK_START + bytes([len(chunk)]) + chunk
        if len(chunk) < 128:
            padding = 128 - len(chunk)
            log.debug('pad with %d characters', padding)
            data = data + (b'\x00' * padding)

        log.debug("packet size %d", len(data))
        self.__write(data)
        self._port.flush()
        return self.__got_ack()

    def __read_chunk(self, buf):
        """Read a chunk of data"""
        log.debug('reading chunk')
        timeout_before = self._port.timeout
        if SYSTEM != 'Windows':
            # Checking for new data every 100us is fast enough
            if self._port.timeout != MINIMAL_TIMEOUT:
                self._port.timeout = MINIMAL_TIMEOUT

        end = time.time() + timeout_before
        if not isinstance(buf, bytes):
            raise Exception('Buffer is not instance of "bytes"')
        while len(buf) < 130 and time.time() <= end:
            r = self._port.read()
            if not isinstance(r, bytes):
                raise Exception('r is not instance of "bytes" is {t}'.format(t=type(r).__name__))
            buf = buf + r

        if buf[0] != ord(BLOCK_START) or len(buf) < 130:
            log.debug('buffer binary: %s ', hexify(buf))
            raise Exception('Bad blocksize or start byte')
        # else:
        #     log.debug('buf binary: %s', hexify(buf))

        if SYSTEM != 'Windows':
            self._port.timeout = timeout_before

        chunk_size = buf[1]
        data = buf[2:chunk_size+2]
        buf = buf[130:]
        return (data, buf)

    def file_list(self):
        """list files on the device"""
        log.info('Listing files')
        res = self.__exchange(LIST_FILES)
        res = res.split('\r\n')
        # skip first and last lines
        res = res[1:-1]
        files = []
        for line in res:
            files.append(line.split('\t'))
        return files

    def file_do(self, filename):
        """Execute a file on the device using 'do'"""
        log.info('Executing '+filename)
        res = self.__exchange('dofile("'+filename+'")')
        log.info(res)
        return res

    def file_format(self):
        """Formats device filesystem"""
        log.info('Formating, can take minutes depending on flash size...')
        res = self.__exchange('file.format()', timeout=300)
        if 'format done' not in res:
            log.error(res)
        else:
            log.info(res)
        return res

    def file_print(self, filename):
        """Prints a file on the device to console"""
        log.info('Printing ' + filename)
        res = self.__exchange(PRINT_FILE.format(filename=filename))
        log.info(res)
        return res

    def file_remove_all(self):
        log.info('Removing all files!!!')
        res = self.__exchange(REMOVE_ALL_FILES)
        log.info(res)
        return res

    def node_heap(self):
        """Show device heap size"""
        log.info('Heap')
        res = self.__exchange('print(node.heap())')
        log.info(res)
        return int(res.split('\r\n')[1])

    def node_restart(self):
        """Restarts device"""
        log.info('Restart')
        res = self.__exchange('node.restart()')
        log.info(res)
        return res

    def node_info(self):
        """Node info"""
        log.info('Node info')
        res = self.node_info_group('hw')
        res += self.node_info_group('sw_version')
        res += self.node_info_group('build_config')
        return res

    def node_info_group(self, group):
        log.info('Node info %s', group)
        res = self.__exchange(INFO_GROUP.format(group=group))
        log.info(res)
        return res

    def file_compile(self, path):
        """Compiles a file specified by path on the device"""
        log.info('Compile '+path)
        cmd = 'node.compile("%s")' % path
        res = self.__exchange(cmd)
        log.info(res)
        return res

    def file_remove(self, path):
        """Removes a file on the device"""
        log.info('Remove '+path)
        cmd = 'file.remove("%s")' % path
        res = self.__exchange(cmd)
        log.info(res)
        return res

    def backup(self, path):
        """Backup all files from the device"""
        log.info('Backing up in '+path)
        # List file to backup
        files = self.file_list()
        # then download each of then
        self.prepare()
        for f in files:
            self.read_file(f[0], os.path.join(path, f[0]))
