
"""
.. module:: imod

IMod
----

Interface to the mod plugin class.
Specification of the minimum requirements of a plugin implementation.
It also provides basic interaction with the :class:`ModWidget <colorview2d.ModWidget.ModWidget>` class.
In particular, the checkbox of the widget is handled.

"""

from modwidget import ModWidget
from pydispatch import dispatcher
import signal

import logging
from yapsy.IPlugin import IPlugin
import abc

# import view


class IMod(IPlugin):
    """
    The interface class is an abstract base class.
    At present, none of the methods have to be overwritten, though.

    The following attributes are defined:

    :title (string): Title string of the plugin. Usually equal to the
                  plugin/module name.
    :args (tuple): The arguments that have to be provided to the mod to work.
    :active (bool): The current state of the plugin.
    """
    __meta__ = abc.ABCMeta
    def __init__(self):
        """
        The init function should be called by the plugin implementation
        to correctly initialize the title and provide logging.
        """
        self.args = self.default_args = ()

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

        #view.add_mod_to_pipeline(self.title,self.args)
        dispatcher.send(signal.FIG_ADD_MOD_TO_PIPELINE, self, modstring = self.title, modargs = self.args)
        
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

        #view.remove_mod_from_pipeline(self.title)
        dispatcher.send(signal.FIG_REMOVE_MOD_FROM_PIPELINE, self, modstring = self.title)


    def reset(self):
        """
        Reset the mod to default values.
        """
        self.args = self.default_args
        self.active = False
        if hasattr(self,'widget'):
            self.widget.update()
        

    def update_widget(self):
        """
        Update the widget using the mod data.
        
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

        Note that the widget is not added to a sizer on the panel but
        is returned as a box sizer.

        :param panel: The panel object to create the widget on.
        :type panel: `wx.Panel <http://www.wxpython.org/docs/api/wx.Panel-class.html>`_
        
        :returns: The widget object.
        :rtype: :class:`ModWidget <colorview2d.ModWidget.ModWidget>`
        """
        self.panel = panel
        self.widget = ModWidget(self,self.panel)

        return self.widget
        
        
    def apply(self,datafile):
        """
        This method has to be overwritten to provide some useful
        functionality.
        It should modify the :class:`Gpfile <colorview2d.gpfile.Gpfile>` object using the parameter in args.

        :param datafile: A :class:`Gpfile <colorview2d.gpfile.Gpfile>` object from the :mod:`gpfile` module.
        :type datafiel: :class:`Gpfile <colorview2d.gpfile.Gpfile>`
        """
        logging.warning('The apply method of the base class Mod should not be called directly.')

