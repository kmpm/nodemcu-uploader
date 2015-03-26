#!/usr/bin/env python
# Copyright (C) 2015 Peter Magnusson

# For NodeMCU version 0.9.4 build 2014-12-30 and newer.

import os
import serial
import sys
import argparse
import time
import logging

log = logging.getLogger(__name__)

def minify(script):
    return ' '.join([line.strip() for line in script.split('\n')])

save_lua = \
r"""
function recv_block(d)
  if string.byte(d, 1) == 1 then
    size = string.byte(d, 2)
    if size > 0 then
      file.write(string.sub(d, 3, 3+size-1))
      uart.write(0,'\006')
    else
      uart.write(0,'\006')
      file.close()
      uart.on('data')
      uart.setup(0,9600,8,0,1,1)
    end
  else
    uart.write(0, '\021' .. d)
    uart.setup(0,9600,8,0,1,1)
    uart.on('data')
  end
end
function recv_name(d)
  d = string.gsub(d, '\000', '')
  file.remove(d)
  file.open(d, 'w')
  uart.on('data', 130, recv_block, 0)
  uart.write(0, '\006')
end
function recv()
  uart.setup(0,9600,8,0,1,0)
  uart.on('data', '\000', recv_name, 0)
  uart.write(0, 'C')
end
"""
#save_lua = minify(save_lua)
#save_lua = ' '.join([line.strip().replace(', ', ',') for line in save_lua.split('\n')])

CHUNK_END = '\v'
CHUNK_REPLY = '\v'

