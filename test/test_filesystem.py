# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import errno
import os.path
import unittest

import shastity.filesystem as fs

class FileSystemBaseCase(object):
    def setUp(self):
        self.fs = self.make_file_system() # provided by subclass

    def assertOSError(self, errno, fn, *args, **kwargs):
        try:
            fn(*args, **kwargs)
            raise AssertionError('expected OSError with errno %d; got no OSError at all' % (errno,))
        except OSError, e:
            self.assertTrue(e.errno == errno, 'errno %d expected, got %d' % (errno, e.errno))
        
    def test_tempdir(self):
        with self.fs.tempdir() as tdir:
            tpath = tdir.path

            self.assertTrue(self.fs.exists(tdir.path), 'tempdir should exist')
            self.assertOSError(errno.EEXIST, self.fs.mkdir, tdir.path)

            # successful mkdir() and exists?
            testdir = os.path.join(tdir.path, 'testdir')
            self.fs.mkdir(testdir)
            self.assertTrue(self.fs.exists(testdir))
            self.assertFalse(self.fs.exists(os.path.join(tdir.path, 'non-existent-testdir')))

            # should not be able to rmdir non-empty dirs
            self.assertOSError(errno.ENOTEMPTY, self.fs.rmdir, tdir.path)

            # successful exists()?
            self.assertTrue(self.fs.exists(testdir))
            
            # successful is_dir()? todo: test non-dir
            self.assertTrue(self.fs.is_dir(testdir))

            # todo: test symlink creation + testing

            # successful listdir()?
            self.assertEqual(self.fs.listdir(tdir.path), ['testdir'])

            # successful rmdir() on empty dir?
            self.fs.rmdir(testdir)

            # retry, this time we should fail
            self.assertOSError(errno.ENOENT, self.fs.rmdir, testdir)

            # todo: populate diverse tree, try rmtree()
            
        self.assertFalse(self.fs.exists(tpath), 'tempdir should be removed')

class LocalFileSystemTests(FileSystemBaseCase, unittest.TestCase):
    def make_file_system(self):
        return fs.LocalFileSystem()

class MemoryFileSystemTests(FileSystemBaseCase, unittest.TestCase):
    def make_file_system(self):
        return fs.MemoryFileSystem()

    def test_creationmodes(self):
        # test creation but do not bother testing flags since it
        # effectively boilds down to cut'n'paste anyway
        fs.OpenMode('r')
        fs.OpenMode('r+')
        fs.OpenMode('w')
        fs.OpenMode('w+')
        fs.OpenMode('a')
        fs.OpenMode('a+')

if __name__ == "__main__":
    unittest.main()
