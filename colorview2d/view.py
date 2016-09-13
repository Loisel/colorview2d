"""
The 'global state module' of the application.
In the State class all application wide configuration
is stored. The functions defined in this module are
utility routines to fill the State class with
config information.
"""


import logging
import yaml
import Mods
import utils

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



class State:
    """
    The state object is used to store the global state of the application.

    :ivar conf: A dictionary containing all the configuration options including those from the config file
    :ivar datafile: A :class:`gpfile <colorview2d.gpfile.gpfile>` object hosting the current plot.
    :ivar pipeline: A list of strings containing the name and the parameters of the applied modifications.
    :ivar modlist: A list of detected plugin (mod) objects.
    """
    pass


def set_pipeline(pipeline):
    State.pipeline = pipeline

def create_modlist():
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

    State.modlist = [pInfo.plugin_object for pInfo in modman.getAllPlugins()]

    dispatcher.send(signal.PANEL_ADD_MODWIDGETS)


def dump_pipeline_string():
    """
    This just returns a string representation of the pipeline.

    :returns: The pipeline string
    """
    # return yaml.dump_all(State.modlist, explicit_start=True)
    return "{}".format(State.pipeline)

def find_mod(modstring):
    """
    Check if a mod is available in the list of plugins.

    :param modstring: The name of the mod to search in the modlist.
    :returns: The mod, a :class:`IMod <colorview2d.IMod.Imod>`, if found, or None.
    """
    for mod in State.modlist:
        if mod.title == modstring:
            return mod

    return None

def add_mod_to_pipeline(title, args):
    """
    Adds a mod to the pipeline by its title string and its arguments.

    :param title: The title of the mod
    :param args: A tuple containing the arguments of the mod.
    """
    State.pipeline.append((title,args))
    apply_pipeline()

def remove_mod_from_pipeline(title):
    """
    Removes a mod from the pipeline by its title string.

    :param title: The title of the mod
    """
    for modtuple in State.pipeline:
        if modtuple[0] == title:
            State.pipeline.remove(modtuple)

    apply_pipeline()


def reset():
    """
    Reset all mods.
    """
    if hasattr(State, 'modlist'):
        for mod in State.modlist:
            mod.reset()


def apply_pipeline():
    """
    Applies the pipeline to the datafile in the parent frame.

    The datafile is first reverted to its original state,
    then mods are applied in the order they were added.
    The plot panel is notified of the update in the datafile.
    The main panel is signalled to update the color controls.
    """

    State.datafile = State.original_datafile.deep_copy()

    for modtuple in State.pipeline:
        mod = find_mod(modtuple[0])
        if mod:
            mod.set_args(modtuple[1])
            mod.update_widget()
            mod.apply(State.datafile)
        else:
            logging.warning('No mod candidate found for {}.'.format(modtuple[0]))

    dispatcher.send(signal.PLOT_UPDATE_DATAFILE)
    dispatcher.send(signal.PANEL_UPDATE_COLORCTRL)


def set_default_font():
    """
    If there is no specific font specified in the config file, i.e.,
    Font is set to 'default', the local installation's default font
    is selected for config['Font']
    """
    # We select the default matplotlib font
    # To that end we catch the warning -- not particularly elegant
    if State.config['Font'] == 'default':
        for font in matplotlib.pyplot.rcParams['font.sans-serif']:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                findfont(FontProperties(family=font))
                if len(w):
                    continue
                else:
                    State.config['Font'] = font
                    break

    

def get_data():
    """
    Shortcut for the 2d data contained int the datafile. 
    Interface for plotting routine.
    """
    return State.datafile.zdata

def set_datafile(datafile):
    """
    Sets the datafile.
    The original datafile is replaced as well and the modlist is applied.

    :param datafile: a replacement for the datafile object in the :class:`State`
    :type datafile: :class:`gpfile <colorview2d.gpfile.gpfile>`
    """
    State.datafile = datafile
    State.original_datafile = datafile.deep_copy()
    if hasattr(State,'modlist'):
        apply_pipeline()

def parse_config(cfgpath):
    """
    Load the configuration and the modlist from the config file
    specified in the YAML format.

    :param cfgpath: The path to a cv2d configuration file.
    """
    from ast import literal_eval

    with open(cfgpath) as file:
        doclist = yaml.load_all(file)
        # The config dict is the first yaml document
        State.config = doclist.next()
        # The pipeline string is the second. It is optional.
        try:
            State.pipeline = literal_eval(doclist.next())
            logging.info('Pipeline string found: {}'.format(State.pipeline))
        except StopIteration:
            State.pipeline = []

    reset()
    set_default_font()
    dispatcher.send(signal.CONFIG_UPDATE)

def save_config(cfgpath):
    """
    Save the configuration and the pipeline to a config file specified by
    cfgpath.

    :param cfgpath: the path to the config file
    :type cfgpath: str
    """
    with open(cfgpath,'w') as stream:
        # We write first the config dict
        yaml.dump(State.config,stream,explicit_start=True)
        # ... and second the pipeline string
        yaml.dump(dump_pipeline_string(),stream,explicit_start=True)
