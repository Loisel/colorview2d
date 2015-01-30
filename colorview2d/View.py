from Subject import Subject
import logging
import yaml
import Mods

class View(Subject):
    def __init__(self,datafile,modlist=[]):
        Subject.__init__(self)
        self.create_modlist()
        self.set_datafile(datafile)
        #self.config = {}

    def create_modlist(self):
        from yapsy.PluginManager import PluginManager
        self.modman = PluginManager()
        self.modman.setPluginPlaces(['Mods'])

        self.modman.collectPlugins()

        # Activate
        for pluginInfo in self.modman.getAllPlugins():
            #self.modman.activatePluginByName(pluginInfo.name)
            logging.info("Found mod {}".format(pluginInfo.name))
            pluginInfo.plugin_object.register(self)

        #import pdb;pdb.set_trace()
        self.modlist = [pInfo.plugin_object for pInfo in self.modman.getAllPlugins()]
        
    def dump_list(self):
        # return yaml.dump_all(self.modlist, explicit_start=True)
        modstringlist = []
        for mod in self.modlist:
            if mod.active:
                modstringlist.append("{},{}".format(mod.title,mod.args))
        return modstringlist
                            

    def set_list(self,modstringlist):
        from ast import literal_eval
        #print "Im called with {}".format(modstringlist)

        for modstring in modstringlist:
            # create mod

            modtitle = modstring.split(',',1)[0]
            modargs = modstring.split(',',1)[1]

            mod = self.find_mod(modtitle)
            if mod:
                mod.set_args(literal_eval(modargs))
                mod.update_widget()
                mod.activate()
            else:
                logging.warning('Found mod {} in config that has no plugin candidate.'.format(modtitle))
            
        self.apply()

    def find_mod(self,string):
        for mod in self.modlist:
            if mod.title == string:
                return mod
                
        return None
    

    def apply(self):
        """
        Applies the modlist to the datafile in the parent frame.
        
        The datafile is first reverted to its original state,
        then mods are applied in the order they were added.
        Observers are notifed.
        """

        self.datafile = self.original_datafile.deep_copy()

        for mod in self.modlist:
#            print "Applying mod {}".format(mod.title())
            if mod.active:
                mod.apply()
        
        self.notify()

    def reset(self):
        """
        Resets the datafile object by emptying the modlist.
        """

        self.modlist = []
        self.apply()
        
    def get_data(self):
        """
        Shortcut for the 2d data contained int the datafile. 
        Interface for plotting routine.
        """
        return self.datafile.Zdata

    def set_datafile(self,datafile):
        """
        Sets the datafile.
        The original datafile is replaced as well and the modlist is applied.

        Args:
          datafile: a datafile object
        """
        self.datafile = datafile
        self.original_datafile = datafile.deep_copy()
        self.apply()

    def rotate_cw(self):
        """
        Resets the datafile and rotates it clockwise.
        """

        # datafile.rotate returns a rotated version of self.
        # That is why set_datafile is used.

        self.reset()
        self.set_datafile(self.datafile.rotate_cw())

    def rotate_ccw(self):
        """
        Resets the datafile and rotates it anti-clockwise.
        """

        # datafile.rotate returns a rotated version of self.
        # That is why set_datafile is used.

        self.reset()
        self.set_datafile(self.datafile.rotate_ccw())
