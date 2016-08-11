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


Since version v0.4.0 of the tool you will need a recent (june/july 2016) 
version or later of the firmware for nodemcu. The default baudrate was changed in 
firmware from 9600 to 115200 and this tool was changed as well. 
Download a recent firmware from http://nodemcu-build.com/ .

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
communication. This requires a firmware from june/july 2016 or later.

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
Listing files, using serial port com1 on Windows
```
nodemcu-uploader --port com1 file list
```

### Do (execute) a file
`nodemcu-uploader file do runme.lua`

This file has to exist on the device before, otherwise you will get an error.

### Print a file
This will show the contents of an existing file.

`nodemcu-uploader file print init.lua`


### Listing heap memory size
`nodemcu-uploader node heap`


### Restarting the device
`nodemcu-uploader node restart`


### Format filesystem
```
nodemcu-uploader file format
```
Note that this can take a long time depending on size of flash on the device.
Even if the tool timeout waiting for response from the device it might have 
worked. The tool was just not waiting long enough.

### Remove specific files
```
nodemcu-uploader file remove foo.lua
```

## Misc
### Setting default serial-port
Using the environment variable `SERIALPORT` you can avoid having to 
type the `--port` option every time you use the tool.

On Windows, if your devices was connected to COM3 this could be done like this.
```batch
set SERIALPORT=com3
REM on all subsequent commands the default port `com3`would be assumed

nodemcu-uploader file list
```
