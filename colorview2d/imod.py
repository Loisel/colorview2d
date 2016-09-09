
"""
IMod
----

Interface to the mod plugin class.
Specification of the minimum requirements of a plugin implementation.
"""

from modwidget import ModWidget

import logging
from yapsy.IPlugin import IPlugin
import abc


class IMod(IPlugin):
    """
    The interface class is an abstract base class.
    At present, none of the methods have to be overwritten, though.

    The following attributes are defined:

    :title (string): Title string of the plugin. Usually equal to the
                  plugin/module name.
    :default_args (tuple): A default set of arguments that works with the apply function.
    """
    __meta__ = abc.ABCMeta
    def __init__(self):
        """
        The init function should be called by the plugin implementation
        to correctly initialize the title and provide logging.
        """
        self.default_args = ()

        self.title = self.__class__.__name__
        logging.info('Mod %s is initialized.' % self.title)


    @staticmethod
    def handle_modfail(function):
        """This is a decorator for the apply function in the mod implementations.
        It is bound to the calling signature of the apply method.
        This enforces a correct implementation of mod.apply(self, datafile, args)
        """
        def decorated(self, datafile, args):
            try:
                function(self, datafile, args)
                return True
            except (ValueError, TypeError):
                logging.warn('Mod %s failed. Args: %s' % (self.title, args))
                return False
        return decorated


    def create_widget(self, panel):
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
        
    @handle_modfail    
    def apply(self,datafile):
        """
        This method has to be overwritten to provide some useful
        functionality.
        It should modify the :class:`Gpfile <colorview2d.gpfile.Gpfile>` object using the parameter in args.

        :param datafile: A :class:`Gpfile <colorview2d.gpfile.Gpfile>` object from the :mod:`gpfile` module.
        :type datafiel: :class:`Gpfile <colorview2d.gpfile.Gpfile>`
        """
        logging.warning('The apply method of the base class Mod should not be called directly.')















