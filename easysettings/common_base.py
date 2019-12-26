#!/usr/bin/env python3

""" EasySettings - Common Base Classes
    Common methods for *Settings classes.
    -Christopher Welborn 05-07-2019
"""

import os
import shutil
try:
    from collections import UserDict
except ImportError:
    # Python 2..
    from UserDict import UserDict

try:
    FileNotFoundError
except NameError:
    # Python 2..
    FileNotFoundError = IOError


class _NotSet(object):
    """ A value other than None to mean 'not set' or 'nothing'. """
    def __bool__(self):
        return False

    def __str__(self):
        return '<NotSet>'


# Singleton instance for identity comparison.
NotSet = _NotSet()


def load_settings(cls, filename, default=None, **kwargs):
    """ Tries to create a `cls` instance from a filename, but returns a new
        `cls` instance if the file does not exist.
         This handles common logic for all SettingsBase subclasses.

        This is a convenience function for the common try/catch block used
        when `cls` is used for the first time.
        Instead of:
            try:
                config = cls.from_file(myfile)
            catch FileNotFoundError:
                config = cls()
                config.filename = myfile

        Just do this:
            config = load_settings(cls, myfile)

        The `default` is merged into existing config, for keys that don't exist
        already.

        Arguments:
            cls       : The class instance to create.
            filename  : File path to load, or try to load.
            default   : Default dict for config keys/values.
                        Keys from an existing config file are merged into
                        this default dict.
            **kwargs  : Extra arguments for the class's `.from_file()` method,
                        and `cls.__init__()` (whichever is used).
    """
    defaults = default or {}
    try:
        # Existing file?
        config = cls.from_file(filename, **kwargs)
        # Set any defaults passed in, if not already set.
        for k, v in config.load_hook(defaults).items():
            config.setdefault(k, v)
        config.set_defaults(defaults)
    except FileNotFoundError:
        # New config, no file yet.
        config = cls(defaults, filename=filename, **kwargs)
    return config


