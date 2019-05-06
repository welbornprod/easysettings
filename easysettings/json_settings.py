#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" json_settings.py
    version: 0.2.0

    ...Simple JSON settings class that uses a JSON mixin.
    Christopher Welborn 01-16-2015
"""

import json

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

__all__ = ['JSONSettings', 'load_json_settings']


def load_json_settings(
        filename, default=None, encoder=None, decoder=None, cls=None):
    """ Tries to create a JSONSettings from a filename, but returns a new
        JSONSettings instance if the file does not exist.

        This is a convenience function for the common try/catch block used
        when JSONSettings is used for the first time.
        Instead of:
            try:
                config = JSONSettings.from_file(myfile)
            catch FileNotFoundError:
                config = JSONSettings()
                config.filename = myfile

        Just do this:
            config = load_json_settings(myfile)

        The `default` is merged into existing config, for keys that don't exist
        already.
    """
    try:
        config = (cls or JSONSettings).from_file(
            filename,
            encoder=encoder,
            decoder=decoder,
        )
    except FileNotFoundError:
        config = JSONSettings(encoder=encoder, decoder=decoder)
        config.filename = filename
    # Set any defaults passed in, if not already set.
    for k in (default or {}):
        config.setdefault(k, default[k])
    return config


class _NotSet(object):
    """ A value other than None to mean 'not set' or 'nothing'. """
    def __bool__(self):
        return False

    def __str__(self):
        return '<NotSet>'


# Singleton instance for identity comparison.
NotSet = _NotSet()


class JSONSettings(UserDict):
    """ This is a UserDict with methods to load/save in JSON format.
        The JSON data must be a dict, and all dict keys and values must be
        compatible with JSON serialization.
    """
    def __init__(
            self, iterable=None, filename=None, encoder=None, decoder=None,
            **kwargs):
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
        self.encoder = encoder
        self.decoder = decoder

    @classmethod
    def from_file(cls, filename, encoder=None, decoder=None):
        """ Return a new JSONSettings from a JSON file.
            Arguments:
                filename  : File name to read.

            All open() and json.load() exceptions are propagated.
        """
        settings = cls(encoder=encoder, decoder=decoder)
        settings.load(filename=filename)
        return settings

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

    def load(self, filename=None):
        """ Load this dict from a JSON file.
            Raises the same errors as open() and json.load().
        """
        if filename or (not getattr(self, 'filename', None)):
            self.filename = filename

        if not self.filename:
            raise ValueError('`filename` must be set.')

        with open(self.filename, 'r') as f:
            data = json.load(f, cls=self.decoder)

        if data is None:
            # JSON null.
            data = {}

        if not isinstance(data, dict):
            raise TypeError(
                'Data was replace with non dict type, got: {}'.format(
                    type(data)))
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

    def save(self, filename=None, sort_keys=False):
        """ Save this dict to a JSON file.
            Raises the same errors as open() and json.dump().
        """
        filename = filename or getattr(self, 'filename', None)
        self.filename = filename

        if not self.filename:
            raise ValueError('`filename` must be set.')

        with open(self.filename, 'w') as f:
            json.dump(
                self.save_hook(self.data),
                f,
                indent=4,
                sort_keys=sort_keys,
                cls=self.encoder,
            )

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

    def setsave(self, option, value, filename=None, sort_keys=False):
        """ The same as calling .set() and then .save(). """
        self.set(option, value)
        self.save(filename=filename, sort_keys=sort_keys)
