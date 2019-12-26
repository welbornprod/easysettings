#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" yaml_settings.py

    ...Simple YAML settings class.
    Christopher Welborn 05-07-19
"""
try:
    import yaml
except ImportError:
    # Raise when used, not while importing. This module may not even be used.
    yaml = None

from .common_base import (
    load_settings,
    SettingsBase,
)

__all__ = ['YAMLSettings', 'load_yaml_settings']


def load_yaml_settings(filename, default=None, cls=None):
    """ Tries to create a YAMLSettings from a filename, but returns a new
        YAMLSettings instance if the file does not exist.

        This is a convenience function for the common try/catch block used
        when YAMLSettings is used for the first time.
        Instead of:
            try:
                config = YAMLSettings.from_file(myfile)
            catch FileNotFoundError:
                config = YAMLSettings()
                config.filename = myfile

        Just do this:
            config = load_yaml_settings(myfile)

        The `default` is merged into existing config, for keys that don't exist
        already.
    """
    return load_settings(cls or YAMLSettings, filename, default=default)


class YAMLSettings(SettingsBase):
    """ This is a UserDict with methods to load/save in YAML format.
        The YAML data must be a dict, and all dict keys and values must be
        compatible with YAML serialization.
    """
    def __init__(
            self, iterable=None, filename=None,
            _dict=dict,
            **kwargs):
        """ Initialize a YAMLSettings instance like a `dict`, with optional
            `translate` and `object_pairs_hook` arguments for pyyaml.
        """
        if yaml is None:
            # pyyaml was not imported, and you are trying to use this class.
            raise ImportError(
                'pyyaml could not be imported. Install it with `pip`?'
            )
        super(YAMLSettings, self).__init__(
            iterable=iterable,
            filename=filename,
            **kwargs
        )
        self._dict = _dict

    @classmethod
    def from_file(cls, filename):
        """ Return a new YAMLSettings from a YAML file.
            Arguments:
                filename  : File name to read.

            All open() and json.load() exceptions are propagated.
        """
        settings = cls(filename=filename)
        settings.load()
        return settings

    def load(self, filename=None):
        """ Load this dict from a YAML file.
            Raises the same errors as open() and json.load().
        """
        super(YAMLSettings, self).load(yaml, filename=filename)

    def save(self, filename=None):
        """ Save this dict to a YAML file.
            Raises the same errors as open() and json.dump().
        """
        super(YAMLSettings, self).save(yaml, filename=filename)

    def setsave(self, option, value, filename=None):
        """ The same as calling .set() and then .save(). """
        super(YAMLSettings, self).setsave(filename=filename)
