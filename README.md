nodemcu-uploader.py
===================
A simple tool for uploading files to the filesystem of an
ESP8266 running NodeMCU as well as some other useful commands.

It should work on Linux, and OS X; and with any type of file
that fits the filesystem, binary or text.

| master |
|--------|
|[![Build Status](https://travis-ci.org/kmpm/nodemcu-uploader.svg?branch=master)](https://travis-ci.org/kmpm/nodemcu-uploader) | 

Please note that these tests is not complete and it might be the tests
themselves that are having issues.


Call for maintainers
--------------------
Hi,
This project is in need of maintenance and I (kmpm) do not have the time the 
project deserves. Look at https://github.com/kmpm/nodemcu-uploader/issues/90 
for more information on what to do about it or email me@kmpm.se


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
There might be some
[significant issues with Windows](https://github.com/kmpm/nodemcu-uploader/issues?q=is%3Aissue+is%3Aopen+label%3Aos%3Awindows).

### Notes for OS X
To solve "ImportError: No module named serial", install the pyserial module:
```sh
python easy_install pyserial
```

Usage
-----
Download NodeMCU firmware from  http://nodemcu-build.com/ .

Since version v0.4.0 of the tool you will need a recent (june/july 2016) version 
of the firmware for nodemcu. The default baudrate was changed in firmware from
9600 to 115200 and this tool was changed as well. 

If you are using an older firmware you MUST use the option `--start-baud 9600`
to the device to be recognized. Otherwise you will get a 
_Device not found or wrong port_ error.

For more usage details see [USAGE.md in doc](doc/USAGE.md)


Issues
-------
When reporting issues please provide operating system (windows, mac, linux etc.),
version of this tool `nodemcu-uploader --version` and version of the firmware
on you device. If you got the firmware from http://nodemcu-build.com/ please
tell if it was the dev or master branch and at what date it was created.

As for firmware version I would like to have a dump of the details you get
when connected using a terminal to the device at boot time.
It would look something like this...
```
NodeMCU custom build by frightanic.com
        branch: master
        commit: b580bfe79e6e73020c2bd7cd92a6afe01a8bc867
        SSL: false
        modules: crypto,file,gpio,http,mdns,mqtt,net,node,tmr,uart,wifi
 build  built on: 2016-07-29 11:08
 powered by Lua 5.1.4 on SDK 1.5.1(e67da894)
 ```

When you have as much of that as possible, 
create a issue in github, https://github.com/kmpm/nodemcu-uploader/issues



Technical Details
-----------------
This *almost* uses a implementation of xmodem protocol for the up-/download part.
The main missing part is checksum and retransmission.

This is made possible by first preparing the device by creating a set of helper
functions using the ordinary terminal mode.
These function utilize the built in uart module for the actual transfer and
cuts up the transfers to a set of manageable blocks that are reassembled
in the receiving end.

### Upload
1. Client calls the function recv()
2. NodeMCU disables echo and send a 'C' to tell that it's ready to receive data
3. Client sends a filename terminated with 0x00
4. NodeMCU sends ACK
5. Client send block of data according to the definition.
6. NodeMCU sends ACK
7. Step 5 and 6 are repeated until NodeMCU receives a block with 0 as size.
8. NodeMCU enables normal terminal again with echo

### Download
1. Client calls the function send(<filename>).
2. NodeMCU disables echo and waits for start.
2. Client send a 'C' to tell that it's ready to receive data
3. NodeMCU sends a filename terminated with 0x00
4. Client sends ACK
5. NodeMCU send block of data according to the definition.
6. Client sends ACK
7. Step 5 and 6 are repeated until client receives a block with 0 as size.
8. NodeMCU enables normal terminal again with echo.



### Data Block Definition
__SOH__, __size__, __data[128]__

* SOH = 0x01
* Single byte telling how much of the 128 bytes data that are actually used.
* Data padded with random bytes to fill out the 128 bytes frame.

This gives a total 130 bytes per block.

The block size was decided for...

1. Being close to xmodem from where the inspiration came
2. A fixed size allow the use of the uart.on('data') event very easy.
3. 130 bytes would fit in the receive buffer.
4. It would not waste that much traffic if the total size uploaded was not a 
   even multiple of the allowed datasize.



Disclaimer
-----------

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

