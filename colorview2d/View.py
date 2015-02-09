import logging
import yaml
import Mods
import Utils

from pydispatch import dispatcher
import Signal

class State: pass

def set_pipeline(pipeline):
    State.pipeline = pipeline

def create_modlist():
    from yapsy.PluginManager import PluginManager
    modman = PluginManager()
    modpath = Utils.resource_path('Mods')
    modman.setPluginPlaces([modpath])

    modman.collectPlugins()

    State.modlist = [pInfo.plugin_object for pInfo in modman.getAllPlugins()]
    dispatcher.send(Signal.PANEL_ADD_MODWIDGETS)


def dump_pipeline_string():
    # return yaml.dump_all(State.modlist, explicit_start=True)
    return "{}".format(State.pipeline)

def find_mod(string):
    for mod in State.modlist:
        if mod.title == string:
            return mod

    return None

def add_mod_to_pipeline(title, args):
    """
    Adds a mod to the pipeline by its title string and its arguments.
    """
    State.pipeline.append((title,args))
    apply_pipeline()

def remove_mod_from_pipeline(title):
    """
    Removes a mod from the pipeline by its title string.
    """
    for modtuple in State.pipeline:
        if modtuple[0] == title:
            State.pipeline.remove(modtuple)

    apply_pipeline()


def apply_pipeline():
    """
    Applies the pipeline to the datafile in the parent frame.

    The datafile is first reverted to its original state,
    then mods are applied in the order they were added.
    Observers are notifed.
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

    dispatcher.send(Signal.PLOT_UPDATE_DATAFILE)
    dispatcher.send(Signal.PANEL_UPDATE_COLORCTRL)

def reset():
    """
    Resets the datafile object by emptying the pipeline and
    deactivating all mods.
    """

    State.pipeline = []
    for mod in State.modlist:
        mod.deactivate()
        apply_pipeline()

def get_data():
    """
    Shortcut for the 2d data contained int the datafile. 
    Interface for plotting routine.
    """
    return State.datafile.Zdata

def set_datafile(datafile):
    """
    Sets the datafile.
    The original datafile is replaced as well and the modlist is applied.

    Args:
    datafile: a datafile object
    """
    State.datafile = datafile
    State.original_datafile = datafile.deep_copy()
    apply_pipeline()

def parse_config(cfgpath):
    """
    Load the configuration and the modlist from the config file
    specified in the YAML format.

    Returns:
    config (dict): A configuration dict.
    modlist (list): A list of modification objects from the toolbox
    module
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


