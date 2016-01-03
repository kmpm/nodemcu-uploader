nodemcu-uploader.py
===================
A simple tool for uploading files to the filesystem of an
ESP8266 running NodeMCU as well as some other useful commands.

It should work on Linux, Windows, and OS X; and with any type of file
that fits the filesystem, binary or text.

Installation
-------------
Should be installable by PyPI but it's not that tested yet.

    pip install nodemcu-uploader
    nodemcu-uploader.py

Otherwise clone from github and run directly from there

    git clone https://github.com/kmpm/nodemcu-uploader
    cd nodemcu-uploader
    ./nodemcu-uploader.py

Support
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
--port and --baud are set to default /dev/ttyUSB0 and 9600 respectively.

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

Uploading a number of files and verify successful uploading.

```
./nodemcu-uploader.py upload init.lua README.md nodemcu-uploader.py -v
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
