import numpy as np
from Mods import IMod

from Mods.ModWidget import ModWidget

from wx.lib.masked import NumCtrl,EVT_NUM

from scipy.ndimage.filters import gaussian_filter

"""
This mod performs a gaussian filter on the data. The window size for the
filter is specified by wx.lib.masked.NumCtrl widgets.

SmoothWidget(ModWidget): 
    A widget to control the filter.

Smooth(IMod):
    The modification class. Covolutes the datafile array with a window of size
    
    args = (xsize, ysize)
"""

class SmoothWidget(ModWidget):
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
        self.num_smooth_xwidth.SetValue(self.mod.args[0])
        self.num_smooth_ywidth.SetValue(self.mod.args[1])
        


class Smooth(IMod.IMod):
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

