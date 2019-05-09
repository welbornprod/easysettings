#!/usr/bin/env python3

""" EasySettings - Common Base Classes
    Common methods for *Settings classes.
    -Christopher Welborn 05-07-2019
"""
try:
    from collections import UserDict
except ImportError:
    # Python 2..
    from UserDict import UserDict

try:
    FileNotFoundError
except NameError:
    # Python 2..
    FileNotFoundError = EnvironmentError


class _NotSet(object):
    """ A value other than None to mean 'not set' or 'nothing'. """
    def __bool__(self):
        return False

    def __str__(self):
        return '<NotSet>'


# Singleton instance for identity comparison.
NotSet = _NotSet()


# Explicitly inheriting from `object` for Python 2.7. Not an old-style class.
class SettingsBase(UserDict, object):
    """ Base class for all *Settings classes. Holds shared methods. """
    def __init__(self, iterable=None, filename=None, **kwargs):
        """ Initialize a JSONSettings instance like a `dict`, with optional
            `encoder` and `decoder` arguments for
            JSONEncoder/JSONDecoder instances.
        """
        if iterable:
            self.data = dict(iterable)
        elif kwargs:
            self.data = {k: v for k, v in kwargs.items()}
        else:
            self.data = {}
        self.filename = filename or None

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
        self.data = self.load_hook(data)

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

        with open(self.filename, 'w') as f:
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

    def setsave(self, option, value, filename=None, **kwargs):
        """ The same as calling .set() and then .save(**kwargs). """
        self.set(option, value)
        self.save(filename=filename, **kwargs)
