#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_jsonsettings.py
    Unit tests for EasySettings - JSONSettings

    -Christopher Welborn 05-07-2019
"""
import json
import os
import sys
import tempfile
import unittest

from . import (
    __version__ as version,
    JSONSettings,
    load_json_settings,
)

try:
    FileNotFoundError
except NameError:
    # Python 2.7.
    FileNotFoundError = IOError


class JSONSettingsTests(unittest.TestCase):
    """ Tests pertaining to JSONSettings. """

    def setUp(self):
        # Setup a test json file to work with.
        self.rawdict = {'option1': 'value1', 'option2': 'value2'}
        fd, fname = self.make_tempfile()
        os.write(fd, json.dumps(self.rawdict, indent=4).encode())
        os.close(fd)
        self.testfile = fname

    def make_tempfile(self):
        return tempfile.mkstemp(suffix='.json', prefix='easysettings.')

    def test_encoder_decoder(self):
        """ JSONSettings should support custom JSONEncoders/Decoders. """
        fd, fname = self.make_tempfile()
        os.close(fd)
        settings = JSONSettings(
            self.rawdict,
            decoder=CustomDecoder,
            encoder=CustomEncoder,
        )
        test_val = CustomString('{a}, {b}, {c}')
        settings['my_str_list'] = test_val
        settings.save(filename=fname)

        notencoded = JSONSettings.from_file(fname)
        self.assertListEqual(
            notencoded['my_str_list'],
            ['a', 'b', 'c'],
            msg='Custom encoder failed.'
        )

        decoded = JSONSettings.from_file(fname, decoder=CustomDecoder)
        self.assertEqual(
            decoded['my_str_list'],
            test_val,
            msg='Custom decoder failed:\n{dec!r} != {enc!r}'.format(
                dec=decoded['my_str_list'].data,
                enc=test_val.data,
            )
        )

    def test_get(self):
        """ JSONSettings.get should raise on missing keys. """
        settings = JSONSettings(self.rawdict)
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
        """ JSONSettings load/save hooks should work. """
        fd, fname = self.make_tempfile()
        os.close(fd)
        teststr = 'testing'
        settings = JSONSettings_Hooks(
            {'hook_test_1': teststr},
        )
        settings.save(filename=fname)

        nothooked = JSONSettings.from_file(fname)
        self.assertEqual(
            nothooked['hook_test_1'],
            '!{}'.format(teststr),
            msg='Failed to hook item on save: {!r}'.format(
                nothooked['hook_test_1'],
            )
        )

        hooked = JSONSettings_Hooks.from_file(fname)
        self.assertEqual(
            hooked['hook_test_1'],
            teststr,
            msg='Failed to hook item on load: {!r}'.format(
                nothooked['hook_test_1'],
            )
        )

    def test_json_load_save(self):
        """ JSONSettings loads and saves JSON files """
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

        with self.assertRaises(FileNotFoundError, msg='Didn\'t raise on load!'):
            settings = JSONSettings.from_file('NONEXISTENT_FILE')

    def test_load_json_settings(self):
        """ load_json_settings should ignore FileNotFound and handle defaults.
        """
        try:
            settings = load_json_settings('NONEXISTENT_FILE')
        except FileNotFoundError:
            self.fail(
                'load_json_settings should not raise FileNotFoundError.'
            )
        # Settings should still load, even when the file doesn't exist.
        self.assertIsInstance(settings, JSONSettings)
        # Settings should be an empty JSONSettings.
        self.assertFalse(bool(settings))

        # Default values should not override existing values.
        settings = load_json_settings(
            self.testfile,
            default={'option1': 'SHOULD_NOT_SET'},
        )
        self.assertDictEqual(
            self.rawdict, settings.data,
            msg='Failed to load dict settings from file with default key.'
        )
        # Default values should be added when not set.
        settings = load_json_settings(
            self.testfile,
            default={'option1': 'SHOULD_NOT_SET', 'option3': 'SHOULD_SET'},
        )

        d = {k: self.rawdict[k] for k in self.rawdict}
        d['option3'] = 'SHOULD_SET'
        self.assertDictEqual(
            d, settings.data,
            msg='Failed to add default setting.'
        )


class CustomDecoder(json.JSONDecoder):
    def __init__(self, **kwargs):
        kwargs['object_hook'] = self.object_hooker
        super(CustomDecoder, self).__init__(**kwargs)

    def object_hooker(self, o):
        modified = {}
        for k, v in o.items():
            if isinstance(v, list):
                modified[k] = CustomString(
                    ', '.join('{{{}}}'.format(s) for s in v)
                )
            else:
                modified[k] = v
        return modified


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, CustomString):
            items = [x.strip()[1:-1] for x in o.data.split(',')]
            return items
        return super(CustomEncoder, self).default(o)


class CustomString(object):
    def __init__(self, data):
        self.data = str(data)

    def __eq__(self, other):
        return isinstance(other, CustomString) and (self.data == other.data)


class JSONSettings_Hooks(JSONSettings):
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
