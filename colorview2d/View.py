from Subject import Subject
import logging
import yaml
import Mods
import Utils

class View(Subject):
    def __init__(self,datafile,modlist=[]):
        Subject.__init__(self)
        self.create_modlist()
        self.pipeline = []
        self.set_datafile(datafile)
        #self.config = {}

    def create_modlist(self):
        from yapsy.PluginManager import PluginManager
        self.modman = PluginManager()
        modpath = Utils.resource_path('Mods')
        self.modman.setPluginPlaces([modpath])

        self.modman.collectPlugins()

        # Activate
        for pluginInfo in self.modman.getAllPlugins():
            #self.modman.activatePluginByName(pluginInfo.name)
            logging.info("Found mod {}".format(pluginInfo.name))
            pluginInfo.plugin_object.register(self)

        #import pdb;pdb.set_trace()
        self.modlist = [pInfo.plugin_object for pInfo in self.modman.getAllPlugins()]
        
    def dump_pipeline_string(self):
        # return yaml.dump_all(self.modlist, explicit_start=True)
        return "{}".format(self.pipeline)

    def load_pipeline_string(self,pipeline):
        from ast import literal_eval
        self.pipeline = literal_eval(pipeline)
        self.apply_pipeline()

    def find_mod(self,string):
        for mod in self.modlist:
            if mod.title == string:
                return mod
                
        return None

    def add_mod_to_pipeline(self,modstring,args):
        self.pipeline.append((modstring,args))
        self.apply_pipeline()

    def remove_mod_from_pipeline(self,modstring):
        print self.pipeline
        for modtuple in self.pipeline:
            if modtuple[0] == modstring:
                self.pipeline.remove(modtuple)

        self.apply_pipeline()

        
    def apply_pipeline(self):
        """
        Applies the pipeline to the datafile in the parent frame.
        
        The datafile is first reverted to its original state,
        then mods are applied in the order they were added.
        Observers are notifed.
        """

        self.datafile = self.original_datafile.deep_copy()
        
        for modtuple in self.pipeline:
            mod = self.find_mod(modtuple[0])
            if mod:
                mod.set_args(modtuple[1])
                mod.update_widget()
                mod.apply()
            else:
                logging.warning('No mod candidate found for {}.'.format(modtuple[0]))
        
        self.notify()

    def reset(self):
        """
        Resets the datafile object by emptying the pipeline.
        """

        self.pipeline = []
        self.apply_pipeline()
        
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
        self.apply_pipeline()

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
