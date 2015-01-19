#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
colorview2d
~~~~~~~~~~~

A GUI driven application to visualize and analyze 3D
datasets. Available tools include linear slope extraction,
linecut series extraction and fitting of (almost) arbitrary 2d
functions to prominent features in the 3d dataset.

:copyright: 2014 by Alois Dirnaichner, see AUTHORS for more details
:license: GPLv3, see LICENSE for more details
"""

import wx
import matplotlib
matplotlib.use('WXAgg')

from MainFrame import MainFrame


class Colorview2d(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
 
    def OnInit(self):
        # create frame here
        self.frame = MainFrame(self)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        self.frame.Layout()
        return True
    


