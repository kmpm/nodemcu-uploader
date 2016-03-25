# -*- coding: utf-8 -*-
"""This module contains all the LUA code that needs to be on the device
to perform whats needed. They will be uploaded if they doesn't exist"""

# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
# pylint: disable=C0301


LUA_FUNCTIONS = ['recv_block', 'recv_name', 'recv', 'shafile', 'send_block', 'send_file', 'send']

DOWNLOAD_FILE = "file.open('{filename}') print(file.seek('end', 0)) file.seek('set', {bytes_read}) uart.write(0, file.read({chunk_size}))file.close()"

PRINT_FILE = "file.open('{filename}') print('---{filename}---') print(file.read()) file.close() print('---')"

LIST_FILES = 'for key,value in pairs(file.list()) do print(key,value) end'
#NUL = \000, ACK = \006
RECV_LUA = \
r"""
function recv_block(d)
  if string.byte(d, 1) == 1 then
    size = string.byte(d, 2)
    uart.write(0,'\006')
    if size > 0 then
      file.write(string.sub(d, 3, 3+size-1))
    else
      file.close()
      uart.on('data')
    end
  else
    uart.write(0, '\021' .. d)
    uart.on('data')
  end
end
function recv_name(d) d = d:gsub('%z.*', '') file.remove(d) file.open(d, 'w') uart.on('data', 130, recv_block, 0) uart.write(0, '\006') end
function recv() uart.on('data', '\000', recv_name, 0) uart.write(0, 'C') end
function shafile(f) print(crypto.toHex(crypto.fhash('sha1', f))) end
"""

SEND_LUA = \
r"""
function send_block(d) l = string.len(d) uart.write(0, '\001' .. string.char(l) .. d .. string.rep('#', 128 - l)) return l end
function send_file(f) file.open(f) s=file.seek('end', 0) p=0 uart.on('data', 1, function(data)
if data == '\006' and p<s then file.seek('set',p) p=p+send_block(file.read(128)) else
send_block('') file.close() uart.on('data') print('interrupted') end end, 0) uart.write(0, f .. '\000')
end
function send(f) uart.on('data', 1, function (data)
    uart.on('data') if data == 'C' then send_file(f) else print('transfer interrupted') end end, 0)
end
"""

UART_SETUP = 'uart.setup(0,{baud},8,0,1,1)'
