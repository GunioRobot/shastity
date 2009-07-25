# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import unittest

import shastity.backend as backend
import shastity.backends.memorybackend as memorybackend

PREFIX = 'shastity_unittest_'

def prefix(name):
    '''Trivial convenience function for constructing a PREFIX:ed filename.'''
    return PREFIX + name

class BackendsBaseCase(object):
    '''Base class for backend unit tests. Subclasses need to implement
    make_backend() (and possibly backend specific tests).'''

    def setUp(self):
        self.backend = self.make_backend() # provided by subclass

        # We do not assume the backend is empty at the time the test
        # starts, but we do assume that we can put, get and delete any
        # file beginning with PREFIX. In order to ensure we can re-run
        # tests in an idempotent fashion, we clean up pre-existing
        # files of tests first.
        fnames = [ name for name in self.backend.list() if name.startswith(PREFIX) ]

        for fname in fnames:
            self.backend.delete(fname)

    def test_basic(self):
        self.assertEqual(self.backend.list(), [])

class MemoryBackendTests(BackendsBaseCase, unittest.TestCase):
    def make_backend(self):
        return memorybackend.MemoryBackend('memory')

if __name__ == "__main__":
    unittest.main()