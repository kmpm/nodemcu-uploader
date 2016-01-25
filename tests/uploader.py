import unittest
from lib import Uploader, __version__

class UploaderTestCase(unittest.TestCase):



    def test_initialize(self):
        uploader = Uploader()
