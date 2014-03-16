#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  EasySettings
  ...easily saves/retrieves settings
     features:
         load/save config file
         set/remove options
         set & save at the same time,
         detect if config file has been saved,
         compare two easysettings(),
         compare value list of two easysettings(),
         compare option list of two easysettings(),
         list settings/options/values,
         list by search query,
         detect if config file exists,
         detect if settings exist,
         pickle/unpickle easysettings.
         
  
Created on Jan 16, 2013

@author: Christopher Welborn
'''
# easy settings version
__version__ = '1.8.1'

# file related imports
import sys, os.path
# pickling the whole settings object
import pickle

__all__ = ['easysettings', 'version', 'esError', 'esGetError', 'esSetError', 'esCompareError', 
           'esSaveError', 'esValueError', 'test_run']

# Python 3 compatibility flag
# ...we need this because pickle likes to use bytes in python 3, and strings
#    in python 2. We will be using strings because they fit the config file
#    format we have been using. No binary config files allowed here.
#    see: safe_pickled_str(), safe_pickled_obj(), and their helper pickled_str()
if sys.version > '3':
    PYTHON3 = True
    # python 3 needs no long() function.
    long = int
else:
    PYTHON3 = False
    
      
class easysettings():
    ''' helper for saving/retrieving settings..
    
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
          name       = name for current project
          version    = version for current project
         
        Example use:
            import easysettings
            settings = easysettings.easysettings("myconfigfile.conf")
            settings.name = "My Project"
            settings.version = "1.0"
            # name & version are optional, they are only used in creating 
            # a config file with '# configuration for My Project 1.0' as
            # the first line. if they are None, that line says '# configuration'.
            
            settings.set("username", "cjwelborn")
            
            # settings can be retrieved without saving to disk first...
            s_user = settings.get("username")
            
            # settings can be saved to disk while setting an option
            settings.setsave("installdir", "/usr/share/easysettings") 
    '''

    
    def __init__(self, sconfigfile = None):
        ''' creates new settings object to work with '''
        # application info (add your own here, or by accessing object)
        # like settings = easysettings.easysettings()
        # settings.name = "My Project"
        # settings.version = "1.0"
        self.name = None
        self.version = None
        # default config file (better to set your own file)
        # like: settings.configfile = "myfile.config"
        #   or: settings = easysettings.easysettings("myfile.config")
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
                      
    def load_file(self, sfile = None):
        """ reads config file into settings object """
        if sfile is None:
            if self.configfile is None:
                return False
            else:
                sfile = self.configfile
        else:
            self.configfile = sfile
    
        if os.path.isfile(sfile):
            with open(sfile, 'r') as fread:
                slines = fread.readlines()
                # cycle thru lines
                for sline in slines:
                    # actual setting?
                    if "=" in sline:
                        sopt = sline[:sline.index("=")]
                        sval = sline[sline.index("=") + 1:].replace('(es_nl)', '\n')
                        
                        try:
                            # non-string typed value
                            val = safe_pickle_obj(sval)
                        except:
                            # normal string value
                            if sval.endswith('\n'):
                                sval = sval[:-1]
                            val = sval
                        self.set(sopt, val)
                # success
                return True
        # failure
        return False
    
    def read_file_noset(self, sfile = None):
        """ reads config file, returns a seperate settings dict.
            not for general use, use load_file() to load your settings
            from file into the settings object.
            ** this does not actually set anything, it is used for      **
            ** comparing the current local settings with those on disk. **
        """
        tmp_dict = {}
        if sfile is None:
            if self.configfile is None:
                return {}
            else:
                sfile = self.configfile
        else:
            self.configfile = sfile
    
        if os.path.isfile(sfile):
            with open(sfile, 'r') as fread:
                slines = fread.readlines()
                # cycle thru lines
                for sline in slines:
                    # actual setting?
                    if "=" in sline:
                        sopt = sline[:sline.index("=")]
                        sval = sline[sline.index("=") + 1:].replace('(es_nl)', '\n')
                        
                        try:
                            # non-string typed value
                            val = safe_pickle_obj(sval)
                        except:
                            # normal string value
                            if sval.endswith('\n'):
                                sval = sval[:-1]
                            val = sval
                            
                        tmp_dict[sopt] = val
                # success (filled dict)
                return tmp_dict
        # failure (empty dict)
        return {}
    
    def reload_file(self):
        """ same as load_file, except self.configfile must be set already """
        if self.configfile is None:
            return False
        else:
            return self.load_file(self.configfile)
  
    def save(self, sfile = None):
        """ save config file to disk
            if sfile is given then config is saved to sfile.
            otherwise, config is saved to self.configfile
        """
        if sfile is None:
            if self.configfile is None:
                return False
            else:
                sfile = self.configfile
        
        try:
            if self.name is None:
                smsg = ""
            else:
                smsg = " for " + self.name
            with open(sfile, 'w') as fwrite:
                fwrite.write("# configuration" + smsg + "\n")
                for skey in list(self.settings.keys()):
                    val = self.settings[skey]
                    if isinstance(val, str):
                        sval = val.replace('\n', '(es_nl)')
                    else:
                        #try:
                        sval = safe_pickle_str(val).replace('\n', '(es_nl)')
                        #except:
                        #    raise esSaveError('Illegal value!: ' + repr(val))
                        
                    fwrite.write(skey + '=' + sval + '\n')
                fwrite.flush()
                # success  
                return True
            return False
        except Exception as ex:
            # failed to open file
            raise esSaveError(ex)
            return False
    
    def load_pickle(self, spicklefile = None):
        """ loads a pickle file into self,,,
            file must exist.
            if spicklefile is None, looks for:
               self.configfile.replace('.conf', '.pkl')
            
            also returns the loaded easysettings object,
            so you can do this:
            es = easysettings().load_pickle("mypickledsettings.pkl")
            
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
                self.settings = es.settings
                
                return es
        except:
            return None
        
    def save_pickle(self, spicklefile = None):
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
        except:
            return False
        
    def set(self, soption, value = None):
        """ sets a setting in config file.
            option cannot be an empty string ("").
            values can be any string or picklable type.
                (int, float, long, complex, etc.)
            a list of settings can be passed like:
                settings.set(['opt1=val1', 'opt2=val2'])
            
            ex: settings.set('user', 'cjw')
        """
        if "=" in soption:
            raise esSetError("no '=' characters allowed in options!")
            return False
        if value is None:
            value = ""
        try:
            # set list
            if isinstance(soption, list):
                return self.set_list(soption)
            # no empty options!
            if len(soption.replace(' ', '')) == 0:
                raise esSetError("empty options are not allowed!")
                return False
            # dict must be able to hold it
            try:
                self.settings[soption] = value
            except:
                raise esValueError('Illegal value!: ' + repr(value))
                return False
            # echo back what was set
            return self.get(soption)
        except:
            return ""
        
    def set_list(self, lst_settings):
        """ sets a list of settings...
                (string values only)
            format of list should be:
                ['option1=value1', 'option2=', 'option3=val3', ...]
            (same format that list_settings() outputs...)
        """
        for sset in lst_settings:
            # actual setting?
            if "=" in sset:
                sopt = sset[:sset.index("=")]
                sval = sset[sset.index("=") + 1:]
                self.set(sopt, sval)
        return str_(lst_settings)
                  
    def setsave(self, soption, svalue = None):
        """ sets a setting in config file, and saves the file 
            ex: settings.setsave('user', 'cjw')
        """
        if self.set(soption, svalue):
            return self.save()
        else:
            raise esSetError("unable to set option: " + \
                             soption + "=" + svalue)
            return False
      
    def get(self, soption, default = None):
        """ retrieves a setting from config file 
            Returns default (None) if no setting found.
            ex: settings.get('mysetting')
        """
        if soption in self.settings.keys():
            return self.settings[soption]
        else:
            if default is None: default = ""
            return default
        

    def remove(self, option):
        """ Remove an option from the current settings
            ex: settings.set('user', 'name')
                settings.remove('user')
            or you can remove a list of options:
                settings.remove(['user', 'homedir', ...])
        
        """
        if isinstance(option, list):
            for itm in option:
                if itm in self.settings.keys():
                    self.settings.pop(itm)
            return True
        else:
            if option in self.settings.keys():
                self.settings.pop(option)
                return True
        return False
    
    def clear(self):
        """ Clears all settings without warning, does not save to disk.
            ex: settings.clear()
        """
        
        self.settings = {}
        return True
    
    def clear_values(self, lst_options = None):
        """ Clear all values by default,
        if lst_options is passed, only options on the list are cleared.
        """
        if lst_options is None:
            for skey in (list(self.settings.keys())):
                self.settings[skey] = ""
        else:
            for sopt in lst_options:
                if sopt in list(self.settings.keys()):
                    self.settings[sopt] = ""
        
        return True
        
            
    def configfile_create(self, sfilename = None):
        """ creates a blank config file.
            if sfilename is given then current config file (self.configfile)
               is set to sfilename.
            if no sfilename is given then current config file is used.
            Returns False if no configfile is set, or on other failure.
            ** Overwrites file if it exists! ***
            ex: # this uses self.configfile as the filename
                # it can be set on initialization
                settings = easysettings.easysettings("myfile.conf")
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
        else:
            if self.name is None:
                smsg = ""
            else:
                smsg = " for " + self.name
            fconfig = open(self.configfile, 'w')
            fconfig.write("# configuration" + smsg + "\n")
            fconfig.close()

            return True
    
    
    def configfile_exists(self, bcreateblank = True):
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
    
    def list_settings(self, ssearch_query = None):
        """ Returns a list of all settings.
            ex: # return all settings as a list
                mysettings = settings.list_settings()
                # returns: ["setting1=value1", "setting2=value2", ...]
                
                # return only settings with the string 'test'
                settings.set('testoption1', 'value1')
                settings.set('option2', 'testvalue2')
                settings.set('regularoption', 'regularvalue')
                testsettings = settings.list_settings('test')
                # returns ['testoption1=value1', 'option2=testvalue2']
        """
        lst_tmp = []
        for skey in (list(self.settings.keys())):
            if ssearch_query is None:
                lst_tmp.append(skey + "=" + str_(self.settings[skey]))
            else:
                sval = self.settings[skey]
                #try:
                #    sval = str_(pickle.loads(sval))
                #except:
                #    sval = self.settings[skey]
                s = skey + "=" + str_(sval)
                if str_(ssearch_query) in s:
                    lst_tmp.append(s)
        return lst_tmp
    
    def list_options(self, ssearch_query = None):
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
            return list(self.settings.keys())
        else:
            lst_tmp = []
            for itm in (list(self.settings.keys())):
                if ssearch_query in itm:
                    lst_tmp.append(str_(itm))
            return lst_tmp

    
    def list_values(self, ssearch_query = None):
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
        else:
            lst_tmp = []
            for itm in list(self.settings.values()):
                # <a3
                #try:
                #    pval = pickle.loads(itm)
                #    sval = str_(pval)
                #    itm = pval
                #except:
                #    sval = itm
                
                if str_(ssearch_query) in str_(itm):
                    lst_tmp.append(itm)
            return lst_tmp

    
    def has_option(self, soption):
        """ Returns True if soption is in settings. """
        return (soption in self.settings.keys())    

    def has_value(self, value):
        """ Returns True if svalue is in settings. """
        # had to lengthen the code after adding non-string types

        try:
            hasit = (value in self.settings.values())
        except:
            hasit = False
        return hasit
       

    def is_saved(self):
        """ Returns True if the current settings match what is saved
            in the config file.
        """
        disk_settings = self.read_file_noset()
        
        return self.compare_settings(disk_settings)
    
    def compare_settings(self, settings1, settings2 = None):
        """ compare two easysettings() instances,
            or dicts (easysettings.settings)
            ex: 
            set1 = easysettings.easysettings("file1.conf")
            set2 = easysettings.easysettings("file2.conf")
            set3 = easysettings.easysettings("file3.conf")
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
        # compare to self
        if settings2 is None:
            settings2 = self.settings
        return all([self.compare_opts(settings1, settings2),
                   self.compare_vals(settings1, settings2)])
        
    def compare_opts(self, settings1, settings2 = None):
        """ compare the options/keys of two easysettings instances, 
            or dicts (easysettings.settings)..
            returns False if values don't match.
        """
        try:
            b_esinstance = isinstance(settings1, easysettings.easysettings)
        except:
            try:
                b_esinstance = isinstance(settings1, easysettings)
            except:
                b_esinstance = False
                
        if b_esinstance:
            set1 = settings1.settings
        elif isinstance(settings1, dict):
            set1 = settings1
        else:
            raise esCompareError("only easysettings instances " + \
                            " or easysettings.settings are allowed!")
            return False
        # compare to self
        if settings2 is None:
            settings2 = self.settings
            
        try:
            b_esinstance = isinstance(settings2, easysettings.easysettings)
        except:
            try:
                b_esinstance = isinstance(settings2, easysettings)
            except:
                b_esinstance = False
                
        if b_esinstance:
            set2 = settings2.settings
        elif isinstance(settings2, dict):
            set2 = settings2
        else:
            raise esCompareError("only easysettings instances " + \
                                 "or easysettings.settings are allowed!")
            return False
        # do the compare
        for itm in list(set1.keys()):
            if not itm in list(set2.keys()):
                return False
        for itm2 in list(set2.keys()):
            if not itm2 in list(set1.keys()):
                return False
        return True   
         
    def compare_vals(self, settings1, settings2 = None):
        """ compare the values of two easysettings instances, 
            or dicts (easysettings.settings)..
            returns False if values don't match.
        """
        try:
            b_esinstance = isinstance(settings1, easysettings.easysettings)
        except:
            try:
                b_esinstance = isinstance(settings1, easysettings)
            except:
                b_esinstance = False
                
        if b_esinstance:
            set1 = settings1.settings
        elif isinstance(settings1, dict):
            set1 = settings1
        else:
            raise esCompareError("only easysettings " + \
                                 "instances or easysettings.settings are allowed!")
            return False
        # compare to self
        if settings2 is None:
            settings2 = self.settings
            
        try:
            b_esinstance = isinstance(settings2, easysettings.easysettings)
        except:
            try:
                b_esinstance = isinstance(settings2, easysettings)
            except:
                b_esinstance = False
                
        if b_esinstance:
            set2 = settings2.settings
        elif isinstance(settings2, dict):
            set2 = settings2
        else:
            raise esCompareError("only easysettings " + \
                            "instances or easysettings.settings are allowed")
            return False
        # do the compare        
        for itm in list(set1.values()):
            if not itm in list(set2.values()):
                return False
        for itm2 in list(set2.values()):
            if not itm2 in list(set1.values()):
                return False
        return True
    
    
    def es_version(self):
        """ returns module-level easysettings version string """
        return __version__
    
     
    def __repr__(self):
        if self.configfile is None:
            sfile = "{No File},"
        else:
            sfile = "{" + self.configfile + "},"
        s = "easysettings(" + sfile + repr(self.settings) + ")"
        return s
        
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
            b_esinstance = isinstance(other, easysettings.easysettings)
        except:
            try:
                b_esinstance = isinstance(other, easysettings)
            except:
                b_esinstance = False
        if b_esinstance:
                set2 = other.settings
        elif isinstance(other, dict):
            set2 = other
        else:
            raise esCompareError("__lt__ only compares easysettings " + \
                            "instances or dicts.")
            return False
        return (len(self.settings) > len(set2))
    def __lt__(self, other):
        """ tests size of settings lists """
        try:
            b_esinstance = isinstance(other, easysettings.easysettings)
        except:
            try:
                b_esinstance = isinstance(other, easysettings)
            except:
                b_esinstance = False
        if b_esinstance:
                set2 = other.settings
        elif isinstance(other, dict):
            set2 = other
        else:
            raise esCompareError("__lt__ only compares easysettings " + \
                            "instances or dicts.")
            return False
        
        return (len(self.settings) < len(set2))
    def __ge__(self, other):
        """ tests size of settings lists """
        try:
            b_esinstance = isinstance(other, easysettings.easysettings)
        except:
            try:
                b_esinstance = isinstance(other, easysettings)
            except:
                b_esinstance = False
        if b_esinstance:
                set2 = other.settings
        elif isinstance(other, dict):
            set2 = other
        else:
            raise esCompareError("__lt__ only compares easysettings " + \
                            "instances or dicts.")
            return False

        return ((len(self.settings) > len(set2)) or 
                self.compare_settings(set2))
        
        return (len(self.settings) >= len(set2))
    def __le__(self, other):
        """ tests size of settings lists """
        try:
            b_esinstance = isinstance(other, easysettings.easysettings)
        except:
            try:
                b_esinstance = isinstance(other, easysettings)
            except:
                b_esinstance = False
        if b_esinstance:
                set2 = other.settings
        elif isinstance(other, dict):
            set2 = other
        else:
            raise esCompareError("__lt__ only compares easysettings " + \
                                 "instances or dicts.")
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

def str_(data):
    """ Python 2 and 3 safe str(), 
        for when Python 3 uses Bytes where Python 2 used Strings.
        Should be used anywhere you would use the str() function.
    """
    if PYTHON3:
        # Safer conversion from bytes to string for python 3.
        if (isinstance(data, bytes) or 
            isinstance(data, bytearray)):
            return str(data, 'utf-8')
    return str(data)

def safe_pickle_str(object_):
    """ Pickles object in the same format whether using Python 2 or 3.
        pickle 2.7 likes strings, pickle 3 likes bytes....
        we will be using strings no matter what the version.
        Returns pickled-string from object.
    """
    return pickled_str(pickle.dumps(object_, 0))

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
    
def pickled_str(pickle_dumps_returned):
    """ Returns Python 2 and 3 safe string for converting pickle.dumps().
        Will always return String, not Bytes like Python3 wants to.
        ex:
            mystring = pickled_str(pickle.dumps(MyObject, 0)
    """
        
    if PYTHON3:
        byte_array= bytearray(pickle_dumps_returned)
        return "".join(chr(int(c)) for c in byte_array)
    else:
        return pickle_dumps_returned
    


def version():
    """ returns version string. """
    return __version__

           
def test_run(stestconfigfile = None):
    """ Runs a test on pretty much every EasySettings function to make
        sure everything works as intended under normal use. Prints to console.
    """
    # run a test on all easysettings functions
    if stestconfigfile is None:
        stestconfigfile = os.path.join(sys.path[0], "easysettings_test.conf")
    
    print ("checking/creating config file: " + stestconfigfile)
    es = easysettings(stestconfigfile)
 
    print ("\nReading:")
    print ("               load_file(): " + str_(es.load_file()))
    print ("         read_file_noset(): " + str_(es.read_file_noset()))
    print ("             reload_file(): " + str_(es.reload_file()))

    print ("\nSaving:")
    print ("                    save(): " + str_(es.save()))

    print ("\nSetting:")
    print ("             set('o', 'v'): " + str_(es.set('o', 'v')))
    print ("        set('obool', True): " + str_(es.set('obool', True)))
    print ("              set('o', 12): " + str_(es.set('o', 12)))
    print ("           set('o', 12.24): " + str_(es.set('o', 12.24)))
    print ("         set('o', 123456L): " + str_(es.set('o', long(123456))))
    print ("   set(['o1=v1', 'o2=v2']): " + str_(es.set(['o1=v1', 'o2=v2'])))
    print ("       setsave('o1', 'o2'): " + str_(es.setsave('o1', 'o2')))
    print ("\nGetting:")
    print ("                 get('o1'): " + str_(es.get('o1')))
    print ("                  get('o'): " + str_(es.get('o')))
    print ("           if get('obool'):")
    if es.get('obool'):
        print ("                             Passed. =" + str_(es.get('obool')))
    else:
        print ("                             Failed. =" + str_(es.get('obool')))
    print ("           list_settings(): " + str_(es.list_settings()))
    print ("            list_options(): " + str_(es.list_options()))
    print ("             list_values(): " + str_(es.list_values()))
    print ("\nGetting Search Query:")
    print ("        list_settings('v'): " + str_(es.list_settings('v')))
    print ("         list_options('1'): " + str_(es.list_options('1')))
    print ("          list_values('2'): " + str_(es.list_values('2')))
    print ("\nGetting Non-String Query:")
    print ("    list_settings(123456L): " + str_(es.list_settings(long(123456))))
    print ("      list_values(123456L): " + str_(es.list_values(long(123456))))
    
    print ("\nSaved:")
    print ("                is_saved(): " + str_(es.is_saved()))
    
    print ("\nRemoving/Clearing:")
    print ("               remove('o'): " + str_(es.remove('o')))
    print ("            remove(['o2']): " + str_(es.remove(['o2'])))
    print ("        clear_values('o1'): " + str_(es.clear_values('o1')))
    print ("      clear_values(['o1']): " + str_(es.clear_values(['o1'])))
    print ("                   clear(): " + str_(es.clear()))
    
    print ("\nComparison:")
    es2 = easysettings(stestconfigfile.replace('.conf', '2.conf'))
    print ("            compare_vals(): " + str_(es.compare_vals(es2)))
    print ("            compare_opts(): " + str_(es.compare_opts(es2)))
    print ("                       == : " + str_(es == es2))
    print ("                       != : " + str_(es != es2))
    print ("                       <= : " + str_(es <= es2))
    print ("                       >= : " + str_(es >= es2))
    print ("                        < : " + str_(es < es2))
    print ("                        > : " + str_(es > es2))
    
    
    print ("\nPickle:")
    spicklefile = stestconfigfile.replace('.conf', '.pkl')
    print ("             save_pickle(): " + str_(es.save_pickle(spicklefile)))
    print ("             load_pickle(): ")
    es = easysettings().load_pickle(spicklefile)
    print ("                            " + str_(es))
    
    print ("\nErrors: ")
    lst_errs = [esError("Base Error"), esSetError("Set Error"), 
                esGetError("Get Error"), esCompareError("Compare Error"),
                esSaveError("Save Error"), esValueError("Value Error")]
    for errs in lst_errs:
        try:
            raise errs
        except Exception as ex:
            print ("    " + str_(ex))

            
    print ("\nRemoving test run configs...")
    if os.path.isfile(stestconfigfile):
        try:
            os.remove(stestconfigfile)
            print ("    Removed " + stestconfigfile)
        except:
            print ("    Unable to remove " + stestconfigfile)
            
    stestconfigfile = stestconfigfile.replace('.conf', '2.conf')
    if os.path.isfile(stestconfigfile):
        try:
            os.remove(stestconfigfile)
            print ("    Removed " + stestconfigfile)
        except:
            print ("    Unable to remove " + stestconfigfile)
    if os.path.isfile(spicklefile):
        try:
            os.remove(spicklefile)
            print ("    Removed " + spicklefile)
        except:
            print ("    Unable to remove " + spicklefile)
            
            
    print ("\n\nFinished with test_run().\n")
    
   
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("EasySettings v. " + __version__ + '\n')
        print ("For help with EasySettings open a terminal and type:")
        print ("    python")
        print ("    help('EasySettings') or help('EasySettings.easysettings')")
        print ('To test EasySettings functionality type:')
        print ('python easysettings.py -test')
        exit(0)
    else:
        if "-test" in sys.argv:
            # run test
            
            try:
                test_run()
                print ("All Passed.")
                exit(0)
            except Exception as ex:
                print ("Failed: " + str_(ex))
                exit(1)
            
            
    
    
    
    
            