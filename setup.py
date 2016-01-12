from setuptools import setup

exec(open('lib/version.py').read())

setup(name='nodemcu-uploader',
      version=__version__,
      install_requires=[
          'pyserial==3.0'
      ],
      packages=['nodemcu_uploader'],
      package_dir={'nodemcu_uploader': 'lib'},
      url='https://github.com/kmpm/nodemcu-uploader',
      author='kmpm',
      author_email='peter@birchroad.net',
      description='tool for uploading files to the filesystem of an ESP8266 running NodeMCU.',
      keywords=['esp8266', 'upload', 'nodemcu'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2.7'
      ],
      license='MIT',
      entry_points={
          'console_scripts': [
              'nodemcu-uploader=nodemcu_uploader.main:main_func'
          ]
      }
     )
