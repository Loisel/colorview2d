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

from colorview2d import Datafile
import colorview2d.utils as utils

# setup logging

LOGGER = logging.getLogger('colorview2d')
LOGGER.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
FHAND = logging.FileHandler('spam.log')
FHAND.setLevel(logging.DEBUG)
# create console handler with a higher log level
CHAND = logging.StreamHandler()
CHAND.setLevel(logging.ERROR)
# create formatter and add it to the handlers
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
FHAND.setFormatter(FORMATTER)
CHAND.setFormatter(FORMATTER)
# add the handlers to the logger
LOGGER.addHandler(FHAND)
LOGGER.addHandler(CHAND)


class CvFig(object):
    """
    .. class:: CvFig(data[, axes_bounds])

    A class to handle a 2d :class:`numpy.ndarray` with (linearly scaled) axes, apply a (extendable)
    range of filters (mods) to the data while keeping track of the
    modifications.

    Hosts a :class:`matplotlib.pyplot.Figure`. Customization of this figure
    is simplified with respect to the matplotlib library.

    Attributes:
        modlist (list): a list of all mods that can be found in the mods/ subfolder.
        datafile (:class:`colorview2d.Datafile`): the colorview2d datafile object encapsulates the 2d data.
        pipeline (dict): a dictionary with mod identifiers (strings) and their arguments (tuples).
        _config (dict): the configuration of the _plot details, colormap, fonts, etc.
        fig (:class:`matplotlib.pyplot.Figure`): The matplotlib figure of the data with axes.

    Example::
        datafile = np.random.random((100, 100))
        fig = colorview2d.cvfig.CvFig(datafile)
        fig.plot_pdf('Test.pdf')


    """
    def __init__(self, data=None,
                 cfgfile=None,
                 config=None,
                 pipeline=None):

        self._modlist = {}
        self._create_modlist()

        self._datafile = None
        
        if isinstance(data, np.ndarray):
            self._datafile = Datafile(data)
        elif isinstance(data, Datafile):
            self.datafile = data
        else:
            raise ValueError("Provide data or datafile to create a CvFig object.")
        self._original_datafile = self._datafile.deep_copy()

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
        self._config = {}

        # The config file is parsed,
        # modlist is a string variable that is given to the view
        # to create the mod pipeline
        self.parse_config(cfgpath)

        # if the config argument is not empty we replace the values
        if config:
            for k, v in config:
                try:
                    self._config[k] = v
                except KeyError:
                    logging.warn('Config key %s not found.' % k)

        # Matplotlib figure object, contains the actual plot
        # Generated upon retrieval by property accessor
        # Readonly, Initialized with one pixel
        plt.ioff()
        self._fig = plt.figure(1, dpi=self._config['Dpi'])

        # We use the setter to add the given pipeline.
        if pipeline is not None:
            self.pipeline = pipeline

        self.apply_pipeline()

    def __repr__(self):
        print "CvFig(data=%r, config=%r, pipeline=%r)" % (self.data, self._config, self.pipeline)

    @property
    def modlist(self):
        return self._modlist
        
    @property
    def datafile(self):
        return self._datafile

    @datafile.setter
    def datafile(self, datafile):
        """Sets the datafile.
        The original datafile is replaced as well and the modlist is applied.

        Args:
            datafile (colorview2d.Datafile): a Datafile object
        """
        self._datafile = datafile
        self._datafile_changed()


    def _datafile_changed(self):
        """Called when the datafile is modified."""

        if hasattr(self, '_plot'):
            self._plot.set_data(self._datafile.zdata)
            self._plot.set_extent([self._datafile.xleft, self._datafile.xright,
                                   self._datafile.ybottom, self._datafile.ytop])
            self.axes.set_xlim(self._datafile.xleft, self._datafile.xright)
            self.axes.set_ylim(self._datafile.ybottom, self._datafile.ytop)
            self._plot.changed()
        return


    @property
    def fig(self):
        """Retrieve the matplotlib figure."""
        if not hasattr(self, '_plot'):
            self.draw_plot()
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
            self.add_mod(modstring)

    @property
    def config(self):
        return self._config
    
    @config.setter
    def config(self, config_dict):
        """Change the config. If there is a plot object (because the session is interactive)
        we update the plot accordingly.

        Be careful when overwriting the config because there is no error checking.
        """
        if not set(config_dict.keys()).issubset(set(self._config.keys())):
            raise KeyError('Not a valid configuration dict. Check the spelling of the keys.')
        else:
            self._config.update(config_dict)

        # When there is no plot we do not care at the moment.
        if not hasattr(self, '_plot'):
            return
            
        # If config_dict only contains changes that update the colorbar we
        # apply them and return
        colorbar_keys = set(['Colormap', 'Cbmin', 'Cbmax'])
        if set(config_dict.keys()).issubset(colorbar_keys):
            self._plot.set_cmap(self._config['Colormap'])
            if self._config['Cbmin'] == 'auto':
                self._plot.set_clim(vmin=self._datafile.zmin)
            else:
                self._plot.set_clim(vmin=self._config['Cbmin'])
            if self._config['Cbmax'] == 'auto':
                self._plot.set_clim(vmax=self._datafile.zmax)
            else:
                self._plot.set_clim(vmax=self._config['Cbmax'])
            self._plot.changed()
            return

        # If config_dict only contains changes that do not need a redrawing
        # of the plot we apply them and return
        soft_keys = set(['Xlabel', 'Ylabel', 'Xtickformat', 'Ytickformat', 'Cblabel'])
        if set(config_dict.keys()).issubset(soft_keys):
            self._apply_config_post_plot()
            return

        # If the font parameters or the ticksize is changed, we have to redraw the plot
        self.draw_plot()

        
    def show(self):
        """Show the figure in the GUI.
        Can be used only if wxpython is installed.
        """

        try:
            import colorview2d.mainapp as mainapp
        except ImportError:
            logging.error('Cannot start the GUI. Is wxpython installed?')
            return
        
        logging.info("Initializing the GUI.")
        self.mainapp = mainapp.MainApp(self)
        self.mainapp.MainLoop()

    def show_plt_fig(self):
        """Show the interactive :class:`matplotlib.pyplot.Figure`."""
        self.draw_plot()
        plt.ion()
        self._fig.show()

    def _create_modlist(self):
        """
        Creates the list of mods from the mods/ folder and adds them
        to the private modlist attribute.

        We check if the module (with arbitrary name) contains a class
        which inherits from colorview2d.IMod
        """
        import pkgutil
        import inspect

        import colorview2d.mods

        package = colorview2d.mods
        for importer, modname, ispckg in pkgutil.iter_modules(package.__path__):
            mod = importer.find_module(modname).load_module(modname)
            for name, obj in inspect.getmembers(mod):
                if inspect.isclass(obj):
                    if issubclass(obj, colorview2d.IMod):
                        self._modlist[name] = obj()
        # import ipdb;ipdb.set_trace()


    def dump_pipeline_string(self):
        """This just returns a string representation of the pipeline."""
        return "{}".format(self._pipeline)


    def add_mod(self, modstring, pos=-1, do_apply=True):
        """Adds a mod to the pipeline by its title string and its arguments.

        Args:
            pos (int): Where to add the mod in the pipeline. Default is last.
            modstring (tuple): Mod type string and arguments.
            args (tuple): A tuple containing the arguments of the mod.
        """
        title = modstring[0]

        logging.info('Add mod %s to pipeline with arguments %s' % (modstring[0], modstring[1]))
        if self._modlist[title]:
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

    def remove_mod(self, pos=-1, modtype=None, do_apply=True):
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

        self._datafile = self._original_datafile.deep_copy()

        for pos, modtuple in enumerate(self._pipeline):
            mod = self._modlist[modtuple[0]]
            if mod:
                # if apply returns false, the application failed and the
                # mod is removed from the pipeline
                if not mod.apply(self._datafile, modtuple[1]):
                    logging.warning(
                        'Application of mod %s at position %d failed.'
                        'Removing mod from pipeline.' % (mod.title, pos))
                    self.remove_mod(pos)
                self._datafile_changed()
            else:
                logging.warning('No mod candidate found for %s.', modtuple[0])


    def get_arraydata(self):
        """Shortcut for the 2d data contained int the datafile.
        Interface for plotting routine.
        """
        return self.datafile.zdata

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
            self._config = doclist.next()
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
            yaml.dump(self._config, stream, explicit_start=True)
            # ... and second the pipeline string
            yaml.dump(self.dump_pipeline_string(), stream, explicit_start=True)

    def plot_pdf(self, filename):
        """Redraw the figure and plot it to a pdf file."""
        self.draw_plot()
        self._fig.set_size_inches(self._config['Width'], self._config['Height'])
        self._fig.tight_layout()
        self._fig.savefig(filename, dpi=self._config['Dpi'])

    def draw_plot(self):
        """Draw a matplotlib figure.

        The figure is stored in the fig attribute.
        In includes an axes object containing the (imshow generated)
        2d color plot with labels, ticks and colorbar as specified in the
        config dictionary..
        """
        self._fig.clear()
        self.axes = self._fig.add_subplot(111)
        self._apply_config_pre_plot()

        self._plot = self.axes.imshow(self.get_arraydata(),
            extent=[self.datafile.xleft,
                    self.datafile.xright,
                    self.datafile.ybottom,
                    self.datafile.ytop],
            aspect='auto',
            origin='lower',
            interpolation="nearest")

        if not self._config['Cbtickformat'] == 'auto':
            self.colorbar = self._fig.colorbar(
                self._plot,
                format=FormatStrFormatter(self._config['Cbtickformat']))
        else:
            self.colorbar = self._fig.colorbar(self._plot)

        self._apply_config_post_plot()

        self._fig.tight_layout()


    def _apply_config_post_plot(self):
        """
        The function applies the rest of the configuration to the plot.
        Note that the colorbar is created in this function because
        colorbar.ax.yaxis.set_major_formatter(FormatStrFormatter(string)) does not work properly.
        """
        self.axes.set_ylabel(self._config['Ylabel'])
        self.axes.set_xlabel(self._config['Xlabel'])

        self.colorbar.set_label(self._config['Cblabel'])
        if not self._config['Xtickformat'] == 'auto':
            self.axes.xaxis.set_major_formatter(FormatStrFormatter(self._config['Xtickformat']))
        if not self._config['Ytickformat'] == 'auto':
            self.axes.yaxis.set_major_formatter(FormatStrFormatter(self._config['Ytickformat']))
        self._plot.set_cmap(self._config['Colormap'])


    def _apply_config_pre_plot(self):
        """
        Applies the ticks and labels stored in the MainFrame.
        This function is called before the actual plot is drawn.
        This pre_plot hook is necessary because the rcParams['font.family']
        attribute can not be changed after the plot is drawn.
        """

        logging.info("Font now {}".format(self._config['Font']))
        
        plt.rcParams['font.family'] = self._config['Font']
        plt.rcParams['font.size'] = self._config['Fontsize']
        plt.rcParams['xtick.major.size'] = self._config['Xticklength']
        plt.rcParams['ytick.major.size'] = self._config['Yticklength']

    
