from colorview2d.Mods.ModWidget import ModWidget

import logging
from yapsy.IPlugin import IPlugin
import abc

"""
Interface to the mod plugin class.
Specification of the minimum requirements of a plugin implementation.
It also provides basic interaction with the ModWidget base class.
In particular, the checkbox of the widget is handled.
The following attributes are defined:

  title (string): Title string of the plugin. Usually equal to the
                  plugin/module name.
  args (tuple): The arguments that have to be provided to the mod to work.
  active (bool): The current state of the plugin.

"""

class IMod(IPlugin):
    __meta__ = abc.ABCMeta
    """
    The interface class is an abstract base class.
    At present, none of the methods have to be overwritten, though.
    """
    def __init__(self):
        """
        The init function should be called by the plugin implementation
        to correctly initialize the title and provide logging.
        """
        self.args = ()
        self.title = self.__class__.__name__
        logging.info('{} is initialized.'.format(self.title))
        self.active = False
        
    def set_args(self,args):
        self.args = args
    def get_args(self):
        return self.args

    def activate(self):
        """
        Activate the plugin. Usually, this method does not have to be
        overwritten by a plugin.
        The yapsy plugin activation routine is called.
        If a checkbox widget is defined, it is checked.
        The mod is added to the pipeline.
        """
        IPlugin.activate(self)
        logging.info("Activating mod {}.".format(self.title))
        self.active = True
        if hasattr(self,'widget'):
            self.widget.chk.SetValue(True)
        self.view.add_mod_to_pipeline(self.title,self.args)
        
    def deactivate(self):
        """
        Deactivate the plugin. Usually, this method does not have to be
        overwritten by a plugin.
        The yapsy plugin deactivation routine is called.
        If a checkbox widget is defined, it is unchecked.
        The mod is removed from the pipeline.
        """
        IPlugin.deactivate(self)
        logging.info("Deactivating mod {}.".format(self.title))
        self.active = False
        if hasattr(self,'widget'):
            self.widget.chk.SetValue(False)
        self.view.remove_mod_from_pipeline(self.title)
        

    def register(self,view):
        """
        Register the mod with a view object. This method is not meant to
        be overwritten.
        """
        self.view = view

    def update_widget(self):
        """
        Update the widget using the mod data.
        The mod is activated on call.
        
        """
        self.active = True
        if hasattr(self,'widget'):
            self.widget.update()
        else:
            logging.warning('Can not update widget: No widget created.')

    def create_widget(self,panel):
        """
        Create a widget for the plugin. This Method has to be overwritten
        to create a custom widget, i.e., a widget that contains more
        than a simple checkbox.

        Args:
          panel (wx.Panel): The panel object to create the widget on.
        Returns:
          widget (wx.ModWidget): The widget object.
        """
        self.panel = panel
        self.widget = ModWidget(self,self.panel)

        return self.widget
        
        
    def apply(self):
        """
        This method has to be overwritten to provide some useful
        functionality.
        It should modify the view object using the parameter in args.
        """
        logging.warning('The apply method of the base class Mod should not be called directly.')

