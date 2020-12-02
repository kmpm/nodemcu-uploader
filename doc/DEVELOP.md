Develop and Test nodemcu-uploader
=================================

Configure development environment
-------
```shell
git clone https://github.com/kmpm/nodemcu-uploader
cd nodemcu-uploader
python3 -m venv
. venv/bin/activate
pip install -r test_requirements.txt
pip install -e .
```



Testing
-------
```shell
pip install -r test_requirements.txt
coverage run setup.py test
# or even better testing with tox
tox
```

To run tests that actually communicate with a device you
will need to set the __SERIALPORT__ environment variable
to the port where you have an device connected.

Linux
```
export SERIALPORT=/dev/ttyUSB0
```


Publishing
----------
* https://packaging.python.org/tutorials/packaging-projects/

Please make sure to bump the version number in
nodemcu_uploader/version.py as well as the testing of that
number in tests/misc.py

```bash
#
python -m pip install --upgrade setuptools wheel twine
python setup.py sdist bdist_wheel

#test upload
python -m twine upload -u __token__ --repository testpypi dist/*

#real upload
python -m twine upload -u __token__ dist/*
```
