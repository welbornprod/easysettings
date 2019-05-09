# EasySettings

EasySettings allows you to easily save and retrieve simple application settings.
Handles non-string types like boolean, integer, long, list, as well as normal
string settings. No sections needed, just set(), get(), and save().

There are [other `*Settings` objects](#jsonsettings-tomlsettings-and-yamlsettings)
that allow you to use a standard format, such as:

* [JSONSettings](#jsonsettings-example) - `UserDict` that has methods to load/save
config in JSON format. `load_json_settings()` is the preferred method for loading
config files.

* [TOMLSettings](#tomlsettings-example) - `UserDict` that has methods to load/save
config in TOML format. `load_toml_settings()` is the preferred method for loading
config files.

* [YAMLSettings](#yamlsettings-example) - `UserDict` that has methods to load/save
config in YAML format. `load_yaml_settings()` is the preferred method for loading
config files.


## Bug Fixes

* Version 3.2.0:

New config formats were added, like `JSONSettings` you can now use
`TOMLSettings` (through the `toml` package) and `YAMLSettings` (through the
`pyyaml` package).

It should be possible to use `EasySettings` and `JSONSettings` without these
new dependencies. They are only required if you want the new `*Settings`
formats.

* Version 3.0.0:

Custom `JSONEncoder`/`JSONDecoder` classes can be used in `JSONSettings`, and
settings/items can be hooked after decoding/loading or before encoding/saving.

This allows you to modify the values in any way you see fit by subclassing.


## Examples

Example of Easy Settings basic usage:

```python
#!/usr/bin/env python
# --------------- Creation ----------------

from easysettings import EasySettings

settings = EasySettings("myconfigfile.conf")

# configfile_exists() checks for existing config, and creates one if needed.
# ** this function is called automatically now when a filename is passed to easysettings. **
# if you wish to disable it, just do: settings = EasySettings() and set
# settings.configfile later.

# ------------- Basic Functions -----------
# set without saving
settings.set("username", "cjw")
settings.set("firstrun", False)

print settings.get("username")
# this results in "cjw"

# check if file is saved
if not settings.is_saved():
    print "you haven't saved the settings to disk yet."

# ...settings are still available even if they haven't
#    been saved to disk

# save
settings.save()

# you may also set & save in one line...
settings.setsave("homedir", "/myuserdir")
```

### Advanced:

```python
    # check if setting exists if you want
    if settings.has_option('username'):
        print "Yes, settings has 'username'"

    # list settings/options/values
    mysettings = settings.list_settings()
    myoptions = settings.list_options()
    myvalues = settings.list_values()

    # remove setting
    settings.remove('homedir')

    # clear all option names and values
    settings.clear()

    # clear all values, leave option names.
    settings.clear_values()
```

### Comparison:

```python
# compare two settings objects
settings2 = EasySettings('myconfigfile2.conf')

if settings.compare_opts(settings2):
    print "these have the same exact options, values may differ"
if settings.compare_vals(settings2):
    print "these have the exact same values, options may differ"

if settings == settings2:
    print "these have the exact same settings/values"
    # can also be written as settings.compare_settings(settings2)
    # if you like typing.. :)

if settings > settings2:
    print "settings has more options than settings2"
# all of them work ==, !=, <=, >= , > , <
# ... the < > features are based on amount of options.
#     the = features are based on option names and values.
```

## Features

Easy Settings has the basic features you would expect out of a settings module,
and it's very easy to use. If your project needs to save simple settings without
the overhead and complication of other modules then this is for you. Save, load, set, &
get are very easy to grasp. The more advanced features are there for you to use,
but don't get in the way. Settings, options, & values can be listed, searched,
detected, removed, & cleared.

Easy Settings uses a dictionary to store settings before writing to disk, so you can
also access settings like a dictionary object using ``easysettings.settings``. The
``setsave()`` function will save every time you set an option, and ``is_saved()`` will
tell you whether or not the file has been saved to disk yet. Code is documented for a
newbie, so a ``help('EasySettings')`` in the python console will get you started.


The search_query argument in the list functions lets you find settings, options, and values by search string:

```python
mydebugoptions = settings.list_options('debug')
# clear all debug values..
settings.clear_values(mydebugoptions)
```

Non-string types were added, so any type that can be pickled can be used as an
option's value. This includes all the major types like int, long, float, boolean, and list.
All of these values will be retrieved as the same type that was set:

```python
es = EasySettings('myconfigfile.conf')

# Boolean
es.set("newuser", True)
if es.get('newuser'):
    print "now you can use get() as a boolean."

# Integer
es.set('maxwidth', 560)
halfwidth = es.get('maxwidth') / 2 # this math works.

# Float
es.set('soda', 1.59)
f_withtax = es.get('soda') * 1.08

# List
es.set('users', ['cjw', 'joseph', 'amy']) # lists as settings, very convenient
for suser in es.get('users'):
    print "retrieved user name: " + suser

# i won't do them all, but if you can pickle it, you can use it with easysettings.
```

Errors are more descriptive and can be caught using their proper names:

```python
try:
    es.get('option_with_a_possibly_illegal_value')
except easysettings.esGetError as exErr:
    print "Error getting option!"
except Exception as exEx:
    print "General Error!"
```

## Automatic Creation:


If you pass a file name to EasySettings(), the ``configfile_exists()`` function is called. This
function will create a blank config file if the file doesn't exist, otherwise it will return True.
To use the 'automatic creation' do this:

```python
settings = EasySettings('myconfigfile.conf')
# if file exists, all settings were loaded.
# if file did not exist, it was created.
# No permissions, disk-full, and other errors are still possible of course
# depending on the machine, or the current directory permissions.
```

You can disable the 'automatic creation' features by not passing a file name, and loading seperately
like this:

```python
settings = EasySettings()
settings.configfile = 'myconfigfile.conf'
# file has not been created or loaded.
# file must exist before calling 'load_file'
if settings.load_file():
    # all settings were loaded.
else:
    # unable to load file for some reason.
```

This will work in the same way to disable the automatic creation:

```python
settings = EasySettings()
# file has not been created or loaded.
# file 'myconfigfile.conf' must exist before calling load_file()
if settings.load_file('myconfigfile.conf'):
    # file was loaded.
    # settings.configfile was set by the load_file() function
else:
    # file could not be loaded.
```

To check if the file exists without creating it automatically you can do this:

```python
if not settings.configfile_exists(False):
    print 'config file does not exist, and was not created.'
# I actually prefer the os.path.isfile() method if you're not going to automatically
# create the file.
import os.path
if not os.path.isfile(settings.configfile):
    print 'config file does not exist, and was not created.'
```

# JSONSettings, TOMLSettings, and YAMLSettings:

All of the `*Settings` objects are simple `UserDict`s that allow loading and saving
in the specified format. All keys and values must be serializable using the
specified format.

## JSONSettings Example:

```python
from easysettings import JSONSettings

# Starting from scratch:
js = JSONSettings(filename='myfile.json')
js['option'] = 'value'
js.save()
```

```python
from easysettings import JSONSettings, load_json_settings
# Loading settings that may not exist yet:
js = load_json_settings('myfile.json', default={'option': 'mydefault'})
print(js['option'])

# Set an item and save the settings.
js.setsave('option2', 'value2', sort_keys=True)

# Alternate load method, may raise FileNotFoundError.
js = JSONSettings.from_file('myjsonfile.json')
```

The same goes for `TOMLSettings` and `YAMLSettings`.

## TOMLSettings Example:

```python
# `toml` must be installed, though you don't have to import it.
import toml

from easysettings import TOMLSettings

# Starting from scratch:
ts = TOMLSettings(filename='myfile.toml')
ts['option'] = 'value'
ts.save()
```

```python
from easysettings import TOMLSettings, load_toml_settings

# Loading settings that may not exist yet:
ts = load_toml_settings('myfile.toml', default={'option': 'mydefault'})
print(ts['option'])

# Set an item and save the settings.
ts.setsave('option2', 'value2')

# Alternate load method, may raise FileNotFoundError.
ts = TOMLSettings.from_file('mytomlfile.toml')
```

## YAMLSettings Example:

```python
# `pyyaml` must be installed, though you don't have to import it.
import yaml
from easysettings import YAMLSettings

# Starting from scratch:
ys = YAMLSettings(filename='myfile.yaml')
ys['option'] = 'value'
ys.save()
```

```python
from easysettings import YAMLSettings, load_yaml_settings

# Loading settings that may not exist yet:
ys = load_yaml_settings('myfile.yaml', default={'option': 'mydefault'})
print(ys['option'])

# Set an item and save the settings.
ys.setsave('option2', 'value2')

# Alternate load method, may raise FileNotFoundError.
ys = YAMLSettings.from_file('myyamlfile.yaml')
```

# PyPi Package

Full PyPi package available at: http://pypi.python.org/pypi/EasySettings

Use pip to install Easy Settings to be used globally.
Ubuntu instructions to install pip:

```bash
sudo apt-get install python-pip
```

After that you should be able to install Easy Settings by typing:

```bash
sudo pip install easysettings
```

# Source Code

You can view the source for this package at: https://github.com/welbornprod/easysettings


# Website

Be sure to visit http://welbornprod.com for more projects and information from Welborn Productions.

# Notes

Since you've scrolled all the way down here, I thought I would tell you that
the `EasySettings` class itself was created a long time ago, when I was still
learning Python. I don't use that specific class anymore. I prefer to use the
other `*Settings` classes in the `easysettings` package.
I've been fixing bugs and adding features in all of the `easysettings` code for
years now, so I don't want to say that it's "abandoned" or "deprecated".
It was designed for me at the time, a beginner, so maybe it's still useful for
beginners, but the other classes are much cleaner and not so opinionated. They're
also widely accepted config formats, where the `EasySettings` format (a mix of
custom `INI` and Python's `pickle`) is not. They raise exceptions instead of
silently trying to "do the right thing".

It's better to be explicit than implicit.

