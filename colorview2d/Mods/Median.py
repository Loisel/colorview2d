import numpy as np
from Mods import IMod

from Mods.ModWidget import ModWidget

import wx
from wx.lib.masked import NumCtrl,EVT_NUM

from scipy.ndimage.filters import median_filter

class MedianWidget(ModWidget):
    def __init__(self,mod,panel):
        ModWidget.__init__(self,mod,panel)
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
        self.num_median_xwidth.SetValue(self.mod.args[0])
        self.num_median_ywidth.SetValue(self.mod.args[1])

    def on_num_median(self,event):
        if self.mod.active:
            self.mod.deactivate()
            self.mod.set_args((self.num_median_xwidth.GetValue(),self.num_median_ywidth.GetValue()))
            self.mod.activate()            
            


class Median(IMod.IMod):
    def __init__(self):
        IMod.IMod.__init__(self)
        self.args = (0.,0.)

    def apply(self):
        datafile = self.view.datafile
        datafile.set_Zdata(median_filter(datafile.Zdata,size=self.args))
        
    def create_widget(self,panel):
        self.panel = panel
        self.widget = MedianWidget(self,self.panel)
        return self.widget
