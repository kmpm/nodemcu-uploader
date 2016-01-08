from setuptools import setup, find_packages

setup(name='nodemcu-uploader',
      version='0.1.3',
      install_requires=[
          'pyserial==2.7'
      ],
      packages = ['nodemcu_uploader'],
      package_dir = {'nodemcu_uploader': 'lib'},
      url='https://github.com/kmpm/nodemcu-uploader',
      author='kmpm',
      author_email='peter@birchroad.net',
      description='tool for uploading files to the filesystem of an ESP8266 running NodeMCU.',
      keywords=['esp8266', 'upload', 'nodemcu'],
      entry_points = {
          'console_scripts': [
              'nodemcu-uploader=nodemcu_uploader.main:main_func'
          ]
      }
)
