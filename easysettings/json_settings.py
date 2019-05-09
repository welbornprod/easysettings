#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" json_settings.py

    ...Simple JSON settings class that uses a JSON mixin.
    Christopher Welborn 01-16-2015
"""

import json

from .common_base import (
    load_settings,
    SettingsBase,
)

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
    return load_settings(
        cls or JSONSettings,
        filename,
        default=default,
        encoder=encoder,
        decoder=decoder,
    )


class JSONSettings(SettingsBase):
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
        self.encoder = encoder
        self.decoder = decoder
        super(JSONSettings, self).__init__(
            iterable=iterable,
            filename=filename,
            **kwargs
        )

    @classmethod
    def from_file(cls, filename, encoder=None, decoder=None):
        """ Return a new JSONSettings from a JSON file.
            Arguments:
                filename  : File name to read.

            All open() and json.load() exceptions are propagated.
        """
        settings = cls(filename=filename, encoder=encoder, decoder=decoder)
        settings.load()
        return settings

    def load(self, filename=None):
        """ Load this dict from a JSON file.
            Raises the same errors as open() and json.load().
        """
        super(JSONSettings, self).load(json, cls=self.decoder)

    def save(self, filename=None, sort_keys=False):
        """ Save this dict to a JSON file.
            Raises the same errors as open() and json.dump().
        """
        super(JSONSettings, self).save(
            json,
            filename=filename,
            indent=4,
            sort_keys=sort_keys,
            cls=self.encoder,
        )

    def setsave(self, option, value, filename=None, sort_keys=False):
        """ The same as calling .set() and then .save(). """
        super(JSONSettings, self).setsave(
            filename=filename,
            sort_keys=sort_keys,
        )
