#import Mods
from Mods.ModWidget import ModWidget
import logging
from yapsy.IPlugin import IPlugin
import abc

class IMod(IPlugin):
    __meta__ = abc.ABCMeta
    def __init__(self):
        self.args = ()
        self.title = self.__class__.__name__
        logging.info('{} is initialized.'.format(self.title))
        self.active = False
        
    def set_args(self,args):
        self.args = args

    def activate(self):
        IPlugin.activate(self)
        logging.info("Activating mod {}.".format(self.title))
        self.active = True
        if hasattr(self,'widget'):
            self.widget.chk.SetValue(True)
        self.view.add_mod_to_pipeline(self.title,self.args)
        
    def deactivate(self):
        IPlugin.deactivate(self)
        logging.info("Deactivating mod {}.".format(self.title))
        self.active = False
        if hasattr(self,'widget'):
            self.widget.chk.SetValue(False)
        self.view.remove_mod_from_pipeline(self.title)
        
    def get_args(self):
        return self.args

    def register(self,view):
        self.view = view

    def update_widget(self):
        self.active = True
        if hasattr(self,'widget'):
            self.widget.update()
        else:
            logging.warning('Can not update widget: No widget created.')

    def create_widget(self,panel):
        self.panel = panel
        self.widget = ModWidget(self,self.panel)

        return self.widget
        
        
    def apply(self):
        logging.warning('The apply method of the base class Mod should not be called directly.')

