from setuptools import setup

setup(name='nodemcu-uploader',
      version='0.1.0-beta',
      install_requires=[
          'pyserial>=3.0'
      ],
      scripts = ['nodemcu-uploader.py'],
      url='https://github.com/kmpm/nodemcu-uploader',
      author='kmpm'
)
