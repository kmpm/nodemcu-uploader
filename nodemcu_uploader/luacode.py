# -*- coding: utf-8 -*-
"""This module contains all the LUA code that needs to be on the device
to perform whats needed. They will be uploaded if they doesn't exist"""

# Copyright (C) 2015-2019 Peter Magnusson <peter@kmpm.se>
# pylint: disable=C0301
# flake8: noqa


LUA_FUNCTIONS = ['recv', 'shafile', 'send']

PRINT_FILE = "do local fd,data = (file.open or io.open)('{filename}'), '---{filename}---\\n'; while data do uart.write(0, data) data = fd:read(1024) end fd:close() uart.write(0, '---\\n') end"

INFO_GROUP = "for key,value in pairs(node.info('{group}')) do k=tostring(key) print(k .. string.rep(' ', 20 - #k), tostring(value)) end"

LIST_FILES = 'for key,value in pairs(file.list()) do print(key,value) end'
# NUL = \000, ACK = \006
RECV_LUA = \
r"""
function recv()
    local on,w,ack,nack=uart.on,uart.write,'\6','\21'
    local fopen = file.open or io.open
    local fd
    local function recv_block(d)
        local t,l = d:byte(1,2)
        if t ~= 1 then w(0, nack); fd:close(); return on('data') end
        if l >= 0  then fd:write(d:sub(3, l+2)); end
        if l == 0 then fd:close(); w(0, ack); return on('data') else w(0, ack) end
    end
    local function recv_name(d) d = d:gsub('%z.*', '') file.remove(d) fd=fopen(d, 'w') on('data', 130, recv_block, 0) w(0, ack) end
    on('data', '\0', recv_name, 0)
    w(0, 'C')
  end
function shafile(f) print(crypto.toHex(crypto.fhash('sha1', f))) end
"""  # noqa: E122

SEND_LUA = \
r"""
function send(f)
  local fd = (file.open or io.open)(f)
  if fd == nil then
    print('un'..'expected could not open '..f)
    return
  end
  local on,w,len,ch,rep=uart.on,uart.write,string.len,string.char,string.rep
  local function send_block(d)
    local l = len(d)
    w(0, '\001' .. ch(l) .. d .. rep('\0', 128 - l))
    return l
  end
  local function send_file()
    local s, p = fd:seek('end', 0), 0
    fd:seek('set', 0)
    on('data', 1, function(data)
      if data == '\006' and p<s then
        p=p+send_block(fd:read(128))
      else
        send_block('') fd:close() on('data') print('interrupted')
      end
    end, 0)
    w(0, f .. '\000')
  end
  on('data', 1, function(data)
    uart.on('data')
    if data == 'C' then send_file() else print('transfer interrupted') fd:close() end
  end, 0)
end
"""

UART_SETUP = 'uart.setup(0,{baud},8,0,1,1)'

REMOVE_ALL_FILES = r"""
for key,value in pairs(file.list()) do file.remove(key) end
"""