class Uploader:
    BAUD = 9600
    PORT = '/dev/ttyUSB0'
    TIMEOUT = 5

    def expect(self, exp='> ', timeout=TIMEOUT):
        t = self._port.timeout

        # Checking for new data every 100us is fast enough
        lt = 0.0001
        if self._port.timeout != lt:
            self._port.timeout = lt

        end = time.time() + timeout

        # Finish as soon as either exp matches or we run out of time (work like dump, but faster on success)
        data = ''
        while not data.endswith(exp) and time.time() <= end:
            data += self._port.read()

        self._port.timeout = t
        log.debug('expect return: %s', data)
        return data

    def write(self, output, binary=False):
        if not binary:
            log.debug('write: %s', output)
        else:
            log.debug('write binary: %s' % ':'.join(x.encode('hex') for x in output))
        self._port.write(output)
        self._port.flush()

    def writeln(self, output):
        self.write(output + '\n')

    def exchange(self, output):
        self.writeln(output)
        return self.expect()

    def __init__(self, port = 0, baud = BAUD):
        self._port = serial.Serial(port, Uploader.BAUD, timeout=Uploader.TIMEOUT)

        # Keeps things working, if following conections are made:
        ## RTS = CH_PD (i.e reset)
        ## DTR = GPIO0
        self._port.setRTS(False)
        self._port.setDTR(False)

        # Get in sync with LUA (this assumes that NodeMCU gets reset by the previous two lines)
        self.expect('NodeMCU ')
        self.expect()
        self.exchange('')

        if baud != Uploader.BAUD:
            log.info('Changing communication to %s baud', baud)
            self.exchange('uart.setup(0,%s,8,0,1,1)' % baud)
            self._port.baudrate = baud

        self.line_number = 0

    def close(self):
        self.writeln('uart.setup(0,%s,8,0,1,1)' % Uploader.BAUD)
        self._port.close()

    def prepare(self):
        log.info('Preparing esp for transfer.')

        data = save_lua.replace('9600', '%d' % self._port.baudrate)
        lines = data.replace('\r', '').split('\n')

        for line in lines:
            d = self.exchange(line)

            if 'unexpected' in d or len(d) > len(save_lua)+10:
                log.error('error in save_lua "%s"' % d)
                return

    def download_file(self, filename):
        d = self.exchange(r"file.open('" + filename + r"') print(file.seek('end', 0)) file.seek('set', 0) uart.write(0, file.read()) file.close()")
        cmd, size, data = d.split('\n', 2)
        data = data[0:int(size)]
        return data

    def read_file(self, filename, destination = ''):
        if not destination:
            destination = filename
        log.info('Transfering %s to %s' %(filename, destination))
        data = self.download_file(filename)
        with open(destination, 'w') as f:
            f.write(data)

    def write_file(self, path, destination = '', verify = False):
        filename = os.path.basename(path)
        if not destination:
            destination = filename
        log.info('Transfering %s as %s' %(filename, destination))
        self.writeln("recv()")

        r = self.expect('C> ')
        if not r.endswith('C> '):
            log.error('Error waiting for esp "%s"' % r)
            return
        log.debug('sending destination filename "%s"', destination)
        self.write(destination + '\x00', True)
        if not self.got_ack():
            log.error('did not ack destination filename')
            return

        f = open( path, 'rt' ); content = f.read(); f.close()
        log.debug('sending %d bytes in %s' % (len(content), filename))
        pos = 0
        chunk_size = 128
        error = False
        while pos < len(content):
            rest = len(content) - pos
            if rest > chunk_size:
                rest = chunk_size

            data = content[pos:pos+rest]
            if not self.write_chunk(data):
                d = self.expect()
                log.error('Bad chunk response "%s" %s' % (d, ':'.join(x.encode('hex') for x in d)))
                return

            pos += chunk_size

        log.debug('sending zero block')
        #zero size block
        self.write_chunk('')

        if verify:
            log.info('Verifying...')
            data = self.download_file(destination)
            if content != data:
                log.error('Verification failed.')

    def got_ack(self):
        log.debug('waiting for ack')
        r = self._port.read(1)
        log.debug('ack read %s', r.encode('hex'))
        return r == '\x06' #ACK


    def write_lines(self, data):
        lines = data.replace('\r', '').split('\n')

        for line in lines:
            self.exchange(line)

        return


    def write_chunk(self, chunk):
        log.debug('writing %d bytes chunk' % len(chunk))
        data = '\x01' + chr(len(chunk)) + chunk
        if len(chunk) < 128:
            padding = 128 - len(chunk)
            log.debug('pad with %d characters' % padding)
            data = data + (' ' * padding)
        log.debug("packet size %d" % len(data))
        self.write(data)

        return self.got_ack()


    def file_list(self):
        log.info('Listing files')
        r = self.exchange('for key,value in pairs(file.list()) do print(key,value) end')
        log.info(r)
        return r

    def file_do(self, f):
        log.info('Executing '+f)
        r = self.exchange('dofile("'+f+'")')
        log.info(r)
        return r

    def file_format(self):
        log.info('Formating...')
        r = self.exchange('file.format()')
        if 'format done' not in r:
            log.error(r)
        else:
            log.info(r)
        return r

    def node_heap(self):
        log.info('Heap')
        r = self.exchange('print(node.heap())')
        log.info(r)
        return r

    def node_restart(self):
        log.info('Restart')
        r = self.exchange('node.restart()')
        log.info(r)
        return r
    
    def file_compile(self, path):
        log.info('Compile '+path)
        cmd = 'node.compile("%s")' % path
        r = self.exchange(cmd)
        log.info(r)
        return r
    
    def file_remove(self, path):
        log.info('Remove '+path)
        cmd = 'file.remove("%s")' % path
        r = self.exchange(cmd)
        log.info(r)
        return r


