# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
import unittest

def get_tests():
    return full_suite()

def full_suite():
    from .misc import MiscTestCase
    #from .uploader import UploaderTestCase
    # from .serializer import ResourceTestCase as SerializerTestCase
    # from .utils import UtilsTestCase

    miscsuite = unittest.TestLoader().loadTestsFromTestCase(MiscTestCase)
    #uploadersuite = unittest.TestLoader().loadTestsFromTestCase(UploaderTestCase)
    return unittest.TestSuite([miscsuite, ])
