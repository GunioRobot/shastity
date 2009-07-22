# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

"""
Provide a thin wrapper around file system operations. Reasons for
doing this include:

  - It makes it easier to unit test code that depends on file system access
    because we can more easily write mock-ups.
  - File system operations are potentially platform sensetive, so it is nice to
    have them in one place.
  - File system operations are a "dangerous" part of shastity in the sense that
    they side-effect on the surrounding environment. It is nice to avoid having
    such things spread all over the place.

Because file system access is inherently destructive in nature (i.e.,
has side-effects) we comfortable module file systems as class
instances.

Note that our "file system" concept is not the same as that of an
operating system; to us, a file system is basically "files and
directories accessible by the process via the native system's API". We
do not intend to imply any specific knowledge about OS file system
mount points, types, or anything like that.
"""

from __future__ import absolute_import
from __future__ import with_statement

import os
import os.path
import shutil
import tempfile

class StaleTemporaryDirectory(Exception):
    '''Raised to indicate that an attempt to use a stale (cleaned up)
    temporary directory was detected.'''
    pass

class TemporaryDirectory(object):
    '''An automatically cleaning temporary directory. The preferred
    use is with the 'with' statement, but calling code may also
    close() it explicitly. It will also close on GC.

    Most users will only be interested in the 'path' attribute of a
    temporary directory object.

    @ivar fs The file system with which the temporary directory is associated.
    @ivar path The path to the temporary directory.'''
    def __init__(self, fs, path):
        assert isinstance(fs, FileSystem)

        self.__fs = fs
        self.__path = path
        self.__stale = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        if not self.__stale:
            self.__stale = True
            self.__fs.rmtree(self.__path)

    def __get_fs(self):
        if self.__stale:
            raise StaleTemporaryDirectory(self.__path)
        return self.__fs
        
    def __get_path(self):
        if self.__stale:
            raise StaleTemporaryDirectory(self.__path)
        return self.__path

    fs = property(__get_fs)
    path = property(__get_path)

class FileSystem(object):
    ''' Abstract base class of file systems (see module documentation
    for our definition of file system). This defines the interface to
    be implemented by file systems.

    Unless otherwise noted, methods with obvious POSIX counterparts
    will have matching semantics.

    In general, failure cases are those of POSIX.
    '''
    def mkdir(self, path):
        raise NotImplementedError

    def rmdir(self, path):
        raise NotImplementedError

    def unlink(self, path):
        raise NotImplementedError

    def symlink(self, src, dst):
        raise NotImplementedError

    def exists(self, path):
        return os.path.exists(path)

    def open(self, path, mode):
        raise NotImplementedError

    def rmtree(self, path):
        '''Recursively delete the tree rooted at path (not following
        symlinks).'''
        raise NotImplementedError

    def mkdtemp(self, suffix=None):
        '''Atomically create/allocate a temporary directory and return
        its name.
        
        @note While similar, this is not identical to python's tempfile.mkdtemp().

        @param suffix: Suffix to apply to the allocated name, if supported.

        @return The absolute path of the temporary directory. '''
        raise NotImplementedError

    def tempdir(self, suffix=None):
        '''Allocate a temporary directory and return a
        TemporaryDirectory instance backed by this file system.

        @note This method has a default implementation in the abstract
              base class which is implemented in terms of mkdtemp().'''
        dirname = self.mkdtemp()
        return TemporaryDirectory(self, dirname)

class LocalFileSystem(FileSystem):
    def mkdir(self, path):
        os.mkdir(path)

    def rmdir(self, path):
        os.rmdir(path)

    def unlink(self, path):
        os.unlink(path)

    def symlink(self, src, dst):
        os.symlink(src, dst)

    def open(self, path, mode):
        return open(path, mode)

    def rmtree(self, path):
        shutil.rmtree(path)

    def mkdtemp(self, suffix=None):
        # mkdtemp differentiates between None and no parameter
        return tempfile.mkdtemp(suffix=('' if suffix is None else suffix))

class MemoryFileSystem(FileSystem):
    '''A simple in-memory file system primarily intended for unit testing.'''

    def __init__(self):
        # internally we represent the file system as follows:
        #
        # A directory is a dict, each key being an entry. If the value
        # is a dict, it represents a directory. If the value is is a
        # tuple, the first element is a string representing the type,
        # and the second element is dependent on the type.
        #
        # The type can be either a "symlink" or a "file". The second
        # element in the case of a symlink is the value of the
        # symlink; for a file, it is a list of one entry which is the
        # file contents. (The extra list in the file case is to
        # support in-place file modification.)

        # Start with a completely empty root directory.
        self.__tree = dict(tmp=dict())

    def __lookup(self, path):
        def rec(cur, comps):
            if not comps:
                return cur
            else:
                if not isinstance(cur, dict):
                    raise OSError(errno.ENOTDIR, 'not a directory')
                else:
                    if comps[0] in cur:
                        rec(cur[comps[0]], comps[1:])
                    else:
                        raise OSError(errno.ENOENT, 'file not found')

        return rec(self.__tree, path.split('/'))

    def __split_slash_agnostically(self, path):
        directory, file = os.path.split(path)
        if not file:
            directory, file = os.path.split(directory)

        assert directory
        assert file

        return (directory, file)

    def mkdir(self, path):
        directory, newdir = self.__split_slash_agnostically(path)
        d = self.__lookup(path)
        if newdir in d:
            raise OSError(errno.EEXIST, 'file exists')
        else:
            d[newdir] = dict()

    def rmdir(self, path):
        raise NotImplementedError

    def unlink(self, path):
        raise NotImplementedError

    def symlink(self, src, dst):
        raise NotImplementedError

    def exists(self, path):
        return os.path.exists(path)

    def open(self, path, mode):
        raise NotImplementedError

    def rmtree(self, path):
        raise NotImplementedError

    def mkdtemp(self, suffix=None):
        raise NotImplementedError

    def tempdir(self, suffix=None):
        return TemporaryDirectory(self, dirname)
    
        
