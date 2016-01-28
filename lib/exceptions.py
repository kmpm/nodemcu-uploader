# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Peter Magnusson <peter@birchroad.net>

class CommunicationTimeout(Exception):
    def __init__(self, message, buffer):
        super(CommunicationTimeout, self).__init__(message)
        self.buffer = buffer


class BadResponseException(Exception):
    def __init__(self, message, expected, actual):
        message = message + ' expected:`%s` != actual: `%s`' % (expected, actual)
        super(BadResponseException, self).__init__(message)

        self.expected = expected
        self.actual = actual


class DeviceNotFoundException(Exception):
    pass