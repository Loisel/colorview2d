#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
colorview2d
~~~~~~~~~~~

A GUI driven application to visualize and analyze 3D
datasets. Available tools include linear slope extraction,
linecut series extraction and a linetrace viewer.

:copyright: 2014 by Alois Dirnaichner, see AUTHORS for more details
:license: GPLv3, see LICENSE for more details
"""

from MainFrame import MainFrame

import wx
import logging
from pydispatch import dispatcher



class Colorview2d(wx.App):
    """
    The colorview2d application object.
    It is used to parse the configuration
    and create the first View object.
    """
    
    def __init__(self, redirect = False, cv2dpath = None, filename = None, datafilename = None, columns = None):
        self.datafilename = datafilename
        self.columns = columns
        self.cv2dpath = cv2dpath
        dispatcher.connect(self.handle_print_events)
        wx.App.__init__(self, redirect, filename)

    def handle_print_events(self,sender,signal):
        logging.debug('{} sent signal: {}'.format(sender,signal))
        
    def OnInit(self):
        # create frame here
        self.frame = MainFrame(self,self.cv2dpath,self.datafilename,self.columns)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        self.frame.Layout()
        return True
    


