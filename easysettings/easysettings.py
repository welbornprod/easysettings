#!/usr/bin/env python
'''
  EasySettings 1.5.0
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
  
Created on Jan 16, 2013

@author: Christopher Welborn
'''
# file related imports
import sys, os.path

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
            
            settings.set("username", "cjwelborn")
            
            # settings can be retrieved without saving to disk first...
            s_user = settings.get("username")
            
            # settings can be saved to disk while setting an option
            settings.setsave("installdir", "/usr/share/easysettings")
            
          
        
    '''
    # easysettings version
    _es_version = "1.5.0"
    
    def __init__(self, sconfigfile = None):
        ''' creates new settings object to work with '''
        # application info (add your own here, or by accessing object)
        # like settings = easysettings.easysettings()
        # settings.name = "My Project"
        # settings.version = "1.0"
        self.name = '' # add your
        self.version = ''
        # default config file (better to set your own file)
        # like: settings.configfile = "myfile.config"
        #   or: settings = easysettings.easysettings("myfile.config")
        if sconfigfile is None:
            sconfigfile = os.path.join(sys.path[0], "config.conf")
        self.configfile = sconfigfile
        # empty setting dictionary
        self.settings = {}
        # load setting from config file
        self.read_file()
    
    def __repr__(self):
        if self.configfile is None:
            sfile = "{No File},"
        else:
            sfile = "{" + self.configfile + "},"
        s = "easysettings(" + sfile + repr(self.settings) + ")"
        return s
    
    def __str__(self):
        return str(self.settings)
    
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
            raise Exception("easysettings.__lt__ only compares easysettings " + \
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
            raise Exception("easysettings.__lt__ only compares easysettings " + \
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
            raise Exception("easysettings.__lt__ only compares easysettings " + \
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
            raise Exception("easysettings.__lt__ only compares easysettings " + \
                            "instances or dicts.")
            return False
        return ((len(self.settings) < len(set2)) or 
                self.compare_settings(set2)) 
           
    def read_file(self, sfile = None):
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
                        sval = sline[sline.index("=") + 1:].replace('\n', '')
            
                        self.set(sopt, sval)
                # success
                return True
        # failure
        return False
    
    def read_file_noset(self, sfile = None):
        """ reads config file, returns a seperate settings dict.
            not for general use, use read_file() to load your settings
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
                        sval = sline[sline.index("=") + 1:].replace('\n', '')
            
                        tmp_dict[sopt] = sval
                # success (filled dict)
                return tmp_dict
        # failure (empty dict)
        return {}
    
    def reload_file(self, sfile = None):
        """ same as read_file """
        return self.read_file(sfile)
    
    def set(self, soption, svalue):
        """ sets a setting in config file.
            soption cannot be an empty string ("").
            svalue can be an empty string.
            ex: settings.set('user', 'cjw')
        """
        if "=" in soption:
            raise Exception("easysettings: no '=' characters allowed in options!")
            return False
        if len(soption.replace(' ', '')) == 0:
            raise Exception("easysettings: empty options are not allowed!")
            return False
    
        try:
            self.settings[soption] = svalue
            return True
        except:
            return False
  
    def setsave(self, soption, svalue):
        """ sets a setting in config file, and saves the file 
            ex: settings.setsave('user', 'cjw')
        """
        if self.set(soption, svalue):
            self.save()
        else:
            raise Exception("easysettings: unable to set option: " + \
                  soption + "=" + svalue)
            return False
      
    def get(self, soption, sdefault = ""):
        """ retrieves a setting from config file 
            Returns sdefault ("") if no setting found.
            ex: settings.get('mysetting')
        """
        if self.settings.has_key(soption):
            return self.settings[soption]
        else:
            #raise Exception("alias_settings: key not found: " + soption)
            return sdefault
        
  
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
                for skey in self.settings.iterkeys():
                    fwrite.write(skey + '=' + self.settings[skey] + '\n')
                fwrite.flush()
                # success  
                return True
        except Exception as ex:
            # failed to open file
            raise Exception("easysettings: failed to open file for write!: " + \
                            sfile + '\n\nError:\n' + str(ex))
            return False

    def remove(self, soption):
        """ Remove an option from the current settings
            ex: settings.set('user', 'name')
                settings.remove('user')
        
        """
        if self.settings.has_key(soption):
            self.settings.pop(soption)
            return True
        return False
    
    def clear(self):
        """ Clears all settings without warning, does not save to disk.
            ex: settings.clear()
        """
        
        self.settings = {}
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
        for skey in self.settings.iterkeys():
            if ssearch_query is None:
                lst_tmp.append(skey + "=" + self.settings[skey])
            else:
                s = skey + "=" + self.settings[skey]
                if ssearch_query in s:
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
            return list(self.settings.iterkeys())
        else:
            lst_tmp = []
            for itm in self.settings.iterkeys():
                if ssearch_query in itm:
                    lst_tmp.append(str(itm))
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
            return list(self.settings.itervalues())
        else:
            lst_tmp = []
            for itm in self.settings.itervalues():
                if ssearch_query in itm:
                    lst_tmp.append(str(itm))
            return lst_tmp

    
    def has_option(self, soption):
        """ Returns True if soption is in settings. """
        return self.settings.has_key(soption)    

    def has_value(self, svalue):
        """ Returns True if svalue is in settings. """
        return (svalue in self.settings.itervalues())

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
            raise Exception("compare_opts() only compares easysettings instances " + \
                            " or easysettings.settings")
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
            raise Exception("compare_opts() only compares easysettings instances " + \
                            "or easysettings.settings")
            return False
        # do the compare
        for itm in set1.iterkeys():
            if not itm in set2.iterkeys():
                return False
        for itm2 in set2.iterkeys():
            if not itm2 in set1.iterkeys():
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
            raise Exception("compare_vals() only compares easysettings " + \
                            "instances or easysettings.settings")
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
            raise Exception("compare_vals() only compares easysettings " + \
                            "instances or easysettings.settings")
            return False
        # do the compare        
        for itm in set1.itervalues():
            if not itm in set2.itervalues():
                return False
        for itm2 in set2.itervalues():
            if not itm2 in set1.itervalues():
                return False
        return True        

if __name__ == "__main__":
    es = easysettings()
    print "EasySettings v. " + es._es_version + '\n'
    print "For help with EasySettings open a terminal and type:"
    print "    python"
    print "    help('EasySettings')"
    del es
    exit(0)
    
    
    
    
            