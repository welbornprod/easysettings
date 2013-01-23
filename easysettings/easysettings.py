#!/usr/bin/env python
'''
  EasySettings
  ...easily saves/retrieves settings
  
  
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
            settings = easysettings.easysettings()
            settings.name = "My Project"
            settings.version = "1.0"
            settings.configfile = "myconfigfile.conf"
            
            settings.setsave("username", "cjwelborn")
            s_user = settings.get("username")
          
        
    '''
    # easysettings version
    _es_version = "1.0"
    
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
    
    def reload_file(self, sfile = None):
        """ same as read_file """
        return self.read_file(sfile)
    
    def set(self, soption, svalue):
        """ sets a setting in config file.
            soption cannot be an empty string ("").
            svalue can be an empty string.
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
        """ sets a setting in config file, and saves the file """
        if self.set(soption, svalue):
            self.save()
        else:
            raise Exception("easysettings: unable to set option: " + \
                  soption + "=" + svalue)
            return False
      
    def get(self, soption, sdefault = ""):
        """ retrieves a setting from config file 
            Returns sdefault ("") if no setting found.
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


    def configfile_create(self, sfilename = None):
        """ creates a blank config file.
            if sfilename is given then current config file (self.configfile)
               is set to sfilename.
            if no sfilename is given then current config file is used.
            Returns False if no configfile is set, or on other failure.
            ** Overwrites file if it exists! ***
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
        """
        if os.path.isfile(self.configfile):
            return True
        else:
            if bcreateblank:
                return self.configfile_create()
            else:
                return False
    
    def list_settings(self):
        """ Returns a list of all settings.
            like: ["setting1=value1", "setting2=value2", ...]
        """
        lst_tmp = []
        for skey in self.settings.iterkeys():
            lst_tmp.append(skey + "=" + self.settings[skey])
        return lst_tmp

def test_run():    
    # Test run / Example of use.
    print "EasySettings Test Run....\n"
    sconf_file = os.path.join(sys.path[0], "easysettings_test.conf")
    print "\nCreating EasySettings object [easysettings.easysettings(" + sconf_file + ")]"
    settings = easysettings(sconf_file)

    print "\nMaking sure file exists, creating if needed. [configfile_exists(True)]"
    bexists = settings.configfile_exists()
    print "Config Exists: " + str(bexists)
    if not bexists:
        print "\nUnable to create config file: " + sconf_file
    
    print "\nRemoving config file... [rm " + sconf_file + "]"
    os.system('rm ' + sconf_file)
    
    print '\nMaking sure file exists, without creating it, [configfile_exists(False)]'
    bexists = settings.configfile_exists(False)
    if bexists:
        print "Config Exists: " + str(bexists)
    else:
        print "Config file does not exist, creating it manually... [configfile_create()]"
        settings.configfile_create()
           
    print "\nSetting option [user=cjw]... [set()]"
    settings.set("user", "cjw")
    
    print "\nSetting option [testing=true] and saving config...[setsave()]"
    settings.setsave("testing", "true")
    
    print "\nSetting option [okay=yes]... [set()]"
    settings.set("okay", "yes")
    
    print "\nSaving config manually... [save()]"
    settings.save()
    
    print "\nReloading config from file... [read_file()]"
    settings.read_file()
    
    print "\nRetrieving option [user]...[get()]"
    print "user=" + settings.get("user")
    
    print "\nListing all settings,,,[list_settings()]"
    for itm in settings.list_settings():
        print "    " + itm
        
    print "\nRetrieving unknown option with default set as [Unknown]... [get()]"
    print "notanoption=" + settings.get("notanoption", "Unknown")
    
    print "\nTrying to set illegal option [my=option], no '=' chars allowed..."
    try:
        settings.set("my=option", "myvalue")
    except Exception as ex:
        print "Error setting option:\n" + str(ex)
        
    print "\nFinished with test run, hope this helps you figure things out."
    print "\nRemoving test config file: " + sconf_file
    os.system('rm ' + sconf_file)
    
    print "Goodbye."
    exit(1)

if __name__ == "__main__":
    test_run()
    
    
            