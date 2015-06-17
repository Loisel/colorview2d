import utils
import logging
import yaml
import Mods

from pydispatch import dispatcher
import signal

import sys

import matplotlib.pyplot
import warnings
from matplotlib.font_manager import FontProperties,findfont

# These imports are needed for the visibility of the modules
# to the yapsy plugins.
import imod
import modwidget


class Cv2d:
    def __init__(self, data = None, datafile = None, cfgfile = None):
        self.create_modlist()

        if data:
            self.set_datafile(gpfile.Gpfile(data))
        elif datafile:
            self.set_datafile(datafile)
        else:
            raise ValueError("Provide data or datafile keyword arguments to create a Cv2d object.")
                    

        if cfgfile:
            # If a config file is provided, we load that one.
            # All other parameters are ignored.
            cfgpath = os.path.join(os.getcwd(),cfgfile)
            datafilename = None
            columns = None
        else:
            # The name of the default config file is hard coded.
            # utils.resource_path adds the path to the 
            # library in win and linux
            cfgfile = utils.resource_path('default.cv2d')
            
        # The config file is parsed, 
        # modlist is a string variable that is given to the view
        # to create the mod pipeline
        view.parse_config(cfgfile)


    def create_modlist(self):
        """
        Creates the list of plugins in the Mods/ folder and adds them
        to the modlist attribute of the State class.

        The widgets of the mods are added to the MainPanel by sending
        'PANEL_ADD_MODWIDGETS'.
        """
        from yapsy.PluginManager import PluginManager
        modman = PluginManager()
        modpath = utils.resource_path('Mods')
        modman.setPluginPlaces([modpath])

        modman.collectPlugins()

        self.modlist = [pInfo.plugin_object for pInfo in modman.getAllPlugins()]

        if self.interactive:
            dispatcher.send(signal.PANEL_ADD_MODWIDGETS)


    def set_datafile(self, datafile):
        """
        Sets the datafile.
        The original datafile is replaced as well and the modlist is applied.

        :param datafile: a replacement for the datafile object in the :class:`State`
        :type datafile: :class:`gpfile <colorview2d.gpfile.gpfile>`
        """
        self.datafile = datafile
        self.original_datafile = datafile.deep_copy()
        if hasattr(self,'modlist'):
            apply_pipeline()

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline

    def dump_pipeline_string(self):
        """
        This just returns a string representation of the pipeline.

        :returns: The pipeline string
        """
        # return yaml.dump_all(self.modlist, explicit_start=True)
        return "{}".format(self.pipeline)

    def find_mod(self, modstring):
        """
        Check if a mod is available in the list of plugins.

        :param modstring: The name of the mod to search in the modlist.
        :returns: The mod, a :class:`IMod <colorview2d.IMod.Imod>`, if found, or None.
        """
        for mod in self.modlist:
            if mod.title == modstring:
                return mod

        return None

    def add_mod_to_pipeline(self, title, args):
        """
        Adds a mod to the pipeline by its title string and its arguments.

        :param title: The title of the mod
        :param args: A tuple containing the arguments of the mod.
        """
        self.pipeline.append((title,args))
        #apply_pipeline()

    def remove_mod_from_pipeline(self, title):
        """
        Removes a mod from the pipeline by its title string.

        :param title: The title of the mod
        """
        for modtuple in self.pipeline:
            if modtuple[0] == title:
                self.pipeline.remove(modtuple)

        #apply_pipeline()


    def reset(self):
        """
        Reset all mods.
        """
        if hasattr(self, 'modlist'):
            for mod in self.modlist:
                mod.reset()


    def apply_pipeline(self):
        """
        Applies the pipeline to the datafile in the parent frame.

        The datafile is first reverted to its original state,
        then mods are applied in the order they were added.
        The plot panel is notified of the update in the datafile.
        The main panel is signalled to update the color controls.
        """

        self.datafile = self.original_datafile.deep_copy()

        for modtuple in self.pipeline:
            mod = find_mod(modtuple[0])
            if mod:
                mod.set_args(modtuple[1])
                if self.interactive:
                    mod.update_widget()
                mod.apply(self.datafile)
            else:
                logging.warning('No mod candidate found for {}.'.format(modtuple[0]))

        if self.interactive:
            dispatcher.send(signal.PLOT_UPDATE_DATAFILE)
            dispatcher.send(signal.PANEL_UPDATE_COLORCTRL)

    def get_data(self):
        """
        Shortcut for the 2d data contained int the datafile. 
        Interface for plotting routine.
        """
        return self.datafile.Zdata


    def parse_config(self, cfgpath):
        """
        Load the configuration and the modlist from the config file
        specified in the YAML format.

        :param cfgpath: The path to a cv2d configuration file.
        """
        from ast import literal_eval

        with open(cfgpath) as file:
            doclist = yaml.load_all(file)
            # The config dict is the first yaml document
            self.config = doclist.next()
            # The pipeline string is the second. It is optional.
            try:
                self.pipeline = literal_eval(doclist.next())
                logging.info('Pipeline string found: {}'.format(self.pipeline))
            except StopIteration:
                self.pipeline = []

        reset()
        set_default_font()
        dispatcher.send(signal.CONFIG_UPDATE)

    def save_config(self, cfgpath):
        """
        Save the configuration and the pipeline to a config file specified by
        cfgpath.

        :param cfgpath: the path to the config file
        :type cfgpath: str
        """
        with open(cfgpath,'w') as stream:
            # We write first the config dict
            yaml.dump(self.config,stream,explicit_start=True)
            # ... and second the pipeline string
            yaml.dump(dump_pipeline_string(),stream,explicit_start=True)
