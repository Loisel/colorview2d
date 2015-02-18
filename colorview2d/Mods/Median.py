from colorview2d import IMod
from colorview2d import ModWidget

import numpy as np

from wx.lib.masked import NumCtrl,EVT_NUM

from scipy.ndimage.filters import median_filter

"""
This mod performs a median filter on the data. The window size for the
filter is specified by wx.lib.masked.NumCtrl widgets.
"""


class MedianWidget(ModWidget.ModWidget):
    """
    A widget to control the filter.
    Hosts two wx.lib.masked.NumCtrl widgets to specify the size of the
    filter window.
    """
    def __init__(self,mod,panel):
        ModWidget.ModWidget.__init__(self,mod,panel)
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
            self.mod.set_args((self.num_median_xwidth.GetValue(),self.num_median_ywidth.GetValue()))
            self.mod.activate()
        else:
            self.mod.deactivate()

    def update(self):
        ModWidget.ModWidget.update(self)
        # Note that we call ChangeValue instead of SetValue to not trigger a
        # EVT_NUM event
        self.num_median_xwidth.ChangeValue(self.mod.args[0])
        self.num_median_ywidth.ChangeValue(self.mod.args[1])

    def on_num_median(self,event):
        if self.mod.active:
            self.mod.deactivate()
            self.mod.set_args((self.num_median_xwidth.GetValue(),self.num_median_ywidth.GetValue()))
            self.mod.activate()            
            


class Median(IMod.IMod):
    """
    The modification class. Applies a median filter of size
    
    args = (xsize, ysize)

    to the datafile.
    """
    def __init__(self):
        IMod.IMod.__init__(self)
        self.args = self.default_args = (0.,0.)

    def apply(self,datafile):
        datafile.set_Zdata(median_filter(datafile.Zdata,size=self.args))
        
    def create_widget(self,panel):
        self.panel = panel
        self.widget = MedianWidget(self,self.panel)
        return self.widget
