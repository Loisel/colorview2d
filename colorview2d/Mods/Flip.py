from colorview2d import imod
from colorview2d import modwidget

import numpy as np
import wx


"""
This mod flips the the datafile along x or y direction.
"""
class FlipWidget(modwidget.ModWidget):
    """
    A widget to control the Flip mod.
    Hosts two radio buttons to choose between up/down or right/left flip.
    """
    def __init__(self,mod,panel):
        modwidget.ModWidget.__init__(self,mod,panel)

        self.radio_lr = wx.RadioButton(self.panel,wx.ID_ANY,'left/right', style=wx.RB_GROUP)
        self.radio_ud = wx.RadioButton(self.panel, wx.ID_ANY,'up/down')

        self.radio_lr.SetValue(self.mod.args)

        self.Add(self.radio_lr,0,self.flags,border=10)
        self.Add(self.radio_ud,0,self.flags,border=10)

        self.panel.Bind(wx.EVT_RADIOBUTTON,self.on_radio,self.radio_lr)
        self.panel.Bind(wx.EVT_RADIOBUTTON,self.on_radio,self.radio_ud)


    def on_chk(self,event):
        if self.chk.GetValue():
            if self.radio_lr.GetValue():
                self.mod.args(True)
            else:
                self.mod.args(False)
            self.add_mod()
        else:
            self.remove_mod()

    def update(self):
        modwidget.ModWidget.update(self)
        if self.mod.args:
            self.radio_lr.SetValue(True)
        else:
            self.radio_ud.SetValue(True)

    def on_radio(self,event):
        if self.mod.active:
            self.remove_mod()
            self.mod.args(self.radio_lr.GetValue())
            self.add_mod()            
            


class Flip(imod.IMod):
    """
    The mod class to flip the datafile.
    """

    def __init__(self):
        imod.IMod.__init__(self)
        self.default_args = True
        
    def do_apply(self, datafile, modargs):
        if modargs:
            datafile.flip_lr()
        else:
            datafile.flip_ud()

    def create_widget(self,panel):
        self.panel = panel
        self.widget = FlipWidget(self,self.panel)
        return self.widget
