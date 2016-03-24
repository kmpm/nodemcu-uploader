Develop and Test nodemcu-uploader
=================================

Configure development environment
-------
```
git clone https://github.com/kmpm/nodemcu-uploader
cd nodemcu-uploader
virtualenv env
. env/bin/activate
pip install -r test_requirements.txt
python setyp.py develop
```



Testing
-------
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

