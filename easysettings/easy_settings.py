#!/usr/bin/env python3
import os
import re
import sys
import pickle
from datetime import date, datetime

# easy settings version
__version__ = '3.2.1'

# Python 3 compatibility flag
# ...we need this because pickle likes to use bytes in python 3, and strings
#    in python 2. We will be using strings because they fit the config file
#    format we have been using.
# see: safe_pickled_str(), safe_pickled_obj(), and their helper
# pickled_str()
if sys.version_info.major > 2:
    PYTHON3 = True
    # python 3 needs no long() function.
    long = int
else:
    PYTHON3 = False
# Safe ISO 8601 format for dates/datetimes.
ISO8601 = '%Y-%m-%dT%H:%M:%SZ'


class __NoValue(object):

    """ A 'not set yet' value to use other than None. """

    def __str__(self):
        return '<No Value>'

    def __repr__(self):
        return self.__str__()


# Singleton "not set yet" instance.
NoValue = __NoValue()


class EasySettings(object):

    """ Helper for saving/retrieving settings..

        Arguments:
            sconfigfile  : Config file to use (see __init__())
            name         : Name of your application (for config file header)
            version      : Version of your application (for config header)
            header       : Extra header for config file (description or notes)

        Attributes:
          configfile = configuration file to use
          settings   = dict object where settings are stored.
                       settings are retrieved like this:
                         myname = settings.settings["username"]
                         or:
                         myname = settings.get("username")
                       settings are set like this:
                         settings.settings["username"] = "cjwelborn"
                         or:
                         settings.set("username", "cjwelborn")
          name       = name for current project (for config file header)
          version    = version for current project (for config file header)
          header     = extra description text (for config file header)

        Example use:
            import easysettings
            settings = easysettings.EasySettings("myconfigfile.conf")
            settings.name = "My Project"
            settings.version = "1.0"
            # name & version are optional, they are only used in creating
            # a config file with '# configuration for My Project 1.0' as
            # the first line. if they are None, that line says
            # '# configuration'.

            settings.set("username", "cjwelborn")

            # settings can be retrieved without saving to disk first...
            s_user = settings.get("username")

            # settings can be saved to disk while setting an option
            settings.setsave("installdir", "/usr/share/easysettings")
    """
    # Pattern for detecting app name and version on config load.
    # Should stay consistent with the strings in self._build_header().
    confpat = re.compile(r'# Configuration for (.+)')

    def __init__(
            self, sconfigfile=None, name=None, version=None, header=None):
        """ Creates new settings object to work with.
            Arguments:
                sconfigfile  : File name to use for config.
                               If the file exists, it is loaded.
                               If the file doesn't exist, it is created.
                               If no file is given, you must set it manually:
                                   settings.configfile = 'myfile.conf'
                                   settings.load_file()
                               or:
                                   settings.load_file('myfile.conf')
                                   ..load_file() assumes the file exists.
                                   see: .configfile_exists()
                                        .configfile_create()


                name         : Name of your application for the config header.
                version      : Version of your application for the config
                               header.
                header       : Extra description/text for the config header.
                               This can be multiline text. It is converted to
                               comments if the lines don't start with '#'.
        """
        # application info (add your own here, or by accessing object)
        # like settings = easysettings.EasySettings()
        # settings.name = "My Project"
        # settings.version = "1.0"
        self.name = name or None
        self.version = version or None

        # This is an extra message for the top of the config file.
        # It can be a string or None. The string is added as a comment,
        # the '# ' will be added to each line if it's not present.
        self.header = header or None

        # default config file (better to set your own file)
        # like: settings.configfile = "myfile.config"
        #   or: settings = easysettings.EasySettings("myfile.config")
        if sconfigfile is None:
            sconfigfile = os.path.join(sys.path[0], "config.conf")
            self.configfile = sconfigfile
        else:
            # if filename is passed, automatically check/create file
            self.configfile = sconfigfile
            self.configfile_exists()

        # empty setting dictionary
        self.settings = {}
        # load setting from config file
        self.load_file()

    def __bool__(self):
        """ An EasySettings is truthy if it's settings are truthy. """
        return bool(self.settings)

    def _as_comparable(self, other=NoValue):
        """ Return self.settings if `other` is not given.
            If `other` is given, return other.settings or dict(other).
        """
        if other is NoValue:
            return self.settings

        if isinstance(other, EasySettings):
            return other.settings
        elif isinstance(other, dict):
            return other

        clsname = type(self).__name__
        raise TypeError(
            'Expecting {clsname} or {clsname}.settings, got: {typ}'.format(
                clsname=clsname,
                typ=type(other).__name__,
            )
        )

    def _build_header(self):
        """ Build the first line for the config file, a comment line
            that describes what the config file is for.
            This uses self.name and self.version when available.
            Returns a str, with no newline, ready to be written to the file.
        """
        lines = ['# Configuration']
        if self.name:
            lines.append('for {}'.format(self.name))
            if self.version:
                lines.append('v. {}'.format(self.version))
        return ' '.join(lines)

    def _get_compare_args(self, other, other2=NoValue):
        """ Determines which two instances are being compared by args.
            Returns either:
                self, other
            or:
                other, other2
            ...as comparable dicts.
        """
        if other2 is NoValue:
            return self._as_comparable(), self._as_comparable(other)
        return self._as_comparable(other), self._as_comparable(other2)

    def _parse_header(self):
        """ Parses self.header and converts it to comment lines.
            If no self.header is set, None is returned.
            self.header may be a str with newlines or a list/tuple of lines.
        """
        if self.header is None:
            return None
        if isinstance(self.header, (list, tuple)):
            headerlines = self.header
        else:
            headerlines = self.header.strip().split('\n')

        if not headerlines:
            return None

        parsed = []
        for line in headerlines:
            stripped = line.lstrip()
            if stripped.startswith('#'):
                parsed.append(stripped)
            else:
                parsed.append('# {}'.format(stripped))
        return '\n'.join(parsed)

    def clear(self):
        """ Clears all settings without warning, does not save to disk.
            ex: settings.clear()
        """

        self.settings = {}
        return True

    def clear_values(self, lst_options=None):
        """ Clear all values by default,
        if lst_options is passed, only options on the list are cleared.
        """
        if lst_options is None:
            for skey in self.settings:
                self.settings[skey] = ''
        else:
            for sopt in lst_options:
                if sopt in self.settings:
                    self.settings[sopt] = ''

        return True

    def compare_opts(self, settings1, settings2=NoValue):  # noqa
        """ compare the options/keys of two easysettings instances,
            or dicts (easysettings.settings)..
            returns False if values don't match.
        """
        adict, bdict = self._get_compare_args(settings1, settings2)

        return set(adict) == set(bdict)

    def compare_settings(self, settings1, settings2=NoValue):
        """ compare two EasySettings() instances,
            or dicts (easysettings.settings)
            ex:
            set1 = easysettings.EasySettings("file1.conf")
            set2 = easysettings.EasySettings("file2.conf")
            set3 = easysettings.EasySettings("file3.conf")
            # set values (notice set1 and set3 have the same)
            set1.set("user", "cjw")
            set2.set("user", "joseph")
            set3.set("user", "cjw"

            # this compares set2 to self (set1)
            bsettings_match = set1.compare(set2)

            # this compares any two, set3 is not compared here
            bsettings_match = set3.compare(set1, set2)
            # ,,,both return False because set1 and set2's 'user' differs

            # compare set3 to set1
            bmatching_settings = set3.compare(set1)
            # ...this returns True because set1 and set3's 'user' is the same

        """
        adict, bdict = self._get_compare_args(settings1, settings2)
        if len(adict) != len(bdict):
            return False
        return (
            self.compare_opts(settings1, settings2) and
            self.compare_vals(settings1, settings2)
        )


    def compare_vals(self, settings1, settings2=NoValue):  # noqa
        """ compare the values of two easysettings instances,
            or dicts (easysettings.settings)..
            returns False if values don't match.
        """
        adict, bdict = self._get_compare_args(settings1, settings2)
        if set(adict.values()) != set(bdict.values()):
            return False
        for key, aval in adict.items():
            bval = bdict.get(key, NoValue)
            if bval is NoValue:
                return False
            elif aval != bval:
                return False
        return True

    def configfile_create(self, sfilename=None):
        """ Creates a blank config file.
            If sfilename is given then current config file (self.configfile)
               is set to sfilename.
            If no sfilename is given then current config file is used.
            Returns False if no configfile is set, or on other failure.
            ** Overwrites file if it exists! ***
            ex: # this uses self.configfile as the filename
                # it can be set on initialization
                settings = easysettings.EasySettings("myfile.conf")
                settings.configfile_create()

                # this creates a different config file, and uses it
                # for setting/saving
                settings.configfile_create("myotherfile.conf")
        """
        if sfilename is None:
            sfilename = self.configfile
        else:
            self.configfile = sfilename

        if self.configfile is None:
            return False

        msg = self._build_header()
        header = self._parse_header()

        with open(self.configfile, 'w') as f:
            f.write('{}\n'.format(msg))
            if header:
                f.write('{}\n'.format(header))
        return True

    def configfile_exists(self, bcreateblank=True):
        """ checks to see if config file exists (creates a blank one
            if it doesn't)
            Returns True if the file exists, or a blank is created.
            ex: # make sure file exists before continuing
                if not settings.configfile_exists(False):
                    print "No settings file, cannot continue"
                # without the False argument, it should always return
                # True, except for when the config file can't be created
                # automatically. Usually because of no permissions.
                if not settings.configfile_exists():
                    print "No settings file, cannot be created!"
        """
        if os.path.isfile(self.configfile):
            return True
        else:
            if bcreateblank:
                return self.configfile_create()
            else:
                return False

    def copy(self):
        """ Return a separate copy of this EasySettings object. """
        new_es = EasySettings()
        new_es.configfile = self.configfile
        new_es.name = self.name
        new_es.version = self.version
        new_es.header = self.header
        new_es.settings = self.settings.copy()
        return new_es

    def es_version(self):
        """ returns module-level easysettings version string """
        return __version__

    def get(self, soption, default=''):
        """ retrieves a setting from config file
            Returns default ('') if no setting found.
            ex: settings.get('mysetting')
        """
        return self.settings.get(soption, default)

    def get_bool(self, option, default=False, strict=False):
        """ Parses a setting as a boolean, mostly for string values.
            This is not really needed, because if you set('opt', False),
            you will get('opt') == False.
            EasySettings already saves actual boolean values.

            This is for when you want a user friendly string setting, and
            solves the bool('False') != False problem.
            It also works with non string values, calling bool(val) instead.

            Arguments:
                option   : Setting option name to retrieve.
                default  : Default value to return when the setting hasn't
                           been set yet. Can be anything.
                strict   : Strict mode, True string values must be in the
                           the allowed values ('true', 'yes', 'on', '1').
                           Values are not case-sensitive.
                           When turned on, invalid values return the default.
                           When turned off, anything that is not a False
                           string value is accepted as True.
                           Default: False
            Example:
                settings.set('opt', 'false')
                assert settings.get_bool('opt') == False

                settings.set('opt', '0')
                assert settings.get_bool('opt') == False

                settings.set('opt', 'foo')
                assert settings.get_bool('opt') == True
                assert settings.get_bool('opt', strict=True) == None

            Map of True/False values for strings (case-insensitive):
                False:
                    'false', 'no', 'off', '0', ''
                when 'strict' is True:
                    True:
                        'true', 'yes', 'on', '1'
                when 'strict' is False (default):
                    True:
                        ..anything else. ('true', 'yes', 'on', '1' included.)

            If the value isn't a string (like: settings.set('opt', 123)),
            bool(value) is returned.

            Returns True, False, or possibly None when strict mode is used.
        """
        # .get() returns an empty str ('') for nonexistent values.
        optval = self.get(option, NoValue)
        if optval is NoValue:
            return default

        truevalues = ('true', 'yes', 'on', '1')
        falsevalues = ('false', 'no', 'off', '0')

        if hasattr(optval, 'lower'):
            optval = optval.lower()

            # String values. Empty string is False.
            if not optval:
                return False

            if strict:
                # Strict mode
                if optval in truevalues:
                    return True
                elif optval in falsevalues:
                    return False
                # Not an acceptable string value.
                return default

            # Non-strict mode.
            return optval not in falsevalues

        # Not a string value.
        return bool(optval)

    def has_option(self, option):
        """ Returns True if soption is in settings. """
        return (option in self.settings.keys())

    def has_value(self, value):
        """ Returns True if svalue is in settings. """
        # had to lengthen the code after adding non-string types

        try:
            hasit = (value in self.settings.values())
        except Exception:
            hasit = False
        return hasit

    def is_saved(self):
        """ Returns True if the current settings match what is saved
            in the config file.
        """
        disk_settings = self.read_file_noset()

        return self.compare_settings(disk_settings)

    def list_options(self, ssearch_query=None):
        """ Returns a list() of all current options.
            ex: # return a list of all options
                myoptions = settings.list_options()
                # returns: ["setting1", "setting2", ...]

                # return only options with 'test' in the name
                settings.set('regularoption', 'regularvalue')
                settings.set('testoption', 'testvalue')
                testoptions = settings.list_options('test')
                # returns ['testoption']
        """
        if ssearch_query is None:
            return list(self.settings)

        query = str_(ssearch_query)
        lst_tmp = []
        for itm in list(self.settings.keys()):
            if query in str_(itm):
                lst_tmp.append(itm)
        return lst_tmp

    def list_settings(self, ssearch_query=None):
        """ Returns a list of all settings.
            ex: # return all settings as a list
                mysettings = settings.list_settings()
                # returns: ["setting1=value1", "setting2=value2", ...]

                # return only settings with the string 'test'
                settings.set('testoption1', 'value1')
                settings.set('option2', 'testvalue2')
                settings.set('regularoption', 'regularvalue')
                testsettings = settings.list_settings('test')
                # returns [('testoption1', 'value1'), ...]
        """

        lst_tmp = []
        for skey in self.settings:
            if ssearch_query is None:
                lst_tmp.append((skey, self.settings[skey]))
            else:
                val = self.settings[skey]
                strform = '{}={}'.format(skey, val)
                if ((str_(ssearch_query) in strform) or
                        (ssearch_query == skey) or
                        (ssearch_query == val)):
                    lst_tmp.append((skey, self.settings[skey]))
        return lst_tmp

    def list_values(self, ssearch_query=None):
        """ Returns a list() of all current values.
            ex: # return a list of all values
                myvalues = settings.list_values()
                # returns: ["value1", "value2", ...]

                # return only values with 'test' in the value
                settings.set("option1", "testvalue1")
                settings.set("option2", "regularvalue2")
                testvalues = settings.list_values('test')
                # returns ['testvalue1']
        """
        if ssearch_query is None:
            return list(self.settings.values())

        lst_tmp = []
        query = str_(ssearch_query)
        for itm in list(self.settings.values()):
            # <a3
            if query in str_(itm):
                lst_tmp.append(itm)
        return lst_tmp

    def load_file(self, sfile=None):
        """ Reads config file into settings object """
        if sfile is None:
            if self.configfile is None:
                return False
        else:
            # Use this file from now on.
            self.configfile = sfile

        if not os.path.isfile(self.configfile):
            return False

        settings = self.read_file_noset()

        for k in settings:
            self.set(k, settings[k])
        return True

    def load_pickle(self, spicklefile=None):
        """ loads a pickle file into self,,,
            file must exist.
            if spicklefile is None, looks for:
               self.configfile.replace('.conf', '.pkl')

            also returns the loaded easysettings object,
            so you can do this:
            es = EasySettings().load_pickle("mypickledsettings.pkl")

            returns None on failure.

        """
        try:
            if spicklefile is None:
                spicklefile = self.configfile.replace('.conf', '.pkl')
            if PYTHON3:
                smode = 'rb'
            else:
                smode = 'r'
            with open(spicklefile, smode) as fpickle_read:
                es = pickle.load(fpickle_read)
                self.configfile = es.configfile
                self.name = es.name
                self.version = es.version
                self.header = es.header
                self.settings = es.settings

                return es
        except Exception:
            return None

    def read_file_noset(self, sfile=None):
        """ Reads config file, returns a settings dict.
            This does not actually set anything, use load_file() to load
            settings into an EasySettings object.
            Arguments:
                sfile : File name to read. Default: self.configfile
        """

        if sfile is None:
            if self.configfile is None:
                return {}
            sfile = self.configfile

        tmp_dict = {}

        if not os.path.isfile(sfile):
            return tmp_dict

        with open(sfile, 'r') as f:
            # cycle thru lines
            for sline in f:
                # Skip comment lines.
                if sline.lstrip().startswith('#'):
                    continue

                # actual setting?
                try:
                    eqindex = sline.index('=')
                except ValueError:
                    continue

                sopt = sline[:eqindex]
                sval = sline[eqindex + 1:].replace('(es_nl)', '\n')

                try:
                    # non-string typed value
                    val = safe_pickle_obj(sval)
                except Exception:
                    # normal string value
                    val = sval.rstrip()
                    try:
                        dateval = datetime.strptime(val, ISO8601)
                    except ValueError:
                        # Not a datetime.
                        pass
                    else:
                        val = dateval

                # Valid setting.
                tmp_dict[sopt] = val
            # success (filled dict)
            return tmp_dict

    def reload_file(self):
        """ same as load_file, except self.configfile must be set already """
        if self.configfile is None:
            return False
        else:
            return self.load_file(self.configfile)

    def save(self, sfile=None):
        """ save config file to disk
            if sfile is given then config is saved to sfile.
            otherwise, config is saved to self.configfile
        """
        if sfile is None:
            if self.configfile is None:
                return False
            else:
                sfile = self.configfile

        # Set header line (name and version.)
        msg = self._build_header()
        header = self._parse_header()

        try:
            with open(sfile, 'w') as fwrite:
                fwrite.write('{}\n'.format(msg))
                if header:
                    fwrite.write('{}\n'.format(header))
                for skey in list(self.settings.keys()):
                    val = self.settings[skey]
                    if isinstance(val, str):
                        sval = val.replace('\n', '(es_nl)')
                    elif isinstance(val, (date, datetime)):
                        sval = val.strftime(ISO8601)
                    else:
                        sval = safe_pickle_str(val).replace('\n', '(es_nl)')
                    fwrite.write(skey + '=' + sval + '\n')
                fwrite.flush()
                # success
                return True
            return False
        except Exception as ex:
            # failed to open file
            raise esSaveError(ex)
            return False

    def save_pickle(self, spicklefile=None):
        """ saves easysettings object into pickle file...
            spicklefile must exist.

            if spicklefile is None, saves to:
                self.configfile.replace('.conf', '.pkl')

            returns True on success, False on failure
        """
        try:
            if spicklefile is None:
                spicklefile = self.configfile.replace('.conf', '.pkl')
            if PYTHON3:
                smode = 'wb'
            else:
                smode = 'w'
            with open(spicklefile, smode) as fpickle_write:
                pickle.dump(self, fpickle_write)
                return True
            return False
        except Exception:
            return False

    def set(self, soption, value=None):
        """ sets a setting in config file.
            option cannot be an empty string ("").
            values can be any string or picklable type.
                (int, float, long, complex, etc.)
            a list of settings can be passed like:
                settings.set(['opt1=val1', 'opt2=val2'])

            ex: settings.set('user', 'cjw')
        """
        if '=' in soption:
            raise esSetError('No \'=\' characters allowed in options!')

        if value is None:
            value = ''

        try:
            # set list
            if isinstance(soption, list):
                return self.set_list(soption)

            # no empty options!
            if len(soption.replace(' ', '')) == 0:
                raise esSetError('Empty options are not allowed!')

            # dict must be able to hold it
            try:
                self.settings[soption] = value
            except Exception as exset:
                raise esValueError(exset)

            # echo back what was set
            return True
        except Exception as exsetmain:
            raise esSetError(exsetmain)

    def set_list(self, lst_settings):
        """ sets a list of settings...
            format of list should be:
                [('opt1', 'val1'), ('opt2',), ('opt3', 'val3'), ...]
            (same format that list_settings() outputs...)
        """

        for sset in lst_settings:
            if sset:
                setlen = len(sset)
                if setlen == 2:
                    opt, val = sset
                elif setlen == 1:
                    opt = sset[0]
                    val = None
                else:
                    errmsg = 'Expecting list of tuples! [ (opt, val), ... ]'
                    raise ValueError(errmsg)
                try:
                    self.set(opt, val)
                except Exception as exsetlist:
                    raise esSetError(exsetlist)
        return True

    def setsave(self, soption, svalue=None):
        """ sets a setting in config file, and saves the file
            ex: settings.setsave('user', 'cjw')
        """
        try:
            if self.set(soption, svalue):
                return self.save()
            else:
                errmsg = 'Unable to set option: {}={!r}'.format(
                    soption,
                    svalue
                )
                raise esSetError(errmsg)
        except Exception as exset:
            raise Exception(exset)

    def remove(self, option):
        """ Remove an option from the current settings
            ex: settings.set('user', 'name')
                settings.remove('user')
            or you can remove a list of options:
                settings.remove(['user', 'homedir', ...])

        """
        if isinstance(option, (list, tuple)):
            actualitem = self.settings.get(option, NoValue)
            if actualitem is NoValue:
                # List of options.
                errs = 0
                for itm in option:
                    try:
                        self.settings.pop(itm)
                    except KeyError:
                        errs += 1
                return not errs
        # Single item.
        try:
            self.settings.pop(option)
        except KeyError:
            return False
        return True

    def __getitem__(self, key):
        """ Shortcut to EasySettings.get() using dict/list behavior.
            This will raise a KeyError if the setting cannot be found.
        """
        notset = object()
        val = self.get(key, notset)
        if val is notset:
            raise KeyError('Option not found: {!r}'.format(key))
        return val

    def __repr__(self):
        return 'EasySettings({!r}, {!r})'.format(
            self.configfile or '<No File>',
            self.settings)

    def __str__(self):
        return str_(self.settings)

    def __eq__(self, other):
        """ tests equality between easysettings instances,
            or dicts (easysettings.settings)
        """
        return self.compare_settings(self.settings, other)

    def __ne__(self, other):
        """ test inequality between easysettings instances,
            or dicts (easysettings.settings)
        """
        return (not self.compare_settings(self.settings, other))

    def __gt__(self, other):
        """ tests size of settings lists """

        try:
            b_esinstance = isinstance(other, EasySettings)
        except Exception:
            b_esinstance = False

        if b_esinstance:
            set2 = other.settings
        elif isinstance(other, dict):
            set2 = other
        else:
            raise esCompareError(
                '__lt__ only compares EasySettings instances or dicts.'
            )
            return False
        return (len(self.settings) > len(set2))

    def __lt__(self, other):
        """ tests size of settings lists """

        try:
            b_esinstance = isinstance(other, EasySettings)
        except Exception:
            b_esinstance = False
        if b_esinstance:
            set2 = other.settings
        elif isinstance(other, dict):
            set2 = other
        else:
            raise esCompareError(
                '__lt__ only compares easysettings instances or dicts.'
            )
            return False

        return (len(self.settings) < len(set2))

    def __ge__(self, other):
        """ tests size of settings lists """

        try:
            b_esinstance = isinstance(other, EasySettings)
        except Exception:
            b_esinstance = False
        if b_esinstance:
            set2 = other.settings
        elif isinstance(other, dict):
            set2 = other
        else:
            raise esCompareError(
                '__lt__ only compares easysettings instances or dicts.'
            )
            return False

        return ((len(self.settings) > len(set2)) or
                self.compare_settings(set2))

    def __le__(self, other):
        """ tests size of settings lists """

        try:
            b_esinstance = isinstance(other, EasySettings)
        except Exception:
            b_esinstance = False
        if b_esinstance:
            set2 = other.settings
        elif isinstance(other, dict):
            set2 = other
        else:
            raise esCompareError(
                '__lt__ only compares easysettings instances or dicts.'
            )
            return False
        return ((len(self.settings) < len(set2)) or
                self.compare_settings(set2))


