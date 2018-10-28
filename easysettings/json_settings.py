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

__all__ = ['JSONMixin', 'JSONSettings', 'load_json_settings']


def load_json_settings(filename, default=None):
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
    """
    try:
        config = JSONSettings.from_file(filename)
    except FileNotFoundError:
        config = JSONSettings()
        config.filename = filename
    # Set any defaults passed in, if not already set.
    for k in (default or {}):
        config.setdefault(k, default[k])
    return config


class JSONMixin(object):

    """ This mixin provides two methods that both operate on `self.data`.
            `self.load(filename=None)`
            `self.save(filename=None, sort_keys=False)`
        These will load and save `self.data` in JSON format.

        If the attribute `self.filename` does not exist, it will be created
        when a filename is passed to `load` or `save`. If either is called
        without arguments, `self.filename` is used.

        All data must be compatible with JSON serialization.
    """

    def load(self, filename=None):
        """ Load this dict from a JSON file.
            Raises the same errors as open() and json.load().
        """
        if filename or not getattr(self, 'filename', None):
            self.filename = filename

        if not self.filename:
            raise ValueError('`filename` must be set.')

        with open(self.filename, 'r') as f:
            data = json.load(f)

        if data is None:
            # JSON null.
            data = {}

        if not isinstance(data, dict):
            raise TypeError(
                'Data was replace with non dict type, got: {}'.format(
                    type(data)))
        self.data = data

    def save(self, filename=None, sort_keys=False):
        """ Save this dict to a JSON file.
            Raises the same errors as open() and json.dump().
        """
        if filename or not getattr(self, 'filename', None):
            self.filename = filename

        if not self.filename:
            raise ValueError('`filename` must be set.')

        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4, sort_keys=sort_keys)


class JSONSettings(UserDict, JSONMixin):

    """ This is a UserDict with methods to load/save in JSON format.
        The JSON data must be a dict, and all dict keys and values must be
        compatible with JSON serialization.
    """

    @classmethod
    def from_file(cls, filename):
        """ Return a new JSONSettings from a JSON file.
            Arguments:
                filename  : File name to read.

            All open() and json.load() exceptions are propagated.
        """
        settings = cls()
        settings.load(filename)
        return settings

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