def arg_auto_int(x):
    return int(x, 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'NodeMCU Lua file uploader', prog = 'nodemcu-uploader')
    parser.add_argument(
            '--verbose',
            help = 'verbose output',
            action = 'store_true',
            default = False)

    parser.add_argument(
            '--port', '-p',
            help = 'Serial port device',
            default = Uploader.PORT)

    parser.add_argument(
            '--baud', '-b',
            help = 'Serial port baudrate',
            type = arg_auto_int,
            default = Uploader.BAUD)

    subparsers = parser.add_subparsers(
        dest='operation',
        help = 'Run nodemcu-uploader {command} -h for additional help')

    upload_parser = subparsers.add_parser(
            'upload',
            help = 'Path to one or more files to be uploaded. Destination name will be the same as the file name.')

    # upload_parser.add_argument(
    #         '--filename', '-f',
    #         help = 'File to upload. You can specify this option multiple times.',
    #         action='append')

    # upload_parser.add_argument(
    #         '--destination', '-d',
    #         help = 'Name to be used when saving in NodeMCU. You should specify one per file.',
    #         action='append')

    upload_parser.add_argument('filename', nargs='+', help = 'Lua file to upload. Use colon to give alternate destination.')

    upload_parser.add_argument(
            '--compile', '-c',
            help = 'If file should be uploaded as compiled',
            action='store_true',
            default=False
            )
    
    upload_parser.add_argument(
            '--verify', '-v',
            help = 'To verify the uploaded data.',
            action='store_true',
            default=False
            )
    
    upload_parser.add_argument(
            '--restart', '-r',
            help = 'If esp should be restarted',
            action='store_true',
            default=False
    )

    download_parser = subparsers.add_parser(
            'download',
            help = 'Path to one or more files to be downloaded. Destination name will be the same as the file name.')

    # download_parser.add_argument(
    #         '--filename', '-f',
    #         help = 'File to download. You can specify this option multiple times.',
    #         action='append')

    # download_parser.add_argument(
    #         '--destination', '-d',
    #         help = 'Name to be used when saving in NodeMCU. You should specify one per file.',
    #         action='append')

    download_parser.add_argument('filename', nargs='+', help = 'Lua file to download. Use colon to give alternate destination.')


    file_parser = subparsers.add_parser(
        'file',
        help = 'File functions')

    file_parser.add_argument('cmd', choices=('list', 'do', 'format'))
    file_parser.add_argument('filename', nargs='*', help = 'Lua file to run.')

    node_parse = subparsers.add_parser(
        'node', 
        help = 'Node functions')

    node_parse.add_argument('ncmd', choices=('heap', 'restart'))


    args = parser.parse_args()

    formatter = logging.Formatter('%(message)s')
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    if args.verbose:
        log.setLevel(logging.DEBUG)

    uploader = Uploader(args.port, args.baud)

    if args.operation == 'upload' or args.operation == 'download':
        sources = args.filename
        destinations = []
        for i in range(0, len(sources)):
            sd = sources[i].split(':')
            if len(sd) == 2:
                destinations.append(sd[1])
                sources[i]=sd[0]
            else:
                destinations.append(sd[0])

        if args.operation == 'upload':
            if len(destinations) == len(sources):
                uploader.prepare()
                for f, d in zip(sources, destinations):
                    uploader.write_file(f, d, args.verify)
                    if args.compile:
                        uploader.file_compile(d)
                        uploader.file_remove(d)
            else:
                raise Exception('You must specify a destination filename for each file you want to upload.')

            if args.restart:
                uploader.node_restart()
            log.info('All done!')

        if args.operation == 'download':
            if len(destinations) == len(sources):
                for f, d in zip(sources, destinations):
                    uploader.read_file(f, d)
            else:
                raise Exception('You must specify a destination filename for each file you want to download.')
            log.info('All done!')

    elif args.operation == 'file':
        if args.cmd == 'list':
            uploader.file_list()
        if args.cmd == 'do':
            for f in args.filename:
                uploader.file_do(f)
        elif args.cmd == 'format':
            uploader.file_format()
    
    elif args.operation == 'node':
        if args.ncmd == 'heap':
            uploader.node_heap()
        elif args.ncmd == 'restart':
            uploader.node_restart()

    uploader.close()
