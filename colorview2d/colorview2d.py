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
import Utils
import yaml
import warnings

from MainFrame import MainFrame


class Colorview2d(wx.App):
    def __init__(self, redirect = False, filename = None, datafilename = None, columns = None):
        self.datafilename = datafilename
        self.columns = columns
        self.default_config = Utils.resource_path('default.config')

        with open(self.default_config) as file:
            self.config = yaml.load(file)

        if self.config['Font'] == 'default':
            for font in plt.rcParams['font.sans-serif']:
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    findfont(FontProperties(family=font))
                    if len(w):
                        continue
                    else:
                        self.config['Font'] = font
                        break

        if self.datafilename:
            self.config['datafilename'] = self.datafilename
            if self.columns:
                self.config['datafilecolumns'] = self.columns

        self.config['datafilecolumns'] = Utils.read_columns(self.config['datafilecolumns'])

        wx.App.__init__(self, redirect, filename)
            
    def OnInit(self):
        # create frame here
        self.frame = MainFrame(self,self.config)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        self.frame.Layout()
        return True
    


