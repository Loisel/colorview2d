import logging
import yaml
import Mods

from pydispatch import dispatcher

import sys
import os

import matplotlib.pyplot
import warnings
from matplotlib.font_manager import FontProperties,findfont

# These imports are needed for the visibility of the modules
# to the yapsy plugins.

#import colorview2d.imod as imod
#import colorview2d.modwidget as modwidget
#import colorview2d.gpfile as gpfile
#import colorview2d.utils as utils
#import colorview2d.signal as signal
#import colorview2d.mainapp as mainapp
import mainapp
import imod
import modwidget
import gpfile
import utils
import signal

class CvFig:
    def __init__(self, 
                 data = None, 
                 datafile = None, 
                 datafilename = None, 
                 datafilecolumns = None, 
                 cfgfile = None, 
                 interactive = False):
        self.create_modlist()

        self.interactive = False

        dispatcher.connect(self.handle_add_mod_to_pipeline, signal = signal.FIG_ADD_MOD_TO_PIPELINE, sender = dispatcher.Any)
        dispatcher.connect(self.handle_remove_mod_from_pipeline, signal = signal.FIG_REMOVE_MOD_FROM_PIPELINE, sender = dispatcher.Any)
        
        if data:
            self.set_datafile(gpfile.Gpfile(data))
        elif datafile:
            self.set_datafile(datafile)
        elif datafilename:
            if not datafilecolumns:
                datafilecolumns = (0,1,2)
            self.set_datafile(gpfile.Gpfile(datafilename,datafilecolumns))
        else:
            raise ValueError("Provide data, datafile or datafilename keyword arguments to create a Cv2d object.")
                    

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
        self.parse_config(cfgfile)

        self.apply_pipeline()

        if self.is_interactive() or interactive:
            self.interactive = True
            print "Interactive mode."
            # logging.info("Interactive mode.")
            self.mainapp = mainapp.MainApp(self)
            self.mainapp.MainLoop()

    def is_interactive(self):
        import __main__ as main
        return hasattr(main, '__file__')

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

        # if self.interactive:
        #     dispatcher.send(signal.PANEL_ADD_MODWIDGETS)


    def set_datafile(self, datafile):
        """
        Sets the datafile.
        The original datafile is replaced as well and the modlist is applied.

        :param datafile: a replacement for the datafile object in the :class:`State`
        :type datafile: :class:`gpfile <colorview2d.gpfile.gpfile>`
        """
        self.datafile = datafile
        self.original_datafile = datafile.deep_copy()

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

    def handle_add_mod_to_pipeline(self, sender, modstring = None, modargs = None):
        self.add_mod_to_pipeline(modstring, modargs)

        
    def add_mod_to_pipeline(self, title, args, DoApply = True):
        """
        Adds a mod to the pipeline by its title string and its arguments.

        :param title: The title of the mod
        :param args: A tuple containing the arguments of the mod.
        """
        self.pipeline.append((title,args))

        if DoApply:
            self.apply_pipeline()

    def handle_remove_mod_from_pipeline(self, sender, modstring = None):
        self.remove_mod_from_pipeline(modstring)
        
    def remove_mod_from_pipeline(self, title, DoApply = True):
        """
        Removes a mod from the pipeline by its title string.

        :param title: The title of the mod
        """
        for modtuple in self.pipeline:
            if modtuple[0] == title:
                self.pipeline.remove(modtuple)

        if DoApply:
            self.apply_pipeline()


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
            mod = self.find_mod(modtuple[0])
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

    def extract_ylinetraces(xfirst, xlast, xinterval, ystart, ystop):

        linecuts = []

        x_left_idx = self.datafile.get_xrange_idx(xfirst)
        x_right_idx = self.datafile.get_xrange_idx(xlast)
        x_sign = np.sign(x_right_idx-x_left_idx)

        y_bottom_idx = self.datafile.get_yrange_idx(ystart)
        y_top_idx = self.datafile.get_yrange_idx(ystop)
        y_sign = np.sign(y_top_idx-y_bottom_idx)

        total_mininterval = np.absolute(self.datafile.dX)
        x_step_idx = int(xinterval/total_mininterval)

        position = x_left_idx

        while position*x_sign <= x_right_idx*x_sign:

            xval = self.datafile.Xrange[position]
                
            linecuts.append = np.vstack([self.datafile.Yrange[y_bottom_idx:y_top_idx:y_sign], self.datafile.Zdata[y_bottom_idx:y_top_idx:y_sign,position]])
                
            position += x_step_idx*x_sign
            if x_sign == 0:
                break

        return linecuts

    def extract_xlinetraces(yfirst, ylast, yinterval, xstart, xstop):

        linecuts = []

        y_bottom_idx = self.datafile.get_yrange_idx(yfirst)
        y_top_idx = self.datafile.get_yrange_idx(ylast)
        y_sign = np.sign(y_top_idx-y_bottom_idx)

        x_left_idx = self.datafile.get_xrange_idx(xstart)
        x_right_idx = self.datafile.get_xrange_idx(xstop)
        x_sign = np.sign(x_right_idx-x_left_idx)

        total_mininterval = np.absolute(self.datafile.dY)

        y_step_idx = int(yinterval/total_mininterval)

        position = y_bottom_idx
        while position*y_sign <= y_top_idx*y_sign:

            yval = self.datafile.Yrange[position]

            linecuts.append = np.vstack([self.datafile.Xrange[x_left_idx:x_right_idx:x_sign],self.datafile.Zdata[position,x_left_idx:x_right_idx:x_sign]])

            position += y_step_idx*y_sign
            if y_sign == 0:
                break

        return linecuts

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

        self.reset()

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
