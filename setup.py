from setuptools import setup

setup(name='nodemcu-uploader',
      version='0.1.2',
      install_requires=[
          'pyserial==2.7'
      ],
      scripts = ['nodemcu-uploader.py'],
      url='https://github.com/kmpm/nodemcu-uploader',
      author='kmpm',
      author_email='peter@birchroad.net',
      description='tool for uploading files to the filesystem of an ESP8266 running NodeMCU.',
      keywords=['esp8266', 'upload', 'nodemcu']
)
