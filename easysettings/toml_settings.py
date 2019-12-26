#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" toml_settings.py

    ...Simple TOML settings class.
    * Must have the `toml` package installed (from pip). Not `pytoml`!.
    Christopher Welborn 05-07-19
"""
try:
    import toml
except ImportError:
    # Raise when used, not while importing. This module may not even be used.
    toml = None

from .common_base import (
    SettingsBase,
    load_settings,
)

__all__ = ['TOMLSettings', 'load_toml_settings']


def default_translate(strtype, strvalue, value):
    """ Default `translate` function for pytoml. """
    return value


def load_toml_settings(
        filename, default=None,
        _dict=dict,
        cls=None):
    """ Tries to create a TOMLSettings from a filename, but returns a new
        TOMLSettings instance if the file does not exist.

        This is a convenience function for the common try/catch block used
        when TOMLSettings is used for the first time.
        Instead of:
            try:
                config = TOMLSettings.from_file(myfile)
            catch FileNotFoundError:
                config = TOMLSettings()
                config.filename = myfile

        Just do this:
            config = load_toml_settings(myfile)

        The `default` is merged into existing config, for keys that don't exist
        already.
    """
    return load_settings(
        cls or TOMLSettings,
        filename,
        default=default,
        _dict=_dict,
    )


class TOMLSettings(SettingsBase):
    """ This is a UserDict with methods to load/save in TOML format.
        The TOML data must be a dict, and all dict keys and values must be
        compatible with TOML serialization.
    """
    def __init__(
            self, iterable=None, filename=None,
            _dict=dict,
            **kwargs):
        """ Initialize a TOMLSettings instance like a `dict`, with optional
            `translate` and `object_pairs_hook` arguments for pytoml.
        """
        if toml is None:
            # pytoml was not imported, and you are trying to use this class.
            raise ImportError(
                'toml could not be imported. Install it with `pip`?'
            )
        super(TOMLSettings, self).__init__(
            iterable=iterable,
            filename=filename,
            **kwargs
        )
        self._dict = _dict

    @classmethod
    def from_file(cls, filename, _dict=dict):
        """ Return a new TOMLSettings from a TOML file.
            Arguments:
                filename  : File name to read.

            All open() and json.load() exceptions are propagated.
        """
        settings = cls(filename=filename, _dict=_dict)
        settings.load()
        return settings

    def load(self, filename=None):
        """ Load this dict from a TOML file.
            Raises the same errors as open() and json.load().
        """
        super(TOMLSettings, self).load(toml, _dict=self._dict)

    def save(self, filename=None):
        """ Save this dict to a TOML file.
            Raises the same errors as open() and json.dump().
        """
        super(TOMLSettings, self).save(toml, filename=filename)

    def setsave(self, option, value, filename=None):
        """ The same as calling .set() and then .save(). """
        super(TOMLSettings, self).setsave(filename=filename)
