# -*- coding: utf-8 -*-
"""
The cvfig module hosts the CvFig class, the central object of cv2d.

Example::
    data = np.random.random((100, 100))
    fig = colorview2d.cvfig.CvFig(data)
    fig.show()

"""
import logging
import threading
import os

import numpy as np

import yaml
from pydispatch import dispatcher

import colorview2d.signal as signal
import colorview2d.mainapp as mainapp
import colorview2d.gpfile as gpfile
import colorview2d.utils as utils


class CvFig(object):
    """Colorview2d figure.
    In some respect similar to a matplotlib figure.

    Attributes:
        modlist (list): a list of all mods that could be found.
        datafile (colorview2d.GpFile): the datafile object encapsulates the 2d data
        pipeline (list): a list of mod identifiers (strings) that are currently in the mod pipeline

    """
    def __init__(self,
                 data=None,
                 cfgfile=None,
                 interactive=False):
        self.create_modlist()

        if isinstance(data, 'numpy.ndarray'):
            self.set_datafile(gpfile.Gpfile(data))
        elif isinstance(data, 'gpfile.Gpfile'):
            self.set_datafile(data)
        else:
            raise ValueError("Provide data or datafile to create a CvFig object.")

        if cfgfile:
            # If a config file is provided, we load that one.
            # All other parameters are ignored.
            # Note: The filename must be removed from the config file
            cfgpath = os.path.join(os.getcwd(), cfgfile)
        else:
            # The name of the default config file is hard coded.
            # utils.resource_path adds the path to the
            # library in win and linux
            cfgpath = utils.resource_path('default.cv2d')

        self.pipeline = []

        # The config file is parsed,
        # modlist is a string variable that is given to the view
        # to create the mod pipeline
        self.parse_config(cfgpath)

        dispatcher.connect(self.handle_add_mod_to_pipeline,
                           signal=signal.FIG_ADD_MOD_TO_PIPELINE,
                           sender=dispatcher.Any)
        dispatcher.connect(self.handle_remove_mod_from_pipeline,
                           signal=signal.FIG_REMOVE_MOD_FROM_PIPELINE,
                           sender=dispatcher.Any)

        self.apply_pipeline()

        if self.shell_is_interactive() or interactive:
            self.show()

    def show(self):
        """Show the figure in the GUI."""

        logging.info("Initializing the GUI.")
        self.mainapp = mainapp.MainApp(self)
        self.guithread = threading.Thread(target=self.mainapp.MainLoop)
        self.guithread.start()

    def hide(self):
        """Destroy the GUI."""
        if hasattr(self, 'mainapp'):
            self.mainapp.Destroy()
        logging.info("GUI destroyed.")

    def is_interactive(self):
        """Check if a GUI is initialized."""
        return hasattr(self, 'mainapp')

    @staticmethod
    def shell_is_interactive():
        """Check if we run in an interactive shell."""
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
        """Sets the datafile.
        The original datafile is replaced as well and the modlist is applied.

        Args:
            datafile (colorview2d.Gpfile): a Gpfile object
        """
        self.datafile = datafile
        self.original_datafile = datafile.deep_copy()

    def set_pipeline(self, pipeline):
        """Overwrite the pipeline string. Note that this is used for initialization
        and does not trigger any modifications to the datafile.

        Args:
            pipeline (list): A list of strings that are valid mod identifiers.
        """
        self.pipeline = pipeline

    def dump_pipeline_string(self):
        """This just returns a string representation of the pipeline."""
        return "{}".format(self.pipeline)

    def find_mod(self, modstring):
        """Check if a mod is available in the list of plugins.

        Args:
            modstring (string): The name of the mod to search in the modlist.

        Returns:
            a colorview2d.IMod
        """
        for mod in self.modlist:
            if mod.title == modstring:
                return mod

        return None

    def handle_add_mod_to_pipeline(self, modstring=None, modargs=None):
        """Handle an event that is triggered when the GUI is used to
        add a mod to the pipeline
        """
        self.add_mod_to_pipeline(modstring, modargs)

    def add_mod_to_pipeline(self, title, args, do_apply=True):
        """Adds a mod to the pipeline by its title string and its arguments.

        Args:
            title (string): The identifier of the mod type
            args (tuple): A tuple containing the arguments of the mod.
        """
        self.pipeline.append((title, args))

        if do_apply:
            self.apply_pipeline()

    def handle_remove_mod_from_pipeline(self, modstring=None):
        """Handle an event that is triggered when the GUI is used to
        remove a mod from the pipeline.
        """
        self.remove_mod_from_pipeline(modstring)

    def remove_mod_from_pipeline(self, title, do_apply=True):
        """Removes a mod from the pipeline by its title string.

        Args:
            title (string): The identifier of the mod type
        """
        for modtuple in self.pipeline:
            if modtuple[0] == title:
                self.pipeline.remove(modtuple)

        if do_apply:
            self.apply_pipeline()

    def reset(self):
        """Reset all mods."""
        if hasattr(self, 'modlist'):
            for mod in self.modlist:
                mod.reset()

    def apply_pipeline(self):
        """Applies the pipeline to the datafile in the parent frame.

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
                if self.is_interactive():
                    mod.update_widget()
                mod.apply(self.datafile)
            else:
                logging.warning('No mod candidate found for %s.', modtuple[0])

        if self.is_interactive():
            dispatcher.send(signal.PLOT_UPDATE_DATAFILE)
            dispatcher.send(signal.PANEL_UPDATE_COLORCTRL)

    def extract_ylinetraces(self, xfirst, xlast, xinterval, ystart, ystop):
        """Extract linetraces along a given y-axis range for
        values on the x axis within a given range and separated by
        a given interval.

        Args:
            xfirst, xlast (float): the values of the boundaries on the x-axis.
            xinterval (float): the interval between two linecuts on the x-axis.
            ystart, ystop (float): the y-axis range that is extracted.
        """
        # pylint: disable=too-many-arguments, too-many-locals
        linecuts = []

        x_left_idx = self.datafile.get_xrange_idx(xfirst)
        x_right_idx = self.datafile.get_xrange_idx(xlast)
        x_sign = np.sign(x_right_idx - x_left_idx)

        y_bottom_idx = self.datafile.get_yrange_idx(ystart)
        y_top_idx = self.datafile.get_yrange_idx(ystop)
        y_sign = np.sign(y_top_idx - y_bottom_idx)

        total_mininterval = np.absolute(self.datafile.dX)
        x_step_idx = int(xinterval / total_mininterval)

        position = x_left_idx

        while position * x_sign <= x_right_idx * x_sign:
            linecuts.append = np.vstack(
                [self.datafile.Yrange[y_bottom_idx:y_top_idx:y_sign],
                 self.datafile.Zdata[y_bottom_idx:y_top_idx:y_sign, position]])

            position += x_step_idx * x_sign
            if x_sign == 0:
                break

        return linecuts

    def extract_xlinetraces(self, yfirst, ylast, yinterval, xstart, xstop):
        """Extract linetraces along a given x-axis range for
        values on the y axis within a given range and separated by
        a given interval.

        Args:
            yfirst, ylast (float): the values of the boundaries on the y-axis.
            yinterval (float): the interval between two linecuts on the y-axis.
            xstart, xstop (float): the x-axis range that is extracted.
        """
        # pylint: disable=too-many-arguments, too-many-locals

        linecuts = []

        y_bottom_idx = self.datafile.get_yrange_idx(yfirst)
        y_top_idx = self.datafile.get_yrange_idx(ylast)
        y_sign = np.sign(y_top_idx - y_bottom_idx)

        x_left_idx = self.datafile.get_xrange_idx(xstart)
        x_right_idx = self.datafile.get_xrange_idx(xstop)
        x_sign = np.sign(x_right_idx - x_left_idx)

        total_mininterval = np.absolute(self.datafile.dY)

        y_step_idx = int(yinterval / total_mininterval)

        position = y_bottom_idx
        while position * y_sign <= y_top_idx * y_sign:
            linecuts.append = np.vstack(
                [self.datafile.Xrange[x_left_idx:x_right_idx:x_sign],
                 self.datafile.Zdata[position, x_left_idx:x_right_idx:x_sign]])

            position += y_step_idx * y_sign
            if y_sign == 0:
                break

        return linecuts

    def get_arraydata(self):
        """Shortcut for the 2d data contained int the datafile.
        Interface for plotting routine.
        """
        return self.datafile.Zdata

    def parse_config(self, cfgpath):
        """Load the configuration and the pipeline from the config file
        specified in the YAML format. Resets all mods in the pipeline.

        Args:
            cfgpath (string): The path to a cv2d configuration file.
        """
        from ast import literal_eval

        with open(cfgpath) as cfgfile:
            doclist = yaml.load_all(cfgfile)
            # The config dict is the first yaml document
            self.config = doclist.next()
            # The pipeline string is the second. It is optional.
            try:
                self.pipeline = literal_eval(doclist.next())
                logging.info('Pipeline string found: %s', self.pipeline)
            except StopIteration:
                self.pipeline = []

        self.reset()

        dispatcher.send(signal.CONFIG_UPDATE)

    def save_config(self, cfgpath):
        """Save the configuration and the pipeline to a config file specified by
        cfgpath.

        Args:
            cfgpath (string): the path to the config file
        """
        with open(cfgpath, 'w') as stream:
            # We write first the config dict
            yaml.dump(self.config, stream, explicit_start=True)
            # ... and second the pipeline string
            yaml.dump(self.dump_pipeline_string(), stream, explicit_start=True)