class esError(Exception):

    """ EasySettings base exception """

    def __init__(self, message):
        Exception.__init__(self, message)


class esSetError(esError):

    """ Set option error """
    pass


class esGetError(esError):

    """ Get option error """
    pass


class esCompareError(esError):

    """ Compare settings error """
    pass


class esSaveError(esError):

    """ Save settings error """
    pass


class esValueError(esError):

    """ Illegal value error """
    pass


def pickled_str(pickle_dumps_returned):
    """ Returns Python 2 and 3 safe string for converting pickle.dumps().
        Will always return String, not Bytes like Python3 wants to.
        ex:
            mystring = pickled_str(pickle.dumps(MyObject, 0)
    """

    if PYTHON3:
        byte_array = bytearray(pickle_dumps_returned)
        return "".join(chr(int(c)) for c in byte_array)
    else:
        return pickle_dumps_returned


def safe_pickle_obj(string_):
    """ Returns Python 2 and 3 safe pickle.loads().
        Will return object from pickle-string,
        Does not need Bytes like Python3 likes.
        Returns unpickled object from pickled-string.
        ex:
            my_object = safe_pickle_obj(safe_pickle_str('12345678'))
            my_obj2 = safe_pickle_obj(safe_pickle_str(['my','list', 'obj']))
    """
    if PYTHON3:
        return pickle.loads(bytearray(string_, 'utf-8'))
    else:
        return pickle.loads(string_)


def safe_pickle_str(object_):
    """ Pickles object in the same format whether using Python 2 or 3.
        pickle 2.7 likes strings, pickle 3 likes bytes....
        we will be using strings no matter what the version.
        Returns pickled-string from object.
    """
    return pickled_str(pickle.dumps(object_, 0))


def str_(data):
    """ Python 2 and 3 safe str(),
        for when Python 3 uses Bytes where Python 2 used Strings.
        Should be used anywhere you would use the str() function.
    """
    if PYTHON3:
        # Safer conversion from bytes to string for python 3.
        if isinstance(data, (bytes, bytearray)):
            return str(data, 'utf-8')
    return str(data)


def version():
    """ returns version string. """
    return __version__


def _print_help():
    print('\n'.join((
        'EasySettings v. {}',
        'For help with EasySettings open a Python interpreter and type:',
        '    help(\'easysettings\') or help(\'easysettings.EasySettings\')',
    )).format(__version__))


if __name__ == '__main__':
    _print_help()
    sys.exit(1)
