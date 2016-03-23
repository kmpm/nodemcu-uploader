Testing nodemcu-uploader
========================

```
pip install -r test_requirements.txt
coverage run setup.py test
```

To run tests that actually communicate with a device you
will need to set the __SERIALPORT__ environment variable
to the port where you have an device connected.

Linux
```
export SERIALPORT=/dev/ttyUSB0
```

