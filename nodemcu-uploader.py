# For NodeMcu version 0.9.4 build 2014-12-30 and newer.

import os
import serial
import sys
import argparse
import time

def minify(script):
    return ' '.join([line.strip() for line in script.split('\n')])

def log(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()

save_lua = \
r"""
function recv_block(d)
  if string.byte(d, 1) == 1 then
    size = string.byte(d, 2)
    if size > 0 then
      file.write(string.sub(d, 3, 3+size))
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
    TIMEOUT = 1

    def __init__(self, port = 0, baud = BAUD):
        self._port = serial.Serial(port, baud, timeout=Uploader.TIMEOUT)
        self.line_number = 0
        self.verbose = False
        self.debug = False


    def set_verbose(self):
        self.verbose = True


    def set_debug(self):
        self.verbose = True
        self.debug = True


    def dump(self, timeout=TIMEOUT):
        t = self._port.timeout
        if self._port.timeout != timeout:
            self._port.timeout = timeout
        n = self._port.read()
        data = ''
        while n != '':
            data += n
            n = self._port.read()
    
        self._port.timeout = t
        return data


    def prepare(self):
        if self.verbose: log('Preparing esp for transfer.')
        self.write_lines(save_lua.replace('9600', '%d' % self._port.baudrate))
        self._port.write('\r\n')
        if self.verbose: log('.')
        d = self.dump(0.1)
        if 'unexpected' in d or len(d) > len(save_lua)+10:
            print 'error in save_lua', d
            return
        if self.verbose: print('.done')


    def write(self, path):
        filename = os.path.basename(path)
        if self.verbose: log('Transfering %s' % filename)
        self.dump()
        self._port.write(r"recv()" + '\n')

        count = 0
        while not 'C' in self.dump(0.2):
            time.sleep(1)
            count += 1
            if count > 5:
                print 'Error waiting for esp', self.dump()
                return
        self.dump(0.5)
        if self.verbose: log('.')
        if self.debug: print 'sending filename', filename
        self._port.write(filename + '\x00')

        if not self.got_ack():
            print 'did not ack filename', self.dump()
            return
        if self.verbose: log('.')
        f = open( path, 'rt' ); content = f.read(); f.close()
        if self.debug: print 'sending %d bytes in %s' % (len(content), filename)
        pos = 0
        chunk_size = 128
        error = False
        while pos < len(content):
            data = content[pos: pos+chunk_size]
            if not self.write_chunk(data):
                error = True
                print 'Bad send'
                d = self.dump()
                print d
                print ':'.join(x.encode('hex') for x in d)
                break

            pos += chunk_size
            if pos + chunk_size > len(content):
                chunk_size = len(content) - pos
            
        if self.verbose: log('.')
        if self.debug: print 'sending zero block'
        if not error:
            #zero size block
            self.write_chunk('')
        if self.verbose: print 'done'

    
    def got_ack(self):
        if self.debug: print 'waiting for ack'
        r = self._port.read(1)
        return r == '\x06' #ACK


    def write_lines(self, data):
        lines = data.replace('\r', '').split('\n')

        for line in lines:
            self._port.write(line + '\r\n')
            d = self.dump(0.1)
            if self.debug: log(d)
        return


    def write_chunk(self, chunk):
        if self.debug: print 'writing %d bytes chunk' % len(chunk)
        data = '\x01' + chr(len(chunk)) + chunk
        if len(chunk) < 128:
            padding = 128 - len(chunk)
            if self.debug: print 'pad with %d characters' % padding
            data = data + (' ' * padding)
        if self.debug: print "packet size %d" % len(data)
        self._port.write(data)

        return self.got_ack()
        

   

def arg_auto_int(x):
    return int(x, 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'nodeMCU Lua uploader', prog = 'uploader')
    parser.add_argument(
            '--port', '-p',
            help = 'Serial port device',
            default = Uploader.PORT)

    parser.add_argument(
            '--baud', '-b',
            help = 'Serial port baud rate',
            type = arg_auto_int,
            default = Uploader.BAUD)

    parser.add_argument(
            '--verbose', '-v',
            help = 'verbouse output',
            action = 'store_true',
            default = False)

    parser.add_argument(
            '--debug', '-d',
            help = 'debug output',
            action = 'store_true',
            default = False)

    parser.add_argument('filename',  nargs='+', help = 'Lua file to upload')


    args = parser.parse_args()
    
    uploader = Uploader(args.port, args.baud)
    if args.verbose:
        uploader.set_verbose()
    if args.debug:
        uploader.set_debug()
    
    uploader.prepare()    
    for f in args.filename:
        uploader.write(f)
    if args.verbose: 
        print 'All done!' 
