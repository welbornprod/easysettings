#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_tomlsettings.py
    Unit tests for EasySettings - TOMLSettings

    -Christopher Welborn 05-07-2019
"""
import pytoml
import os
import sys
import tempfile
import unittest

from . import (
    __version__ as version,
    TOMLSettings,
    load_toml_settings,
)

try:
    FileNotFoundError
except NameError:
    # Python 2.7.
    FileNotFoundError = IOError


class TOMLSettingsTests(unittest.TestCase):
    """ Tests pertaining to TOMLSettings. """

    def setUp(self):
        # Setup a test toml file to work with.
        self.rawdict = {'option1': 'value1', 'option2': 'value2'}
        fd, fname = self.make_tempfile()
        os.write(fd, pytoml.dumps(self.rawdict).encode())
        os.close(fd)
        self.testfile = fname

    def make_tempfile(self):
        return tempfile.mkstemp(suffix='.toml', prefix='easysettings.')

    def test_get(self):
        """ TOMLSettings.get should raise on missing keys. """
        settings = TOMLSettings(self.rawdict)
        # Non-existing key should raise.
        with self.assertRaises(KeyError, msg='.get() failed to raise!'):
            settings.get('NOT_AN_OPTION')
        # Existing key.
        val = settings.get('option1', None)
        self.assertEqual(
            val,
            'value1',
            msg='.get() failed to return an existing value!'
        )
        # Default should be honored.
        val = settings.get('NOT_AN_OPTION', default='test')
        self.assertEqual(
            val,
            'test',
            msg='.get() failed to return default value!'
        )

    def test_hooks(self):
        """ TOMLSettings load/save hooks should work. """
        fd, fname = self.make_tempfile()
        os.close(fd)
        teststr = 'testing'
        settings = TOMLSettings_Hooks(
            {'hook_test_1': teststr},
        )
        settings.save(filename=fname)

        nothooked = TOMLSettings.from_file(fname)
        self.assertEqual(
            nothooked['hook_test_1'],
            '!{}'.format(teststr),
            msg='Failed to hook item on save: {!r}'.format(
                nothooked['hook_test_1'],
            )
        )

        hooked = TOMLSettings_Hooks.from_file(fname)
        self.assertEqual(
            hooked['hook_test_1'],
            teststr,
            msg='Failed to hook item on load: {!r}'.format(
                nothooked['hook_test_1'],
            )
        )

    def test_toml_load_save(self):
        """ TOMLSettings loads and saves TOML files """
        settings = TOMLSettings.from_file(self.testfile)
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

        with self.assertRaises(FileNotFoundError, msg='Didn\'t raise on load!'):
            settings = TOMLSettings.from_file('NONEXISTENT_FILE')

    def test_load_toml_settings(self):
        """ load_toml_settings should ignore FileNotFound and handle defaults.
        """
        try:
            settings = load_toml_settings('NONEXISTENT_FILE')
        except FileNotFoundError:
            self.fail(
                'load_toml_settings should not raise FileNotFoundError.'
            )
        # Settings should still load, even when the file doesn't exist.
        self.assertIsInstance(settings, TOMLSettings)
        # Settings should be an empty TOMLSettings.
        self.assertFalse(bool(settings))

        # Default values should not override existing values.
        settings = load_toml_settings(
            self.testfile,
            default={'option1': 'SHOULD_NOT_SET'},
        )
        self.assertDictEqual(
            self.rawdict, settings.data,
            msg='Failed to load dict settings from file with default key.'
        )
        # Default values should be added when not set.
        settings = load_toml_settings(
            self.testfile,
            default={'option1': 'SHOULD_NOT_SET', 'option3': 'SHOULD_SET'},
        )

        d = {k: self.rawdict[k] for k in self.rawdict}
        d['option3'] = 'SHOULD_SET'
        self.assertDictEqual(
            d, settings.data,
            msg='Failed to add default setting.'
        )


class TOMLSettings_Hooks(TOMLSettings):
    def load_item_hook(self, key, value):
        if key.startswith('hook_test'):
            return key, value[1:]

    def save_item_hook(self, key, value):
        if key.startswith('hook_test'):
            return key, '!{}'.format(value)


if __name__ == '__main__':
    print('\n'.join((
        'Testing EasySettings v. {esver}',
        'Using Python {v.major}.{v.minor}.{v.micro}.',
    )).format(esver=version(), v=sys.version_info))
    unittest.main(argv=sys.argv, verbosity=2)
