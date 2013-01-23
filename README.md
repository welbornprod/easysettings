Easy Settings
=============

Easy Settings allows you to easily save and retrieve simple application settings.

Full PyPi package available at: http://pypi.python.org/pypi/EasySettings


Local Use
=================
This file is hosted on github to be downloaded as a single-file module. If you include it in your project directory
you can import it by typing:

    import easysettings
    settings = easysettings.easysettings()

Example
=======
Example of Easy Settings usage::

    #!/usr/bin/env python
    # if using a local copy:
    import easysettings
    # use this method if pypi package is installed
    # from easysettings import easysettings

    settings = easysettings.easysettings("myconfigfile.conf")
    settings.configfile_create()
    
    settings.set("username", "cjw")
    
    print settings.get("username")
    # this results in "cjw"
    settings.save()
    # you may also set & save in one line...
    settings.setsave("username", "otheruser")

Features
========
Easy Settings has the basic features you would expect out of a settings module,
and it's very easy to use. If your project needs to save simple string settings without
the overhead and complication of other modules then this is for you. 

Easy Settings uses a dictionary to store settings before writing to disk, so you can
also access settings like a dictionary object using ``easysettings.settings``. This 
allows you to do things like this (where ``mysettings`` is an EasySettings instance)::
    
    for s_opt in mysettings.settings.iterkeys():
              print "Setting '" + s_opt + "' is set to '" + mysettings.settings[s_opt] + "'"
        # this results in: "Setting 'username' is set to 'otheruser'"

You can also retrieve a list of options & values strings::

    lst_settings = mysettings.list_settings()
    for itm in lst_settings:
              print itm
        # this results in "username=otheruser"
    
PyPi Package
============

Full PyPi package available at: http://pypi.python.org/pypi/EasySettings

Use pip to install Easy Settings to be used globally.
Ubuntu instructions to install pip:

    sudo apt-get install python-pip

After that you should be able to install Easy Settings by typing:

    sudo pip install easysettings

Website
=======
Be sure to visit http://welbornproductions.net for more projects and information from Welborn Productions.
