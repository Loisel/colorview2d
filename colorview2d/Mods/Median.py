from colorview2d import imod
from colorview2d import modwidget

import numpy as np

from wx.lib.masked import NumCtrl,EVT_NUM

from scipy.ndimage.filters import median_filter

"""
This mod performs a median filter on the data. The window size for the
filter is specified by wx.lib.masked.NumCtrl widgets.
"""


class MedianWidget(modwidget.ModWidget):
    """
    A widget to control the filter.
    Hosts two wx.lib.masked.NumCtrl widgets to specify the size of the
    filter window.
    """
    def __init__(self,mod,panel):
        modwidget.ModWidget.__init__(self,mod,panel)
        self.num_median_xwidth = NumCtrl(self.panel,
                                          fractionWidth = 1,
                                          allowNegative = False)
        self.num_median_ywidth = NumCtrl(self.panel,
                                          fractionWidth = 1,
                                          allowNegative = False)

        self.Add(self.num_median_xwidth,0,self.flags,border=10)
        self.Add(self.num_median_ywidth,0,self.flags,border=10)

        self.panel.Bind(EVT_NUM,self.on_num_median,self.num_median_ywidth)
        self.panel.Bind(EVT_NUM,self.on_num_median,self.num_median_xwidth)


    def on_chk(self,event):
        if self.chk.GetValue():
            self.mod.args((self.num_median_xwidth.GetValue(),self.num_median_ywidth.GetValue()))
            self.add_mod()
        else:
            self.remove_mod()

    def update(self):
        modwidget.ModWidget.update(self)
        # Note that we call ChangeValue instead of SetValue to not trigger a
        # EVT_NUM event
        self.num_median_xwidth.ChangeValue(self.mod.args[0])
        self.num_median_ywidth.ChangeValue(self.mod.args[1])

    def on_num_median(self,event):
        if self.mod.active:
            self.remove_mod()
            self.mod.args((self.num_median_xwidth.GetValue(),self.num_median_ywidth.GetValue()))
            self.add_mod()            
            


class Median(imod.IMod):
    """
    The modification class. Applies a median filter of size
    
    args = (xsize, ysize)

    to the datafile.
    """
    def __init__(self):
        imod.IMod.__init__(self)
        self.default_args = (0., 0.)

    def do_apply(self, datafile, modargs):
        datafile.set_Zdata(median_filter(datafile.Zdata, size=modargs))
        
    def create_widget(self,panel):
        self.panel = panel
        self.widget = MedianWidget(self,self.panel)
        return self.widget
