# -*- coding: utf-8 -*-
"""
The cvfig module hosts the CvFig class, the central object of cv2d.

Example::
    data = np.random.random((100, 100))
    fig = colorview2d.cvfig.CvFig(data)
    fig.show()

"""
import logging
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

import yaml

import colorview2d.mainapp as mainapp
import colorview2d.gpfile as gpfile
import colorview2d.utils as utils


class CvFig(object):
    """Colorview2d figure.
    In some respect similar to a matplotlib figure.

    Attributes:
        modlist (list): a list of all mods that could be found.
        datafile (colorview2d.GpFile): the datafile object encapsulates the 2d data
        pipeline (list): a list of tuples with mod identifiers (strings) 
            and their arguments (tuples).
        config (dict): the configuration of the plot details, colormap, fonts, etc.

    """
    def __init__(self, data=None,
                 cfgfile=None,
                 config=None,
                 pipeline=None):
        self.create_modlist()

        if isinstance(data, np.ndarray):
            self.set_datafile(gpfile.Gpfile(data))
        elif isinstance(data, gpfile.Gpfile):
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

        # The pipeline contains a dict of numbers and tuples with
        # strings that are unique to IMod objects
        # and their arguments
        self._pipeline = []

        # Holds information on the plot layout, ticks, fonts etc.
        self.config = {}

        # The config file is parsed,
        # modlist is a string variable that is given to the view
        # to create the mod pipeline
        self.parse_config(cfgpath)

        # if the config argument is not empty we replace the values
        if config:
            for k, v in config:
                try:
                    self.config[k] = v
                except KeyError:
                    logging.warn('Config key %s not found.' % k)

        # Matplotlib figure object, contains the actual plot
        # Generated upon retrieval by property accessor
        # Readonly, Initialized with one pixel
        plt.ioff()
        self._fig = plt.figure(1, dpi=self.config['Dpi'])

        # We use the setter to add the given pipeline.
        if pipeline is not None:
            self.pipeline = pipeline

        self.apply_pipeline()

    def __repr__(self):
        print "CvFig(data=%r, config=%r, pipeline=%r)" % (self.data, self.config, self.pipeline)

    @property
    def fig(self):
        """Retrieve the matplotlib figure."""
        self.draw_mpl_fig()
        return self._fig

    @property
    def pipeline(self):
        return self._pipeline

    @pipeline.setter
    def pipeline(self, pipeline):
        """Overwrite the pipeline string. Note that this is used for initialization
        and does not trigger any modifications to the datafile.

        Args:
            pipeline (list): A list of strings that are valid mod identifiers.
        """
        self._pipeline = []

        for modstring in pipeline:
            self.add_mod_to_pipeline(modstring)

    def show(self):
        """Show the figure in the GUI."""

        logging.info("Initializing the GUI.")
        self.mainapp = mainapp.MainApp(self)
        self.mainapp.MainLoop()

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

    def set_datafile(self, datafile):
        """Sets the datafile.
        The original datafile is replaced as well and the modlist is applied.

        Args:
            datafile (colorview2d.Gpfile): a Gpfile object
        """
        self.datafile = datafile
        self.original_datafile = datafile.deep_copy()

    def dump_pipeline_string(self):
        """This just returns a string representation of the pipeline."""
        return "{}".format(self._pipeline)

    def find_mod(self, modtype):
        """Check if a modtype is available in the list of plugins.

        Args:
            modtype (string): The name of the mod to search in the modlist.

        Returns:
            a colorview2d.IMod
        """
        for mod in self.modlist:
            if mod.title == modtype:
                return mod

        return None

    def add_mod_to_pipeline(self, modstring, pos=-1, do_apply=True):
        """Adds a mod to the pipeline by its title string and its arguments.

        Args:
            pos (int): Where to add the mod in the pipeline. Default is last.
            modstring (tuple): Mod type string and arguments.
            args (tuple): A tuple containing the arguments of the mod.
        """
        title = modstring[0]

        logging.info('Add mod %s to pipeline with arguments %s' % (modstring[0], modstring[1]))
        if self.find_mod(title):
            if pos == -1:
                self._pipeline.append(modstring)
            elif pos < len(self._pipeline) and pos >= 0:
                self._pipeline.insert(pos, modstring)
            else:
                logging.warn('Position %d not available in pipeline.' % pos)
        else:
            logging.warn('Mod %s not available in mod plugin list.' % title)

        if do_apply:
            self.apply_pipeline()

    def remove_mod_from_pipeline(self, pos=-1, modtype=None, do_apply=True):
        """Removes the last mod from the pipeline, or the mod at position pos
        or the last mod in the pipeline with the type modtype.

        Args:
            modtype (string): The identifier of the mod type.
            pos (int): The position of the mod in the pipeline.
            do_apply (bool): Is the pipeline applied after the element is removed?
        """

        if pos == -1 and not modtype:
            self._pipeline.pop()
        elif pos >= 0 and pos < len(self._pipeline):
            del self._pipeline[pos]
        elif modtype:
            found = False
            for modtuple in reversed(self._pipeline):
                if modtuple[0] == modtype:
                    self._pipeline.remove(modtuple)
                    found = True
            if not found:
                logging.warn('Mod %s not in current pipeline.' % modtype)
        else:
                logging.warn('Pos = %d is not a valid position.' % pos)

        if do_apply:
            self.apply_pipeline()

    def apply_pipeline(self):
        """Applies the pipeline to the datafile in the parent frame.

        The datafile is first reverted to its original state,
        then mods are applied in the order they were added.
        The plot panel is notified of the update in the datafile.
        The main panel is signalled to update the color controls.
        """

        self.datafile = self.original_datafile.deep_copy()

        for pos, modtuple in enumerate(self._pipeline):
            mod = self.find_mod(modtuple[0])
            if mod:
                # if apply returns false, the application failed and the
                # mod is removed from the pipeline
                if not mod.apply(self.datafile, modtuple[1]):
                    logging.warning(
                        'Application of mod %s at position %d failed.'
                        'Removing mod from pipeline.' % (mod.title, pos))
                    self.remove_mod_from_pipeline(pos)
            else:
                logging.warning('No mod candidate found for %s.', modtuple[0])

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
        specified in the YAML format. 

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
                logging.info('Pipeline string found: %s', self.pipeline)
                pipeline = literal_eval(doclist.next())
                # Note that the property setter is called
                self.pipeline = pipeline

            except StopIteration:
                logging.info('No pipeline string found.')


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

    def plot_pdf(self, filename):
        """Redraw the figure and plot it to a pdf file."""
        self.draw_mpl_fig()
        self._fig.set_size_inches(self.config['Width'], self.config['Height'])
        self._fig.tight_layout()
        self._fig.savefig(filename, dpi=self.config['Dpi'])

    def draw_mpl_fig(self):
        """Draw a matplotlib figure.

        The figure is stored in the fig attribute.
        In includes an axes object containing the (imshow generated)
        2d color plot with labels, ticks and colorbar as specified in the
        config dictionary..
        """
        self._fig.clear()
        self.axes = self._fig.add_subplot(111)
        self.apply_config_pre_plot()

        self.plot = self.axes.imshow(self.get_arraydata(),
            extent=[self.datafile.Xleft,
                    self.datafile.Xright,
                    self.datafile.Ybottom,
                    self.datafile.Ytop],
            aspect='auto',
            origin='lower',
            interpolation="nearest")

        self.apply_config_post_plot()

        self._fig.tight_layout()


    def apply_config_post_plot(self):
        """
        The function applies the rest of the configuration to the plot.
        Note that the colorbar is created in this function because
        colorbar.ax.yaxis.set_major_formatter(FormatStrFormatter(string)) does not work properly.
        """
        self.axes.set_ylabel(self.config['Ylabel'])
        self.axes.set_xlabel(self.config['Xlabel'])

        if not self.config['Cbtickformat'] == 'auto':
            self.colorbar = self._fig.colorbar(
                self.plot,
                format=FormatStrFormatter(self.config['Cbtickformat']))
        else:
            self.colorbar = self._fig.colorbar(self.plot)
        self.colorbar.set_label(self.config['Cblabel'])
        if not self.config['Xtickformat'] == 'auto':
            self.axes.xaxis.set_major_formatter(FormatStrFormatter(self.config['Xtickformat']))
        if not self.config['Ytickformat'] == 'auto':
            self.axes.yaxis.set_major_formatter(FormatStrFormatter(self.config['Ytickformat']))
        self.plot.set_cmap(self.config['Colormap'])


    def apply_config_pre_plot(self):
        """
        Applies the ticks and labels stored in the MainFrame.
        This function is called before the actual plot is drawn.
        This pre_plot hook is necessary because the rcParams['font.family']
        attribute can not be changed after the plot is drawn.
        """

        logging.info("Font now {}".format(self.config['Font']))
        
        plt.rcParams['font.family'] = self.config['Font']
        plt.rcParams['font.size'] = self.config['Fontsize']
        plt.rcParams['xtick.major.size'] = self.config['Xticklength']
        plt.rcParams['ytick.major.size'] = self.config['Yticklength']

    
