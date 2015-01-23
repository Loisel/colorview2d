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
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties,findfont

import wx

from MainFrame import MainFrame


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
        wx.App.__init__(self, redirect, filename)

        
    def OnInit(self):
        # create frame here
        self.frame = MainFrame(self,self.cv2dpath,self.datafilename,self.columns)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        self.frame.Layout()
        return True
    


