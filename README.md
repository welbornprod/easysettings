EasySettings
=============

EasySettings allows you to easily save and retrieve simple application settings.
Handles non-string types like boolean, integer, long, list, as well as normal
string settings. No sections needed, just set(), get(), and save().

A JSONSettings object is also included to allow easily saving/retrieving
settings in JSON format.

Bug Fixes
---------

* Version 2.1.4:

    `get()` and `get_bool()` will honor default values when the key doesn't
    exist.
    Fixes Issue #3.

    Python 2 compatibility bug fixed.

* Version 2.1.0:

Added `bool(EasySettings())`. It's the same as `bool(EasySettings().settings)`.
Some other code was linted.

* Version 2.0.4:

Simplization/clean-up, added unit tests for comparison operators.

* Version 2.0.2:

The `repr()`for EasySettings was modified slightly to better represent python
syntax.

* Version 2.0.1:

Added unit tests and `JSONSettings`/`JSONMixin`.

`JSONSettings` is a `UserDict` with a few extra methods for saving settings as
JSON. It uses `JSONMixin` to achieve this.

You can `load()`, `save()`, and `setsave()` settings to/from a JSON file
as a dict. There is also a class method, `JSONSettings.from_file()` for loading
existing settings.

The `get()` function is just the native `dict.get()`, though a `set()`
function was added to make this more compatible with `EasySettings`. The
`__setitem__()` method is preferred (`mysettings[option] = value`) over `set()`.

* Version 1.9.3-5:

Added get_bool(option). Parses string values as booleans in a human friendly way.
Solves the `bool('false') != False` problem. This is not required because EasySettings
already saves boolean values. `settings.set('opt', False)` will already do
`settings.get('opt') == False`. This is for when you want to parse the values
`true/false`, `yes/no`, `on/off`, `1/0` as a boolean and get the correct result.
The strings are not case-sensitive.

By default, any value that is not a known `False` value is returned `True`,
though there is a `strict` option that will return `default` for unknown values.

When used on non-string values `bool(value)` is returned.

* Version 1.9.3-2:

Changed default returns in EasySettings.get().
None is a valid default return now.
Empty string will be returned if no default is set,
but any other default setting will be honored.

* Version 1.9.3:

Added `EasySettings.header` and initialization arguments.

Usage:

```python
appdesc = 'My beautiful application.\nUse wisely.'
settings = EasySettings('myfile.conf', name='MyApp', version='1.0.0', header=appdesc)
# or for an existing EasySettings() instance:
# settings.header = appdesc
settings.setsave('option', 'value')
```

Now when `save()` is called the configuration file will look like this:
```
# Configuration for MyApp v1.0.0
# My beautiful application.
# Use wisely.
option=value
```

* Version 1.9.2:

Package changes. Switched README to automatically convert markdown to rst
using pypandoc.

* Version 1.8.8:

Small changes were made to help compatibility issues between the old and new
package layouts. You can still do: `from easysettings import easysettings` and
then `easysettings.easysettings` if you have to. The new method is much better
though.


* Version 1.8.7:

Changed package layout. Instead of `from easysettings.easysettings import easysettings`,
the simple form of `from easysettings import EasySettings' can be used.
The main class has been given a proper class name.


* Version 1.8.6:

Fixed small bug in `setsave()` where `setsave('opt', False)` caused errors.


* Version 1.8.3:

Non-string types were not being loaded or saved
properly. All issues are resolved. The method has been enhanced so debug printing will be
'prettier'. Example of 'debug printing' settings:

```python
from easysettings import easysettings
settings = EasySettings('myconfigfile.conf')
settings.set('option', True)
settings.set('option2', ['cjw', 'amy', 'joseph'])
print settings
# this will now print as:
#     {'option': True, 'option2', ['cjw', 'amy', 'joseph']}
# instead of pickle's messed up looking strings like:
#    {'option': I01\n.  (for a True boolean value), ... }
```

This fix also allows you to save values with the newline character in them. So code like
this will work:

```python
settings.set('mytext', 'this\nstring\n\has\nnewlines.')
print settings.get('mytext')
# this will result in:
#     this
#    string
#    has
#    newlines.
```

Examples
--------

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

####Advanced:

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

####Comparison:

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

Features
--------

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
es = EasySettings('myconfigfile.conf)

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

Automatic Creation:
-------------------


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

JSONSettings:
=============

The `JSONSettings` object is a simple `UserDict` that allows loading and saving
in JSON format. All keys and values must be JSON serializable.

JSONSettings Example:

```python
from easysettings import JSONSettings

# Starting from scratch:
js = JSONSettings()
js['option'] = 'value'
js.save(filename='myfile.json')

# Loading existing settings:
js = JSONSettings()
js.load('myfile.json')
print(js['option'])

# Set an item and save the settings.
js.setsave('option2', 'value2', sort_keys=True)

# Alternate load method:
js = JSONSettings.from_file('myjsonfile.json')
```

PyPi Package
============

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

Source Code
===========

You can view the source for this package at: https://github.com/welbornprod/easysettings


Website
=======

Be sure to visit http://welbornprod.com for more projects and information from Welborn Productions.


[![I Love Open Source](http://www.iloveopensource.io/images/logo-lightbg.png)](http://www.iloveopensource.io/projects/53e6d33587659fce660044f9)
