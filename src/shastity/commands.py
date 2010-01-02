# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

"""
Operational command interface to shastity.

Provides an easy-to-use high-level library interface to invoking all
of shastities main functions, de-coupled from the normal command line
interface.

This is the public interface intended for other software to use for
invoking shastity as a library rather than a shell tool, for tighter
integration.

Commands
========

Commands are named operation that can be executed. A command takes
some number (possibly zero) of positional arguments, and potentially
some number of options on a key/value basis.

In concrete terms, each command will have associated with it::

  - Its name.
  - Information about positional arguments for purpose of display to humans.
  - Information about options that may apply to the command.

In plain python, a command C with poitional arguments pos1, pos2,
... poN and a set of options O (in the form of a Configuration
instance) translates to a function call on this module of the form:

  C(pos1, pos2, ..., posN, options=O)

The concept is specifically meant to translate well into a command
line interface while still being fairly idiomatic and usable as a
library interface, while keeping the implementation identical.
"""

from __future__ import absolute_import
from __future__ import with_statement

import shastity.options as options

# In the future we'll have groups of commands too, or else command
# listings to the user become too verbose.

class Command(object):
    def __init__(self, name, args, options):
        """
        @param name: Name - string.
        @param args: List of arguments (list of name strings for human use).
        @param options: Configuration instance for the command.
        """
        self.name = name
        self.args = args
        self.options = options

_all_commands = [ Command('persist',
                          ['src-path', 'dst-uri'],
                          options.GlobalOptions()),
                  Command('materialize',
                          ['src-uri', 'dst-path'],
                          options.GlobalOptions()),
                  Command('verify',
                          ['src-path', 'dst-uri'],
                          options.GlobalOptions()),
                  Command('garbage-collect',
                          ['dst-uri'],
                          options.GlobalOptions()) ]

def all_commands():
    """
    Returns a list of all commands. The order of the list is significant.
    """
    return _all_commands

def has_command(name):
    """
    Convenience function to check whether there is a command by the
    given name.
    """
    return (len([ cmd for cmd in all_commands() if cmd.name == name]) > 0)

def persist(config):
    raise NotImplementedError('persist not implemented')

def materialize(config):
    raise NotImplementedError('materialze not implemented')

def verify(config):
    raise NotImplementedError('very not implemented')

def garbage_collect(config):
    raise NotImplementedError('garbage-collect not implemented')
