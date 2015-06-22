import sys
import logging
from optparse import OptionParser

from pydispatch import dispatcher
import utils
from mainframe import MainFrame
import wx



class MainApp(wx.App):
    """
    The colorview2d application object.
    It is used to parse the configuration
    and create the first View object.
    """
    
    def __init__(self, cvfig, redirect = False):
        self.cvfig = cvfig
        dispatcher.connect(self.handle_print_events)
        wx.App.__init__(self)

    def handle_print_events(self,sender,signal):
        logging.debug('{} sent signal: {}'.format(sender,signal))
        
    def OnInit(self):
        # create frame here
        self.frame = MainFrame(self, self.cvfig)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        self.frame.Layout()
        return True
