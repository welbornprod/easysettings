#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" test_yamlsettings.py
    Unit tests for YAMLSettings.

    -Christopher Welborn 05-08-2019
"""

import os
import sys
import unittest
import tempfile

import json
import toml
import yaml

from .common_base import (
    BackedUpWriter,
)
from .json_settings import (
    load_json_settings,
    JSONSettings,
)
from .toml_settings import (
    load_toml_settings,
    TOMLSettings,
)
from .yaml_settings import (
    load_yaml_settings,
    YAMLSettings,
)

try:
    FileNotFoundError
except NameError:
    # Python 2.7.
    FileNotFoundError = IOError


class BackedUpWriterTests(unittest.TestCase):
    """ Tests for the BackedUpWriter class. """
    def setUp(self):
        self.fmt = '{}~'

    def make_temp_file(self):
        return tempfile.mkstemp(
            suffix='.txt',
            prefix='easysettings.BackedUpWriter.'
        )

    def make_temp_filename(self):
        return tempfile.mktemp(
            suffix='.txt',
            prefix='easysettings.BackedUpWriter.',
        )

    def test_backs_up(self):
        """ Should backup files while opening a file in write mode. """
        fd, fname = self.make_temp_file()
        os.write(fd, 'Test Content'.encode())
        os.close(fd)

        backupname = self.fmt.format(fname)
        with BackedUpWriter(fname, fmt=self.fmt) as f:
            self.assertTrue(
                os.path.exists(backupname),
                msg='Failed to create backup file: {}'.format(backupname),
            )
            f.write('Changed Content')

        # Everything went okay, backup file should be gone.
        self.assertFalse(
            os.path.exists(backupname),
            msg='Failed to remove backup file: {}'.format(backupname),
        )
        with open(fname, 'r') as f:
            self.assertEqual(
                f.read(),
                'Changed Content',
                msg='Writing without errors resulted in a bad file!',
            )

    def test_new_files(self):
        """ Should remove new files when errors occur while creating them. """
        newfilename = self.make_temp_filename()
        backupname = self.fmt.format(newfilename)
        try:
            with BackedUpWriter(newfilename, fmt=self.fmt) as f:
                f.write('APPLE BANANA CIDER')
                raise ValueError('Raising an error to trigger file removal.')
        except ValueError:
            pass

        self.assertFalse(
            os.path.exists(newfilename),
            msg='Failed to remove new file on errors.',
        )
        self.assertFalse(
            os.path.exists(backupname),
            msg='Shouldn\'t have created a backup for a new file.',
        )

    def test_restores(self):
        """ Should restore original files on error. """
        fd, fname = self.make_temp_file()
        os.write(fd, 'Test Content'.encode())
        os.close(fd)
        fmt = '{}~'
        backupname = fmt.format(fname)
        try:
            with BackedUpWriter(fname, fmt=fmt) as f:
                f.write('BLAH BLAH BLAH')
                raise ValueError('Raising an error to trigger restore.')
        except ValueError:
            pass
        self.assertFalse(
            os.path.exists(backupname),
            msg='Failed to remove/restore the backup file: {}'.format(
                backupname,
            ),
        )
        with open(fname, 'r') as f:
            self.assertEqual(
                f.read(),
                'Test Content',
                msg='Failed to restore backed up content from: {}'.format(
                    fname,
                ),
            )


class SettingsBaseTests(object):
    """ Tests pertaining to subclasses of SettingsBase. """
    module = None
    extension = '.testfile'
    settings_hook = None
    settings_cls = None

    def setUp(self):
        """ Setup a test {format} file to work with. """
        self.rawdict = {'option1': 'value1', 'option2': 'value2'}
        fname = self.make_temp_filename()
        with open(fname, 'w') as f:
            self.module.dump(self.rawdict, f)
        self.testfile = fname

        self.settings_hook = create_settings_hook(self.settings_cls)

    def make_temp_file(self):
        return tempfile.mkstemp(
            suffix='.{}'.format(
                self.extension.lstrip('.') or self.module.__name__
            ),
            prefix='easysettings.'
        )

    def make_temp_filename(self):
        return tempfile.mktemp(
            suffix='.txt',
            prefix='easysettings.BackedUpWriter.',
        )

    def test_get(self):
        """ .get() should raise on missing keys. """
        settings = self.settings_cls(self.rawdict)
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
            msg='.get() failed to return default value!',
        )

    def test_getattr(self):
        """ __getattr__ should return valid keys, and raise on invalid. """
        settings = self.settings_cls(self.rawdict)
        raisecatch = self.assertRaises(
            AttributeError,
            msg='getattr() failed to raise AttributeError!',
        )
        with raisecatch:
            settings.does_not_exist

        try:
            settings.option1
        except AttributeError:
            self.fail('getattr() raised AttributeError on a valid key!')

    def test_hooks(self):
        """ load/save hooks should work. """
        fname = self.make_temp_filename()
        teststr = 'testing'
        settings = self.settings_hook(
            {'hook_test_1': teststr},
        )
        settings.save(filename=fname)

        nothooked = self.settings_cls.from_file(fname)
        self.assertEqual(
            nothooked['hook_test_1'],
            '!{}'.format(teststr),
            msg='Failed to hook item on save: {!r}'.format(
                nothooked['hook_test_1'],
            ),
        )

        hooked = self.settings_hook.from_file(fname)
        self.assertEqual(
            hooked['hook_test_1'],
            teststr,
            msg='Failed to hook item on load: {!r}'.format(
                nothooked['hook_test_1'],
            ),
        )

    def test_load_save(self):
        """ loads and saves files """
        settings = self.settings_cls.from_file(self.testfile)
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
            msg='Could not find new option in saved data!',
        )

        with self.assertRaises(FileNotFoundError, msg='Didn\'t raise on load!'):
            settings = self.settings_cls.from_file('NONEXISTENT_FILE')

    def test_load_settings(self):
        """ load_settings should ignore FileNotFound and handle defaults.
        """
        try:
            settings = self.load_func('NONEXISTENT_FILE')
        except FileNotFoundError:
            self.fail(
                'load_toml_settings should not raise FileNotFoundError.'
            )
        # Settings should still load, even when the file doesn't exist.
        self.assertIsInstance(settings, self.settings_cls)
        # Settings should be an empty SettingsBase instance/subclassed.
        self.assertFalse(bool(settings))

        # Default values should not override existing values.
        settings = self.load_func(
            self.testfile,
            default={'option1': 'SHOULD_NOT_SET'},
        )
        self.assertDictEqual(
            self.rawdict, settings.data,
            msg='Failed to load dict settings from file with default key.',
        )
        # Default values should be added when not set.
        settings = self.load_func(
            self.testfile,
            default={'option1': 'SHOULD_NOT_SET', 'option3': 'SHOULD_SET'},
        )

        d = {k: self.rawdict[k] for k in self.rawdict}
        d['option3'] = 'SHOULD_SET'
        self.assertDictEqual(
            d, settings.data,
            msg='Failed to add default setting.',
        )

    def test_setattr(self):
        """ setattr() should work for config keys and normal attributes. """
        settings = self.settings_cls(self.rawdict)
        # Key was set during init.
        settings.option1 = 'my_value'
        self.assertEqual(
            settings['option1'],
            'my_value',
            msg='Failed to set config key through attribute!',
        )

        # Not a key at all.
        settings.real_attr = 'my_real_value'
        self.assertNotIn(
            'real_attr',
            settings.data,
            msg='Shouldn\'t create config keys through attributes!',
        )

        # Key was set through the 'set()' method.
        settings.set('mykey', 'myvalue')
        self.assertEqual(
            settings.mykey,
            'myvalue',
        )

        settings.mykey = 'mynewvalue'
        self.assertEqual(
            settings['mykey'],
            'mynewvalue',
            msg='Failed to set config key through attribute!',
        )

        # Both real and config keys exist.
        settings.original_attr = 'original_value'
        settings['original_attr'] = 'config_value'

        self.assertEqual(
            settings.original_attr,
            'original_value',
            msg='getattr() should always return the real attribute.',
        )

        settings.original_attr = 'changed_value'
        self.assertEqual(
            settings['original_attr'],
            'config_value',
            msg='setattr() should always change the real attribute.',
        )
        self.assertEqual(
            settings.original_attr,
            'changed_value',
            msg='setattr() did not change the real attribute.',
        )


class JSONSettingsBaseTests(SettingsBaseTests):
    def test_encoder_decoder(self):
        """ JSONSettings should support custom JSONEncoders/Decoders. """
        fname = self.make_temp_filename()

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


def create_settings_hook(cls):
    """ Create a *Settings_Hook class to use with tests.
        It will have the proper name, dynamically created.
    """
    def load_item_hook(self, key, value):
        if key.startswith('hook_test'):
            return key, value[1:]

    def save_item_hook(self, key, value):
        if key.startswith('hook_test'):
            return key, '!{}'.format(value)

    return type(
        '{cls.__name__}_Hooks'.format(cls=cls),
        (cls, ),
        {
            'load_item_hook': load_item_hook,
            'save_item_hook': save_item_hook,
        }
    )


def create_suite(module, settings_cls, load_func, extension=None, bases=None):
    """ Create a test suite class for any subclass of SettingsBase. """
    testname = '{}Tests'.format(settings_cls.__name__)

    def cls_load_func(self, *args, **kwargs):
        return load_func(*args, **kwargs)

    bases = list(bases or [])
    for userbase in bases:
        if isinstance(userbase, SettingsBaseTests):
            break
    else:
        bases.append(SettingsBaseTests)
    bases.append(unittest.TestCase)

    return type(
        testname,
        tuple(bases),
        {
            'module': module,
            'extension': extension or '',
            'settings_cls': settings_cls,
            'load_func': cls_load_func,
        }
    )


# Tests for SettingsBase subclasses.
JSONSettingsTests = create_suite(
    json,
    JSONSettings,
    load_json_settings,
    extension='.json',
    bases=(JSONSettingsBaseTests, ),
)

TOMLSettingsTests = create_suite(
    toml,
    TOMLSettings,
    load_toml_settings,
    extension='.toml',
)

YAMLSettingsTests = create_suite(
    yaml,
    YAMLSettings,
    load_yaml_settings,
    extension='.yaml',
)


if __name__ == '__main__':
    unittest.main(argv=sys.argv, verbosity=2)
