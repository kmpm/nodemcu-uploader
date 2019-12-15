# -*- coding: utf-8 -*-
"""This module contains all the LUA code that needs to be on the device
to perform whats needed. They will be uploaded if they doesn't exist"""

# Copyright (C) 2015-2019 Peter Magnusson <peter@kmpm.se>
# pylint: disable=C0301
# flake8: noqa


LUA_FUNCTIONS = ['recv_block', 'recv_name', 'recv', 'shafile', 'send_block', 'send_file', 'send']

DOWNLOAD_FILE = "file.open('{filename}') print(file.seek('end', 0)) file.seek('set', {bytes_read}) uart.write(0, file.read({chunk_size}))file.close()"

PRINT_FILE = "file.open('{filename}') print('---{filename}---') print(file.read()) file.close() print('---')"

INFO_GROUP = "for key,value in pairs(node.info('{group}')) do k=tostring(key) print(k .. string.rep(' ', 20 - #k), tostring(value)) end"

LIST_FILES = 'for key,value in pairs(file.list()) do print(key,value) end'
# NUL = \000, ACK = \006
RECV_LUA = \
r"""
function recv()
    local on,w,ack,nack=uart.on,uart.write,'\6','\21'
    local fd
    local function recv_block(d)
        local t,l = d:byte(1,2)
        if t ~= 1 then w(0, nack); fd:close(); return on('data') end
        if l >= 0  then fd:write(d:sub(3, l+2)); end
        if l == 0 then fd:close(); w(0, ack); return on('data') else w(0, ack) end
    end
    local function recv_name(d) d = d:gsub('%z.*', '') d:sub(1,-2) file.remove(d) fd=file.open(d, 'w') on('data', 130, recv_block, 0) w(0, ack) end
    on('data', '\0', recv_name, 0)
    w(0, 'C')
  end
function shafile(f) print(crypto.toHex(crypto.fhash('sha1', f))) end
"""  # noqa: E122

SEND_LUA = \
r"""
function send(f) uart.on('data', 1, function (data)
  local on,w=uart.on,uart.write
  local fd
  local function send_block(d) l = string.len(d) w(0, '\001' .. string.char(l) .. d .. string.rep('\0', 128 - l)) return l end
  local function send_file(f)
    local s, p
    fd=file.open(f) s=fd:seek('end', 0) p=0
    on('data', 1, function(data)
      if data == '\006' and p<s then
        fd:seek('set',p) p=p+send_block(fd:read(128))
      else
        send_block('') fd:close() on('data') print('interrupted')
      end
    end, 0)
    w(0, f .. '\000')
  end
  uart.on('data') if data == 'C' then send_file(f) else print('transfer interrupted') end end, 0)
end
"""

UART_SETUP = 'uart.setup(0,{baud},8,0,1,1)'

REMOVE_ALL_FILES = r"""
for key,value in pairs(file.list()) do file.remove(key) end
"""
