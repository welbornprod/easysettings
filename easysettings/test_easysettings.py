#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_easysettings.py
    Unit tests for EasySettings

    -Christopher Welborn 07-14-2015
"""
from __future__ import print_function
import os
import sys
import tempfile
import unittest
from datetime import (
    date,
    datetime,
)

from . import (
    __version__ as version,
    EasySettings,
    ISO8601,
)


if sys.version_info.major < 3:
    FileNotFoundError = IOError

NONEXISTENT_FILE = 'NONEXISTENT_FILE'
if os.path.exists(NONEXISTENT_FILE):
    # It's happened before, because of a test failure. :(
    os.remove(NONEXISTENT_FILE)


class EasySettingsTests(unittest.TestCase):

    """ Tests EasySettings functionality. """

    def setUp(self):
        # Set up a test configuration file to work with.
        fd, fname = tempfile.mkstemp(suffix='.conf', prefix='easysettings.')
        os.write(fd, '# Test settings.'.encode())
        os.close(fd)
        self.testfile = fname
        # Known values to test with.
        # Assumptions about these values are made in some tests.
        self.test_values = [
            ('option{}'.format(i), 'value{}'.format(i))
            for i in range(1, 4)
        ]

    def assertDateEqual(self, d1, d2, msg=None):
        acceptable = (date, datetime)
        if not (isinstance(d1, acceptable) and isinstance(d2, acceptable)):
            acceptables = '({})'.format(', '.join(
                type(x).__name__
                for x in acceptable
            ))
            raise TypeError('Expecting {}, got: {!r} and {!r}'.format(
                acceptables,
                type(d1).__name__,
                type(d2).__name__
            ))
        self.assertEqual(d1.strftime(ISO8601), d2.strftime(ISO8601), msg=msg)

    def clear_file(self, filename):
        with open(filename, 'w') as f:
            f.write('# Test settings.')

    def test_compare_opts(self):
        """ compare_settings() should make a good comparison. """
        es1 = EasySettings()
        es1.set_list(self.test_values)
        es2 = EasySettings()
        es2.set_list(self.test_values)
        self.assertTrue(
            es1.compare_opts(es2),
            msg='compare_opts(es2) failed for equal instances!',
        )
        self.assertTrue(
            es1.compare_opts(es1, es2),
            msg='compare_opts(es1, es2) failed for equal instances!',
        )
        # Change the first value.
        es2.set('new_option', 'MODIFED')
        self.assertFalse(
            es1.compare_opts(es2),
            msg='compare_opts(es2) failed for non-equal instances!',
        )
        self.assertFalse(
            es1.compare_opts(es1, es2),
            msg='compare_opts(es1, es2) failed for non-equal instances!',
        )

    def test_compare_settings(self):
        """ compare_settings() should make a good comparison. """
        es1 = EasySettings()
        es1.set_list(self.test_values)
        es2 = EasySettings()
        es2.set_list(self.test_values)
        self.assertTrue(
            es1.compare_settings(es2),
            msg='compare_settings(es2) failed for equal instances!',
        )
        self.assertTrue(
            es1.compare_settings(es1, es2),
            msg='compare_settings(es1, es2) failed for equal instances!',
        )
        # Change the first value.
        es2.set(es2.list_options()[0], 'MODIFED')
        self.assertFalse(
            es1.compare_settings(es2),
            msg='compare_settings(es2) failed for non-equal instances!',
        )
        self.assertFalse(
            es1.compare_settings(es1, es2),
            msg='compare_settings(es1, es2) failed for non-equal instances!',
        )

    def test_compare_vals(self):
        """ compare_vals() should make a good comparison. """
        es1 = EasySettings()
        es1.set_list(self.test_values)
        es2 = EasySettings()
        es2.set_list(self.test_values)
        self.assertTrue(
            es1.compare_vals(es2),
            msg='compare_vals(es2) failed for equal instances!',
        )
        self.assertTrue(
            es1.compare_vals(es1, es2),
            msg='compare_vals(es1, es2) failed for equal instances!',
        )
        # Change the first value.
        firstkey = es2.list_options()[0]
        es2.set(firstkey, 'MODIFIED')
        self.assertFalse(
            es1.compare_vals(es2),
            msg='compare_vals(es2) failed for non-equal instances!',
        )
        self.assertFalse(
            es1.compare_vals(es1, es2),
            msg='compare_vals(es1, es2) failed for non-equal instances!',
        )
        # Change the first one, to make them equal again.
        es1.set(firstkey, 'MODIFIED')
        self.assertTrue(
            es1.compare_vals(es2),
            msg='compare_vals(es2) failed for equal instances!',
        )
        self.assertTrue(
            es1.compare_vals(es1, es2),
            msg='compare_vals(es1, es2) failed for equal instances!',
        )
        # Remove an option from #2
        es2.remove('option3')
        self.assertFalse(
            es1.compare_vals(es2),
            msg='compare_vals(es2) failed for missing option!',
        )
        # Reset, except with None value (bug #4)
        es1.set('option3', None)
        es2.set('option3', None)
        self.assertTrue(
            es1.compare_vals(es2),
            msg='compare_vals(es2) failed for None values!',
        )

    def test_comparison_ops(self):
        """ EasySettings comparison operators hold true """
        es1 = EasySettings()
        es1.set_list(self.test_values)
        es2 = EasySettings()
        es2.set_list(self.test_values)
        # Extra values for bug #4.
        es1.set('option4', None)
        es2.set('option4', None)
        self.assertEqual(
            es1,
            es2,
            msg='EasySettings with the same options/values are not equal!'
        )

        # Change the first value.
        es2.set(es2.list_options()[0], 'MODIFED')
        self.assertNotEqual(
            es1,
            es2,
            msg='EasySettings with different values compared equal!'
        )

        # Add a value.
        es2.set('new_option', 'new_value')
        self.assertGreater(
            es2,
            es1,
            msg='EasySettings with more options was not greater!'
        )
        self.assertLess(
            es1,
            es2,
            msg='EasySettings with less options was not less!'
        )

        # Reset to equal.
        es2 = es1.copy()
        self.assertGreaterEqual(
            es1,
            es2,
            msg='EasySettings with same options/values not greater or equal!'
        )
        self.assertLessEqual(
            es1,
            es2,
            msg='EasySettings with same options/values was not less or equal!'
        )
        # Add an option.
        es2.set('new_option', 'new_value')
        self.assertGreaterEqual(
            es2,
            es1,
            msg='EasySettings with more options was not greater or equal!'
        )
        self.assertLessEqual(
            es1,
            es2,
            msg='EasySettings with less options was not less or equal!'
        )

    def test_datetimes(self):
        """ EasySettings handles dates/datetimes. """
        self.clear_file(self.testfile)
        settings = EasySettings(self.testfile)
        d = datetime.now()
        settings.set('today', d.date())
        settings.setsave('now', d)
        loaded = EasySettings(self.testfile)
        self.assertDateEqual(
            d,
            loaded.get('now'),
            msg='Failed to serialize datetime.'
        )
        self.assertDateEqual(
            d.date(),
            loaded.get('today'),
            msg='Failed to serialize date.'
        )

    def test_list_values(self):
        """ EasySettings handles lists of options and values """

        settings = EasySettings()
        settings.set_list(self.test_values)

        self.assertListEqual(
            sorted(settings.settings),
            sorted(settings.list_options()),
            msg='settings.list_options() differs from list(settings)'
        )

        self.assertListEqual(
            sorted(settings.settings.values()),
            sorted(settings.list_values()),
            msg='settings.list_values() differs from list(settings.values())'
        )

        self.assertListEqual(
            sorted(settings.list_settings()),
            self.test_values,
            msg='list_settings() failed'
        )

        # Test queries.
        self.assertListEqual(
            sorted(settings.list_options('3')),
            ['option3'],
            msg='Search query failed for list_options(\'3\')'
        )

        self.assertListEqual(
            sorted(settings.list_values('3')),
            ['value3'],
            msg='Search query failed for list_values(\'3\')'
        )

        self.assertListEqual(
            sorted(settings.list_settings('3')),
            [('option3', 'value3')],
            msg='Search query failed for list_settings(\'3\')'
        )

    def test_load_save(self):
        """ EasySettings loads and saves valid config files """
        settings = EasySettings(self.testfile)
        self.assertTrue(
            settings.load_file(),
            msg='Failed to load file: {}'.format(self.testfile)
        )

        settings.set('new_option', 'value')
        self.assertTrue(
            settings.save(),
            msg='Failed to save file: {}'.format(self.testfile)
        )

        with open(self.testfile) as f:
            rawdata = f.read()

        self.assertTrue(
            ('new_option' in rawdata) and ('value' in rawdata),
            msg='Could not find new option in saved data!'
        )

    def test_removals(self):
        """ EasySettings clears and removes items """
        settings = EasySettings()
        settings.set_list(self.test_values)

        settings.remove('option3')
        self.assertTrue(
            'option3' not in settings.settings,
            msg='Failed to remove item from settings.'
        )

        settings.remove(('option1', 'option2'))
        self.assertDictEqual(
            settings.settings,
            {},
            msg='Failed to remove list of items from settings.'
        )

        settings.set_list(self.test_values)
        settings.clear()
        self.assertDictEqual(
            settings.settings,
            {},
            msg='Failed to clear all items from settings.'
        )

        settings.set_list(self.test_values)
        settings.clear_values()
        self.assertDictEqual(
            settings.settings,
            {k: '' for k, _ in self.test_values},
            msg='Failed to clear all values.'
        )

        settings.set_list(self.test_values)
        clearopts = 'option1', 'option2'
        settings.clear_values(lst_options=clearopts)
        self.assertDictEqual(
            {k: ('' if k in clearopts else v) for k, v in self.test_values},
            settings.settings,
            msg='Failed to clear specified values.'
        )

    def test_set_get_value(self):
        """ EasySettings sets/reads str and non-str values. """

        settings = EasySettings()
        test_values = [
            ('opt{}'.format(i), v) for i, v in enumerate((
                'hello world',
                1337,
                3.14,
                ['a', 'b', 'c'],
                (1, 2, 3),
                {'key': 'value'},
                True,
                False,
            ))
        ]

        for opt, val in test_values:
            settings.set(opt, val)
            self.assertEqual(
                val,
                settings.settings[opt],
                msg='Failed to set value ({}): {}'.format(type(opt), val)
            )
        settings.save(self.testfile)

        # Reload from disk
        settings = EasySettings(self.testfile)
        self.assertTrue(
            bool(settings),
            msg='Failed to load settings for test!')

        self.assertListEqual(
            sorted(test_values),
            sorted(settings.list_settings()),
            msg='Settings differed after saving to disk!')

    def test_get_defaults(self):
        """ get() returns correct default values. """
        settings = EasySettings()
        for default in ('', False, True, None, 1, {}, [], 3.14):
            val = settings.get('nonexistent', default=default)
            if default in (False, True, None):
                self.assertIs(
                    val,
                    default,
                    msg='get() failed with default value {}: {}'.format(
                        default,
                        val,
                    )
                )
            else:
                self.assertEqual(
                    val,
                    default,
                    msg='get() failed with default value {}: {}'.format(
                        default,
                        val,
                    ),
                )

        val = settings.get('nonexistent')
        self.assertEqual(
            val,
            '',
            msg='get() should return empty str on nonexistent values',
        )

    def test_get_bool(self):
        """ get_bool() returns correct values. """
        vals = {
            True: ('true', 'yes', 'on', '1'),
            False: ('false', 'no', 'off', '0'),
        }
        for expected, vals in vals.items():
            for val in vals:
                settings = EasySettings()
                settings.set('boolopt', val)
                setval = settings.get_bool('boolopt')
                self.assertEqual(
                    setval,
                    expected,
                    msg='get_bool() failed for {} value: {}'.format(
                        expected,
                        setval,
                    ),
                )

    def test_get_bool_defaults(self):
        """ get_bool() should return correct default values. """
        settings = EasySettings()
        for default in (True, False):
            val = settings.get_bool('nonexistent', default=default)
            self.assertEqual(
                val,
                default,
                msg='get_bool(default={}) failed.'.format(default),
            )


if __name__ == '__main__':
    print('\n'.join((
        'Testing EasySettings v. {esver}',
        'Using Python {v.major}.{v.minor}.{v.micro}.',
    )).format(esver=version(), v=sys.version_info))

    sys.exit(unittest.main(argv=sys.argv))
