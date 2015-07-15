#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_easysettings.py
    Unit tests for EasySettings

    -Christopher Welborn 07-14-2015
"""

import json
import os
import sys
import tempfile
import unittest

from . import EasySettings, JSONSettings

# TODO: Comparison tests for EasySettings.


class EasySettingsTests(unittest.TestCase):
    """ Tests EasySettings functionality. """
    def setUp(self):
        # Set up a test configuration file to work with.
        fd, fname = tempfile.mkstemp(suffix='.conf', prefix='easysettings.')
        os.write(fd, '# Test settings.'.encode())
        os.close(fd)
        self.testfile = fname
        # Known values to test with.
        self.test_values = [
            ('option1', 'value1'),
            ('option2', 'value2'),
            ('option3', 'value3')
        ]

    def test_list_values(self):
        """ EasySettings handles lists of options and values """

        settings = EasySettings()
        settings.set_list(self.test_values)

        self.assertListEqual(
            list(settings.settings),
            sorted(settings.list_options()),
            msg='settings.list_options() differs from list(settings)'
        )

        self.assertListEqual(
            list(settings.settings.values()),
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
        """ Make sure EasySettings loads and saves """
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
        test_values = (
            (str(type(o)), o) for o in (
                'hello world',
                1337,
                3.14,
                ['a', 'b', 'c'],
                (1, 2, 3),
                {'key': 'value'},
                True
            ))
        for opt, val in test_values:
            settings.set(opt, val)
            self.assertEqual(
                val,
                settings.settings[opt],
                msg='Failed to set value ({}): {}'.format(opt, val)
            )


class JSONSettingsTests(unittest.TestCase):

    def setUp(self):
        # Setup a test json file to work with.
        self.rawdict = {'option1': 'value1', 'option2': 'value2'}
        fd, fname = tempfile.mkstemp(suffix='.json', prefix='easysettings.')
        os.write(fd, json.dumps(self.rawdict, indent=4).encode())
        os.close(fd)
        self.testfile = fname

    def test_json_load_save(self):
        """ Make sure JSON loads and saves with JSONSettings """
        settings = JSONSettings.from_file(self.testfile)
        self.assertDictEqual(
            self.rawdict, settings.data,
            msg='Failed to load dict settings from file.'
        )

        settings['option3'] = 'value3'
        settings.save()

        with open(self.testfile) as f:
            rawdata = f.read()

        self.assertTrue(
            ('option3' in rawdata) and ('value3' in rawdata),
            msg='Could not find new option in saved data!'
        )


if __name__ == '__main__':
    sys.exit(unittest.main(argv=sys.argv))