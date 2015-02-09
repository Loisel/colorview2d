import logging
import yaml
import Mods
import Utils

from pydispatch import dispatcher
import Signal

class View:
    def __init__(self,datafile,modlist=[]):
        self.create_modlist()
        self.pipeline = []
        self.set_datafile(datafile)
        dispatcher.connect(self.handle_remove_mod_from_pipeline, Signal.VIEW_REMOVE_MOD_FROM_PIPELINE)
        dispatcher.connect(self.handle_add_mod_to_pipeline, Signal.VIEW_ADD_MOD_TO_PIPELINE)
        
        #self.config = {}

    def create_modlist(self):
        from yapsy.PluginManager import PluginManager
        self.modman = PluginManager()
        modpath = Utils.resource_path('Mods')
        self.modman.setPluginPlaces([modpath])

        self.modman.collectPlugins()

        self.modlist = [pInfo.plugin_object for pInfo in self.modman.getAllPlugins()]
        dispatcher.send(Signal.PANEL_ADD_MODWIDGETS,self,modlist=self.modlist)
    
        
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

    def handle_add_mod_to_pipeline(self, sender, title = None, args = None):
        """
        Adds a mod to the pipeline by its title string and its arguments.
        """
        self.pipeline.append((title,args))
        self.apply_pipeline()

    def handle_remove_mod_from_pipeline(self, sender, title = None):
        """
        Removes a mod from the pipeline by its title string.
        """
        for modtuple in self.pipeline:
            if modtuple[0] == title:
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
                mod.apply(self.datafile)
            else:
                logging.warning('No mod candidate found for {}.'.format(modtuple[0]))
        
        dispatcher.send(Signal.PLOT_UPDATE_DATAFILE, datafile = self.datafile)
        dispatcher.send(Signal.PANEL_UPDATE_COLORCTRL, minval = self.datafile.Zmin, maxval = self.datafile.Zmax)

    def reset(self):
        """
        Resets the datafile object by emptying the pipeline and
        deactivating all mods.
        """

        self.pipeline = []
        for mod in self.modlist:
            mod.deactivate()
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

