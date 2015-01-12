nodemcu-uploader.py
===================


A simple tool for uploading files to the filesystem of an
ESP8266 running nodeMcu as well as some other usefull commands.

It should work on linux and windows and with any type of file 
that fits the filesystem, binary or text.


Usage
-----
--port and --baud are set to default /dev/ttyUSB0 and 9600 respectively.

###Upload
Uploading a number of files
```
./nodemcu-uploader.py upload init.lua README.md nodemcu-uploader.py
```

###List files
```
./nodemcu-uploader.py --port com1 file list
```

###Format filesystem
```
./nodemcu-uploader.py file format
```
 
Details
-------

This is *almost* an implementation of xmodem protocol.

1. Client calls the function recv()
2. NodeMCU disables echo and send a 'C' to tell that it's ready to receive data
3. Client sends a filename terminated with 0x00
4. NodeMCU sends ACK
5. Client send block of data according to the definition.
6. Client sends ACK
7. Step 5 and 6 are repeated until NodeMCU receives a block with 0 as size.
8. NodeMCU enables normal terminal again with echo

### Data Block Definition
__SOH__, __size__, __data[128]__

* SOH = 0x01
* Single byte telling how much of the 128 bytes data that are actually used.
* Data padded with random bytes to fill out the 128 bytes frame.
