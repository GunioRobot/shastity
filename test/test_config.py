# -*- coding: utf-8 -*-

# Copyright (c) 2009 Peter Schuller <peter.schuller@infidyne.com>

from __future__ import absolute_import
from __future__ import with_statement

import unittest

import shastity.config as config

class ConfigTests(unittest.TestCase):
    def test_naming(self):
        self.assertEqual(config.StringOption('long-name', 'l').name(), 'long-name')
        self.assertEqual(config.StringOption('long-name', 'l').short_name(), 'l')

    def test_default(self):
        self.assertEqual(config.StringOption('testname', default='test').get(), 'test')

    def test_required(self):
        self.assertRaises(config.RequiredOptionMissingError,
                          lambda: config.StringOption('testname').get_required())
        self.assertEqual('test', config.StringOption('testname').parse('test').get_required())

    def test_string_option(self):
        config.StringOption('testname').parse('test')
        self.assertRaises(config.BadOptionValueType, lambda: config.StringOption('testname').parse(5))

    def test_int_option(self):
        config.IntOption('testname').parse(5)
        config.IntOption('testname').parse('5')
        self.assertRaises(config.BadOptionValueType, lambda: config.IntOption('testname').set('5'))

    def test_bool_option(self):
        config.BoolOption('testname').parse('true')
        config.BoolOption('testname').parse('True')
        config.BoolOption('testname').parse('1')
        config.BoolOption('testname').parse('0')
        config.BoolOption('testname').parse('false')
        config.BoolOption('testname').parse('False')

        self.assertRaises(config.OptionParseError,
                          lambda: config.BoolOption('testname').parse('notabool'))

    def test_default_configuration_creation(self):
        c = config.DefaultConfiguration()
        self.assertFalse(c.has_option('a'))

        c = config.DefaultConfiguration({'test-option': config.StringOption('test-option')})
        self.assertTrue(c.has_option('test-option'))
        self.assertEqual(c.options()['test-option'].short_name(), None)

        c = config.DefaultConfiguration({'test-option': config.StringOption('test-option', 't')})
        self.assertTrue(c.has_option('test-option'))
        self.assertEqual(c.options()['test-option'].short_name(), 't')

    def test_default_configuration_merge(self):
        c1 = config.DefaultConfiguration({'o1': config.StringOption('o1')})
        c2 = config.DefaultConfiguration({'o2': config.StringOption('o2')})

        c3 = c1.merge(c2)

        self.assertTrue(c3.has_option('o1'))
        self.assertTrue(c3.has_option('o2'))

        c4 = config.DefaultConfiguration({'o2': config.StringOption('o2', 'o')})

        self.assertRaises(config.ConflictingMergeError,
                          lambda: c4.merge(c3))

        c5 = c3.merge(c4, allow_override=True)

        self.assertEqual(c5.get_option('o2').short_name(), 'o')

    def test_default_configuration_option_getter(self):
        opt = config.StringOption('o-1')
        opt2 = config.StringOption('non-specified-option')
        c = config.DefaultConfiguration({'o-1': opt,
                                         'non-specified-option': opt2})

        opt.set('value')

        self.assertEqual(opt.get(), c.opts.o_1)

        # caller asked for non-existent option
        self.assertRaises(AttributeError,
                          lambda: c.opts.nonexistent_option)

        # user did not provide a value for an existing option
        self.assertRaises(config.RequiredOptionMissingError,
                          lambda: c.opts.non_specified_option)

if __name__ == '__main__':
    unittest.main()
