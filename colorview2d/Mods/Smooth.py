from colorview2d.Mods import IMod
from colorview2d.Mods.ModWidget import ModWidget

import numpy as np

from wx.lib.masked import NumCtrl,EVT_NUM

from scipy.ndimage.filters import gaussian_filter

"""
This mod performs a gaussian filter on the data. The window size for the
filter is specified by wx.lib.masked.NumCtrl widgets.
"""

class SmoothWidget(ModWidget):
    """
    A widget to control the filter.
    Hosts two wx.lib.masked.NumCtrl widgets to specify the size of the
    filter window.
    """
    def __init__(self,mod,panel):
        ModWidget.__init__(self,mod,panel)
        self.num_smooth_xwidth = NumCtrl(self.panel,
                                          fractionWidth = 1,
                                          allowNegative = False)
        self.num_smooth_ywidth = NumCtrl(self.panel,
                                          fractionWidth = 1,
                                          allowNegative = False)

        self.Add(self.num_smooth_xwidth,0,self.flags,border=10)
        self.Add(self.num_smooth_ywidth,0,self.flags,border=10)

        self.panel.Bind(EVT_NUM,self.on_num_smooth,self.num_smooth_ywidth)
        self.panel.Bind(EVT_NUM,self.on_num_smooth,self.num_smooth_xwidth)


    def on_chk(self,event):
        if self.chk.GetValue():
            self.mod.set_args((self.num_smooth_xwidth.GetValue(),self.num_smooth_ywidth.GetValue()))
            self.mod.activate()
        else:
            self.mod.deactivate()

    def on_num_smooth(self,event):
        if self.mod.active:
            self.mod.deactivate()
            self.mod.set_args((self.num_smooth_xwidth.GetValue(),self.num_smooth_ywidth.GetValue()))
            self.mod.activate()            

    def update(self):
        ModWidget.update(self)
        # Note that we call ChangeValue instead of SetValue to not trigger a
        # EVT_NUM event
        self.num_smooth_xwidth.ChangeValue(self.mod.args[0])
        self.num_smooth_ywidth.ChangeValue(self.mod.args[1])
        


class Smooth(IMod.IMod):
    """
    The modification class. Convolutes a gaussian window of size
    
    args = (xsize, ysize)

    with the datafile array.
    """
    def __init__(self):
        IMod.IMod.__init__(self)
        self.args = (0.,0.)

    def apply(self):
        datafile = self.view.datafile
        datafile.set_Zdata(gaussian_filter(datafile.Zdata,self.args))
        
    def create_widget(self,panel):
        self.panel = panel
        self.widget = SmoothWidget(self,self.panel)
        return self.widget

