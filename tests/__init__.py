# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
"""Add tests to include here"""

import unittest
import logging

def get_tests():
    """returns the tests to run"""
    return full_suite()

def full_suite():
    """creates a full suite of tests"""
    logging.basicConfig(filename='test.log', level=logging.INFO,
        ormat='%(asctime)s %(levelname)s %(module)s.%(funcName)s %(message)s')

    from .misc import MiscTestCase
    from . import uploader
    # from .serializer import ResourceTestCase as SerializerTestCase
    # from .utils import UtilsTestCase

    miscsuite = unittest.TestLoader().loadTestsFromTestCase(MiscTestCase)
    uploadersuite = unittest.TestLoader().loadTestsFromModule(uploader)
    return unittest.TestSuite([miscsuite, uploadersuite])