# Explicitly inheriting from `object` for Python 2.7. Not an old-style class.
class SettingsBase(UserDict, object):
    """ Base class for all *Settings classes. Holds shared methods. """
    def __init__(self, iterable=None, filename=None, **kwargs):
        """ Initialize a SettingsBase instance like a `dict`, with optional
            `filename` argument (must be set before `save()` or `load()`,
            but can be set with those methods at the time).
        """
        if iterable:
            self.data = dict(iterable)
        elif kwargs:
            self.data = self.load_hook({k: v for k, v in kwargs.items()})
        else:
            self.data = {}
        self.filename = filename or None
        self.defaults = {}
        self.set_defaults(self.data)

    def __bool__(self):
        return bool(self.data)

    def __getattr__(self, key):
        """ Enable retrieval of settings through attributes. """
        if key in self.data:
            return self.data[key]
        raise AttributeError('{!s} has no attribute {!s}.'.format(
            type(self).__name__,
            key,
        ))

    def __setattr__(self, key, value):
        """ Enable setting of keys through attributes. """
        try:
            object.__getattribute__(self, key)
        except AttributeError:
            # Not an existing attribute.
            try:
                data = object.__getattribute__(self, 'data')
            except AttributeError:
                # No self.data yet.
                object.__setattr__(self, key, value)
            else:
                # A config key, not a real attribute.
                if key in data:
                    data[key] = value
                    return
        object.__setattr__(self, key, value)

    @classmethod
    def from_file(cls, filename):
        raise NotImplementedError('SettingsBase should not be used directly.')

    def get(self, option, default=NotSet):
        """ Like `dict.get`. Raises `KeyError` for missing keys if no
            default value is given.
        """
        val = self.data.get(option, NotSet)
        if val is NotSet:
            if default is NotSet:
                raise KeyError('Key does not exist: {}'.format(option))
            return default
        return val

    def load(self, module, filename=None, **kwargs):
        """ Load this dict from a file using `module`.load(f, **args).
            Raises the same errors as open() and `module`.load().
        """
        if filename or (not getattr(self, 'filename', None)):
            self.filename = filename

        if not self.filename:
            raise ValueError('`filename` must be set.')

        with open(self.filename, 'r') as f:
            data = module.load(f, **kwargs)

        if data is None:
            # Null/Empty.
            data = {}

        if not isinstance(data, dict):
            raise TypeError(
                'Data was replaced with non dict type, got: {}'.format(
                    type(data).__name__,
                )
            )
        # Replace existing values from __init__, add new ones.
        self.data.update(self.load_hook(data))

    def load_hook(self, data):
        """ Called on self.data after JSON decoding, before setting
            self.data.
            Can be overridden to modify self.data after decoding, before
            before setting self.data.
        """
        modified = {}
        for k, v in data.items():
            newk, newv = self.load_item_hook(k, v)
            modified[newk] = newv
        return modified

    def load_item_hook(self, key, value):
        """ Called on all keys/values after JSON decoding, before setting
            self.data[key] = value.
            Can be overridden to modify values after encoding.
        """
        return key, value

    def save(self, module, filename=None, **kwargs):
        """ Save this dict to a file using `module`.dump(**kwargs).
            Raises the same errors as open() and `module`.dump().
        """
        filename = filename or getattr(self, 'filename', None)
        self.filename = filename

        if not self.filename:
            raise ValueError('`filename` must be set.')

        with BackedUpWriter(self.filename) as f:
            module.dump(self.save_hook(self.data), f, **kwargs)

    def save_hook(self, data):
        """ Called on self.data before JSON encoding, before saving.
            Can be overridden to modify self.data before encoding/saving.
        """
        modified = {}
        for k, v in data.items():
            newk, newv = self.save_item_hook(k, v)
            modified[newk] = newv
        return modified

    def save_item_hook(self, key, value):
        """ Called on all keys/values before JSON encoding and saving.
            Can be overridden to modify values before encoding.
        """
        return key, value

    def set(self, option, value):
        """ Convenience function to match EasySettings behaviour.
            Though the __setitem__() (settings[option] = value) form is better.
            Arguments:
                option  : Option/key to set.
                value   : Value to set for the option/key.
        """
        self.data[option] = value

    def set_defaults(self, default_config):
        """ Save a copy of keys/value-types from `default_config` to optionally
            enforce config keys and value types later.
        """
        self.defaults = {
            k: type(v)
            for k, v in default_config.items()
        }

    def setsave(self, option, value, filename=None, **kwargs):
        """ The same as calling .set() and then .save(**kwargs). """
        self.set(option, value)
        self.save(filename=filename, **kwargs)


class BackedUpWriter(object):
    """ A context manager that backs up files when opening in write mode,
        and deletes the backup if no errors occurred while the file was open.
        If errors do occur, the backup is restored.

        If the file does not exist yet, no backup is made, but the file is
        deleted if errors occur.
    """
    def __init__(self, filename, fmt='{}~'):
        self.filename = filename
        self.fmt = fmt or '{}~'
        self.file = None
        self.filename_backup = None

    def __enter__(self):
        backupfile = self.fmt.format(self.filename)
        try:
            shutil.copy2(self.filename, backupfile)
        except FileNotFoundError:
            # The file doesn't exist yet.
            pass
        else:
            # Backup created.
            self.filename_backup = backupfile
        self.file = open(self.filename, 'w')
        return self.file

    def __exit__(self, typ, val, trace):
        try:
            self.file.close()
        except Exception:
            pass
        if self.filename_backup:
            # Backup was created.
            if val is None:
                # No errors, remove the backup.
                os.remove(self.filename_backup)
            else:
                # Errors occurred, restore the backup.
                shutil.move(self.filename_backup, self.filename)
        else:
            # No backup was created.
            if val is not None:
                # Errors occurred.
                try:
                    os.remove(self.filename)
                except FileNotFoundError:
                    # Never was created in the first place.
                    pass
