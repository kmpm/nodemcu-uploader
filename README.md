nodemcu-uploader.py
===================
A simple tool for uploading files to the filesystem of an
ESP8266 running NodeMCU as well as some other useful commands.

| master | next |
|--------|------|
|[![Build Status](https://travis-ci.org/kmpm/nodemcu-uploader.svg?branch=master)](https://travis-ci.org/kmpm/nodemcu-uploader) | [![Build Status](https://travis-ci.org/kmpm/nodemcu-uploader.svg?branch=next)](https://travis-ci.org/kmpm/nodemcu-uploader) |
Please note that these tests is not complete and it might be the tests
themselves that are having issues.

It should work on Linux, and OS X; and with any type of file
that fits the filesystem, binary or text.
For windows see the notes below.

Installation
-------------
Should be installable by PyPI (prefered) but there might be
packaging issues still.

    pip install nodemcu-uploader
    nodemcu-uploader

Otherwise clone from github and run directly from there

    git clone https://github.com/kmpm/nodemcu-uploader
    cd nodemcu-uploader
    python ./nodemcu-uploader.py

Note that pip would install pyserial >= 2.7.
The terminal command (using miniterm from pyserial) might
not work depending on version used. This is a known issue.


### Notes for Windows
There are some 
[significant issues with Windows](https://github.com/kmpm/nodemcu-uploader/issues?q=is%3Aissue+is%3Aopen+label%3Aos%3Awindows)
that might be related to serial port hardware but it can be things like
complete hang (you have to kill the python.exe process) to random
errors and/or corrupted file transfers.


Issues
-------
Create a issue in github, https://github.com/kmpm/nodemcu-uploader/issues


Disclaimer
-----------

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


Usage (part of it)
------------------
* --baud are set at a default of 9600
* --port is by default __/dev/ttyUSB0__,
  __/dev/tty.SLAB_USBtoUART__ if on Mac and __COM1__ on Windows

###Upload
Uploading a number of files.
Supports multiple files. If you want an alternate destination name, just
add a colon ":" and the new destination filename.

```
./nodemcu-uploader.py upload init.lua README.md nodemcu-uploader.py [--compile] [--restart]
```

Uploading a number of files, but saving with a different file name.

```
./nodemcu-uploader.py upload init.lua:new_init.lua README.md:new_README.md [--compile] [--restart]
```

Uploading a number of files and verify successful uploading by downloading the file
and comparing contents. Might fail because of Issue #33 - 'Upload verification breaks if file has "> " in it'

```
./nodemcu-uploader.py upload init.lua README.md nodemcu-uploader.py --verify=text
```

Uploading a number of files and verify successful uploading by doing a sha1 checksum.
__Requires crypto module on the device__

```
./nodemcu-uploader.py upload init.lua README.md nodemcu-uploader.py --verify=sha1
```


###Download
Downloading a number of files.
Supports multiple files. If you want an alternate destination name, just
add a colon ":" and the new destination filename.
```
./nodemcu-uploader.py download init.lua README.md nodemcu-uploader.py
```

Downloading a number of files, but saving with a different file name.

```
./nodemcu-uploader.py download init.lua:new_init.lua README.md:new_README.md
```

###List files
```
./nodemcu-uploader.py --port com1 file list
```

###Format filesystem
```
./nodemcu-uploader.py file format
```

###Remove specific files
```
./nodemcu-uploader.py file remove foo.lua
```

OS X Python serial module
----
To solve "ImportError: No module named serial", install the pyserial module:
```sh
python easy_install pyserial
```

Todo
----
* Speed up the initial step of uploading the script to NodeMCU
* Implement a change of baudrate for the actual transfer and go back when done
* Documentation
* --help should show full usage

Details
-------
This is *almost* an implementation of xmodem protocol for the upload part.

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

This gives a total 130 bytes per block.

The block size was decided for...

1. Being close to xmodem from where the inspiration came
2. A fixed size allow the use of the uart.on('data') event very easy.
3. 130 bytes would fit in the receive buffer buffer.
4. It would not waste that much traffic if the total size uploaded was not a multiple of the allowed datasize.
