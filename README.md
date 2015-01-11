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
 