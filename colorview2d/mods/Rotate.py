from colorview2d import imod
from colorview2d import modwidget

import numpy as np
import wx


"""
This mod performs a 90 deg clockwise or anti-clockwise rotation of the datafile.
"""
class RotateWidget(modwidget.ModWidget):
    """
    A widget to control the Rotate mod.
    Hosts two radio buttons to choose between clockwise and anti-clockwise rotation.
    """
    def __init__(self,mod,panel):
        modwidget.ModWidget.__init__(self,mod,panel)

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
                self.mod.args(True)
            else:
                self.mod.args(False)
            self.add_mod()
        else:
            self.remove_mod()

    def update(self):
        modwidget.ModWidget.update(self)
        if self.mod.args:
            self.radio_cw.SetValue(True)
        else:
            self.radio_ccw.SetValue(True)

    def on_radio(self,event):
        if self.mod.active:
            self.remove_mod()
            self.mod.args(self.radio_cw.GetValue())
            self.add_mod()            
            


class Rotate(imod.IMod):
    """
    The mod class to apply the rotation.
    """

    def __init__(self):
        imod.IMod.__init__(self)
        self.args = self.default_args = True
        
    def do_apply(self, datafile, modargs):
        if modargs:
            datafile.rotate_cw()
        else:
            datafile.rotate_ccw()

    def create_widget(self,panel):
        self.panel = panel
        self.widget = RotateWidget(self,self.panel)
        return self.widget
