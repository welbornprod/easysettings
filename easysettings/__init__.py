#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  EasySettings
  An easy interface for setting and retrieving application settings.

Created on Jan 16, 2013

@author: Christopher Welborn
'''

from .easy_settings import (  # noqa
    EasySettings,
    __version__,
    esError,
    esGetError,
    esSetError,
    esCompareError,
    esSaveError,
    esValueError,
)
from .json_settings import (
    JSONSettings,
    load_json_settings,
)
from .toml_settings import (
    TOMLSettings,
    load_toml_settings,
)
__all__ = [
    'EasySettings',
    'JSONSettings',
    'TOMLSettings',
    'esCompareError',
    'esError',
    'esGetError',
    'esSaveError',
    'esSetError',
    'esValueError',
    'load_json_settings',
    'load_toml_settings',
]
