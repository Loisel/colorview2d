from colorview2d import imod
from colorview2d import modwidget

import logging

from wx.lib.masked import NumCtrl, EVT_NUM

from scipy.ndimage.filters import gaussian_filter

"""
This mod performs a gaussian filter on the data. The window size for the
filter is specified by wx.lib.masked.NumCtrl widgets.
"""

class SmoothWidget(modwidget.ModWidget):
    """
    A widget to control the filter.
    Hosts two wx.lib.masked.NumCtrl widgets to specify the size of the
    filter window.
    """
    def __init__(self, mod, panel):
        modwidget.ModWidget.__init__(self,mod,panel)
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
            self.mod.args = (self.num_smooth_xwidth.GetValue(), self.num_smooth_ywidth.GetValue())
            self.add_mod()
        else:
            self.remove_mod()

    def on_num_smooth(self,event):
        if self.chk.GetValue():
            self.remove_mod()
            self.mod.args = (self.num_smooth_xwidth.GetValue(),self.num_smooth_ywidth.GetValue())
            self.add_mod()            

    def update(self):
        modwidget.ModWidget.update(self)
        # Note that we call ChangeValue instead of SetValue to not trigger a
        # EVT_NUM event

        self.num_smooth_xwidth.ChangeValue(self.mod.args[0])
        self.num_smooth_ywidth.ChangeValue(self.mod.args[1])
        


class Smooth(imod.IMod):
    """
    The modification class. Convolutes a gaussian window of size
    
    args = (xsize, ysize)

    with the datafile array.
    """
    def __init__(self):
        imod.IMod.__init__(self)
        self.default_args = (0., 0.)

    def do_apply(self, datafile, args):
        datafile.zdata = gaussian_filter(datafile.zdata, args)
        
    def create_widget(self,panel):
        self.panel = panel
        self.widget = SmoothWidget(self,self.panel)
        return self.widget




