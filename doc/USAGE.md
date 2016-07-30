 Usage
===================
This document is by no means complete.


## Common options
* --help will show some help
* --start_baud set at a default of 115200 (the speed of the nodemcu at boot in later
  versions of the firmware)
* --baud are set at a default of 115200. This setting is used for transfers and such.
* --port is by default __/dev/ttyUSB0__,
  __/dev/tty.SLAB_USBtoUART__ if on Mac and __COM1__ on Windows
* the environment variable __SERIALPORT__ will override any default port

Since v0.2.1 the program works with 2 possible speeds. It connects at a default
(--start_baud) of 115200 baud which is what the default firmware uses. Earlier
versions of the firmware and this tool used 9600 as start baudrate.
Immediately after first established communication it changes
to a higher (--baud) speed, if neccesary, which defaults
to 115200. This allows all communication to happen much faster without having to
recompile the firmware or do any manual changes to the speed.
When done and before it closes the port it changes the speed back to normal
if it was changed.
Since v0.4.0 of nodemcu-uploader it tries to use the auto-baudrate feature
build in to the firmware by sending a character repetedly when initiating
communication.

## Commands
### Upload
From computer to esp device.

```
nodemcu-uploader upload init.lua 
```


Uploading a number of files, but saving with a different file name. If you want an alternate 
destination name, just add a colon ":" and the new destination filename.

```
nodemcu-uploader upload init.lua:new_init.lua README.md:new_README.md
```

Uploading with wildcard and compiling to .lc when uploaded.
```
nodemcu-uploader upload lib/*.lua --compile
```


Uploading and verify successful uploading by downloading the file
to RAM and comparing contents.

```
nodemcu-uploader.py upload init.lua --verify=raw
```

Uploading and verify successful uploading by calculating the sha1
checksum on the esp and compare it to the checksum of the original file.
This requires the __crypto__ module in the firmware but it's more
reliable than the _raw_ method.

```
nodemcu-uploader upload init.lua --verify=sha1
```


###Download
From esp device to computer.

Downloading a number of files.
Supports multiple files. If you want an alternate destination name, just
add a colon ":" and the new destination filename.
```
nodemcu-uploader download init.lua README.md nodemcu-uploader.py
```

Downloading a number of files, but saving with a different file name.

```
nodemcu-uploader download init.lua:new_init.lua README.md:new_README.md
```

### List files
```
nodemcu-uploader --port com1 file list
```

### Format filesystem
```
nodemcu-uploader file format
```

### Remove specific files
```
nodemcu-uploader file remove foo.lua
```


