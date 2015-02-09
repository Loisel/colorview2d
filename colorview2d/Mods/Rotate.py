from colorview2d.Mods import IMod
from colorview2d.Mods.ModWidget import ModWidget

import numpy as np
import wx


"""
This mod performs a 90 deg clockwise or anti-clockwise rotation of the datafile.
"""
class RotateWidget(ModWidget):
    """
    A widget to control the Rotate mod.
    Hosts two radio buttons to choose between clockwise and anti-clockwise rotation.
    """
    def __init__(self,mod,panel):
        ModWidget.__init__(self,mod,panel)

        self.radio_cw = wx.RadioButton(self.panel,wx.ID_ANY,'cw', style=wx.RB_GROUP)
        self.radio_ccw = wx.RadioButton(self.panel, wx.ID_ANY,'ccw')

        self.radio_cw.SetValue(self.mod.args)

        self.Add(self.radio_cw,0,self.flags,border=10)
        self.Add(self.radio_ccw,0,self.flags,border=10)

        self.panel.Bind(wx.EVT_RADIOBUTTON,self.on_radio,self.radio_cw)
        self.panel.Bind(wx.EVT_RADIOBUTTON,self.on_radio,self.radio_ccw)


    def on_chk(self,event):
        if self.chk.GetValue():
            if self.radio_cw.GetValue():
                self.mod.set_args(True)
            else:
                self.mod.set_args(False)
            self.mod.activate()
        else:
            self.mod.deactivate()

    def update(self):
        ModWidget.update(self)
        if self.mod.args:
            self.radio_cw.SetValue(True)
        else:
            self.radio_ccw.SetValue(True)

    def on_radio(self,event):
        if self.mod.active:
            self.mod.deactivate()
            self.mod.set_args(self.radio_cw.GetValue())
            self.mod.activate()            
            


class Rotate(IMod.IMod):
    """
    The mod class to apply the rotation.
    """

    def __init__(self):
        IMod.IMod.__init__(self)
        self.args = True
        
    def apply(self,datafile):
        if self.args:
            datafile.rotate_cw()
        else:
            datafile.rotate_ccw()

    def create_widget(self,panel):
        self.panel = panel
        self.widget = RotateWidget(self,self.panel)
        return self.widget
