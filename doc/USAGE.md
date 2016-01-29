 Usage 
===================
This document is by no means complete.


## Common options
* --help will show some help
* --start_baud set at a default of 9600 (the speed of the nodemcu at boot)
* --baud are set at a default of 115200
* --port is by default __/dev/ttyUSB0__,
  __/dev/tty.SLAB_USBtoUART__ if on Mac and __COM1__ on Windows
* the environment variable __SERIALPORT__ will override any default port

Since v0.2.1 the program works with 2 speeds. It connects at a default
(--start_baud) of 9600 baud which is what the default firmware uses. Immediately after
first established communication it changes to a higher (--baud) speed which defaults
to 115200. This allows all communication to happen much faster without having to
recompile the firmware or do any manual changes to the speed.
When done and before it closes the port it changes the speed back to normal.

## Commands
### Upload
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
and comparing contents.

```
./nodemcu-uploader.py upload init.lua README.md nodemcu-uploader.py --verify=raw
```

Uploading a number of files and verify successful uploading by doing a sha1 checksum.
__Requires crypto module on the device__ and currently files not to big (~1000 bytes)

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

### List files
```
./nodemcu-uploader.py --port com1 file list
```

### Format filesystem
```
./nodemcu-uploader.py file format
```

### Remove specific files
```
./nodemcu-uploader.py file remove foo.lua
```


