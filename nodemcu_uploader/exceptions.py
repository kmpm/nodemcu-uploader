# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>
#pylint: disable=C0111

"""Various custom exceptions"""

class CommunicationTimeout(Exception):
    def __init__(self, message, buf):
        super(CommunicationTimeout, self).__init__(message)
        self.buf = buf


class BadResponseException(Exception):
    def __init__(self, message, expected, actual):
        message = message + ' expected:`%s` != actual: `%s`' % (expected, actual)
        super(BadResponseException, self).__init__(message)

        self.expected = expected
        self.actual = actual

class NoAckException(Exception):
    pass

class DeviceNotFoundException(Exception):
    pass

class VerificationError(Exception):
    pass
