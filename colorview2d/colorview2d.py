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
import logging
from View import View
import gpfile

from MainFrame import MainFrame


class Colorview2d(wx.App):
    """
    The colorview2d application object.
    It is used to parse the configuration
    and create the first View object.
    """
    
    def __init__(self, redirect = False, filename = None, datafilename = None, columns = None):
        self.datafilename = datafilename
        self.columns = columns

        # The name of the default config file is hard coded.
        
        self.default_config = Utils.resource_path('default.cv2d')

        self.config,self.modlist = self.parse_config()

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
                self.config['datafilecolumns'] = Utils.read_columns(self.columns)


        data_file = Utils.resource_path(self.config['datafilename'])

        self.view = View(gpfile.gpfile(data_file,self.config['datafilecolumns']))

        wx.App.__init__(self, redirect, filename)

    def parse_config(self):
        """
        Load the configuration and the modlist from the config file
        specified in the YAML format.

        Returns:
          config (dict): A configuration dict.
          modlist (list): A list of modification objects from the toolbox
                          module
        """
        import toolbox
        
        with open(self.default_config) as file:
            doclist = yaml.load_all(file)
            config = doclist.next()
            modlist = [mod for mod in doclist]
            logging.info('Modlist found: {}'.format(modlist))

            return config,modlist
        
    def OnInit(self):
        # create frame here
        self.frame = MainFrame(self,self.config,self.view)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        self.frame.Layout()
        return True
    


