#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>


DOWNLOAD_FILE = "file.open('{filename}') print(file.seek('end', 0)) file.seek('set', {bytes_read}) uart.write(0, file.read({chunk_size}))file.close()"

PRINT_FILE = "file.open('{filename}') print('---{filename}---') print(file.read()) file.close() print('---')"

LIST_FILES = 'for key,value in pairs(file.list()) do print(key,value) end'

SAVE_LUA = \
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
      uart.setup(0,{baud},8,0,1,1)
    end
  else
    uart.write(0, '\021' .. d)
    uart.setup(0,{baud},8,0,1,1)
    uart.on('data')
  end
end
function recv_name(d) d = string.gsub(d, '\000', '') file.remove(d) file.open(d, 'w') uart.on('data', 130, recv_block, 0) uart.write(0, '\006') end
function recv() uart.setup(0,{baud},8,0,1,0) uart.on('data', '\000', recv_name, 0) uart.write(0, 'C') end
function shafile(f) file.open(f, "r") print(crypto.toHex(crypto.hash("sha1",file.read()))) file.close() end
"""
LUA_FUNCTIONS = ['recv_block', 'recv_name','recv','shafile']
UART_SETUP = 'uart.setup(0,{baud},8,0,1,1)'
