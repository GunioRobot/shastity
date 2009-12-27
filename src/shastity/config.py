# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

"""
Configuration handlng.

Provides some infra-structure for expressing and dealing with the
configuration of shastity, hopefully in a way which caters both to
creating a user-friendly command line interface and a user-friendly
library API for Python callers.
"""

from __future__ import absolute_import
from __future__ import with_statement

class RequiredOptionMissingError(Exception):
    """
    Raised to indicate an option value was mssing, where it was in
    fact required.

    @ivar option_name The name of the option whose value is missing.
    @ivar comment A human-readable comment providing further details, or
                  None if not available.
                  """
    def __init__(self, option_name, comment=None):
        """
        @param option_name The value to assign to self.option_name
        @param comment The value to assign to self.comment
        """
        self.option_name = option_name
        self.comment = comment

class BadOptionValueType(Exception):
    """
    Raised to indicate an attempt to set the value of an option to the
    wrong type.
    """
    pass

class ConflictingMergeError(Exception):
    """
    Raised to indicate an attempt to merge configurations failed due
    to an option conflict.
    """
    pass

class Option:
    """
    Abastract base class defining the interface for all options. An
    option is some configuration "knob" that has a name and a value
    that has to satisfy certain criteria. An interface is provided for
    handling options in a generic fashion.

    Methods beginning with an underscore are intended for
    implementation by subclasses.
    """
    def name(self):
        """
        Return the name of the option. The convention is for
        hyphen-separated lower-case names (i.e., 'name-of-my-option').

        @return The name (key) of this option.
        """
        pass

    def short_name(self):
        """
        @return The short name (one character) of this option, or None
                if there is none.

        @note This is a somewhat unclean coupling to the command line
              interface.
        """
        pass

    def parse(self, s):
        """
        Parse a string representation of the desired value of the
        option.

        @raise Exceptoin If the string cannot be parsed.
        @raise Exception If the resulting value after parsing is invald.
        """
        pass

    def set(self, value):
        """
        Set the value of the option.

        @raise An exception if the value is nod valid for this option.
        """
        pass

    def get(self):
        """
        Return the current value of this option, or None if there is
        none (not distingushed from an actual option value of None).

        @returns The value.
        """
        pass

    def get_required(self):
        """
        Return the current value of this option, or raise an exception
        if one is not available. This is intended to be used when
        asking for options where the code requires that it be
        available, in a way which should generate an error containing
        reasonably user-friendly error information.

        @raise RequiredOptionMissingError

        @return The current value.
        """
        pass

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)

class AbstractOption(Option):
    """
    Provide a suitable baseclass for most/all subclasses of
    options. Subclasses implement _validate_value() and
    _parse_value().
    """
    def __init__(self, long_name, short_name=None):
        self.__long_name = long_name
        self.__short_name = short_name

        self.__set = False

    def name(self):
        return self.__long_name

    def short_name(self):
        return self.__short_name

    def parse(self, value):
        self.set(self._parse(value))

        return self

    def set(self, value):
        self._validate(value)

        self.__set = True
        self.__value = value

        return self

    def get(self):
        return self.__value

    def get_required(self, comment=None):
        if not self.__set:
            raise RequiredOptionMissingError(unicode(self), comment=comment)

        return self.get()

    def _parse(self, value):
        """
        @return Parsed value (string -> object).
        """
        raise NotImplementedError

    def _validate(self, value):
        """
        @raise An error if the value is not valid.
        """
        raise NotIMplementedError

    def _assertType(self, obj, typ):
        if not isinstance(obj, typ):
            raise BadOptionValueType('value %s of option %s is not of type %s'
                                     '' % (obj, unicode(self), unicode(typ)))

    def _assertString(self, obj):
        # special case string due to disjoint types :(
        if not isinstance(obj, str) and not isinstance(obj, unicode):
            raise BadOptionValueType('value %s of option %s is not a string'
                                     '' % (obj, unicode(self)))

class StringOption(AbstractOption):
    def _parse(self, s):
        return s

    def _validate(self, value):
        self._assertString(value)

class IntOption(AbstractOption):
    def _parse(self, s):
        return int(s)

    def _validate(self, value):
        self._assertType(value, int)

class Configuration(object):
    """
    A configuration is a set of expected (or potential) options that
    define the outcome of some operation. Configuration instances can
    be merged (with conflict detection).

    In essence the functionality is a subset of a dict, plus some
    additions. The existence of the class hierarchy is mostly for
    interface/documentation purposes.
    """
    def options(self):
        """
        Return all options in this configuration.

        @return An iterable of Option instances.
        """
        raise NotImplementedError()

    def merge(self, other, allow_override=False):
        """
        Merge the other configuration with this one, producting a new
        Configuration.

        @param other: The other Configuration instance.
        @param allow_overwrite: Whether to allow options in
                                the other configuration to
                                override our own. If not,
                                confliction options will
                                result in a ConflictingMergeError.

        @return The result of the merger (a Configuration instance).
        """
        raise NotImplementedError()

class DefaultConfiguration(Configuration):
    def __init__(self, opts=None):
        """
        @param opts: None, or dict of name->option mappings.
        """
        self.__options = dict()

        if opts:
            for name, opt in opts.iteritems():
                assert name == opt.name()
                self.add_option(opt)

    def options(self):
        return self.__options

    def remove_option(self, name):
        del self.__options[name]

    def add_option(self, option):
        name = option.name()
        if name in self.__options:
            raise DuplicateOptionError(name)

        self.__options[name] = option

    def get_option(self, name):
        return self.__options[name]

    def has_option(self, name):
        return (name in self.__options)

    def merge(self, other, allow_override=False):
        ret = DefaultConfiguration(self.options())

        for name, opt in other.options().iteritems():
            if ret.has_option(opt.name()):
                if allow_override:
                    ret.remove_option(opt.name())
                else:
                    raise ConflictingMergeError(opt.name())
            ret.add_option(opt)

        return ret
