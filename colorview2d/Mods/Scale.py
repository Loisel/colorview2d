from colorview2d import imod
from colorview2d import view
from colorview2d import modwidget
from colorview2d import floatvalidator

import numpy as np
import wx

"""
A mod to scale the data. 
A text control with a custom validator is applied so that 
exponential notation can be used.
"""

class ScaleWidget(modwidget.ModWidget):
    """
    The Widget that controls the mod. 
    Hosts a TextCtrl with a custom validator.
    """
    def __init__(self,mod,panel):
        modwidget.ModWidget.__init__(self,mod,panel)
        self.num_scale = wx.TextCtrl(self.panel,-1,"",validator = floatvalidator.FloatValidator('1e0'))
        self.auto_scale_button = wx.Button(self.panel,wx.ID_ANY,'dI/dV')        

        self.Add(self.num_scale,0,self.flags,border=10)
        self.Add(self.auto_scale_button,0,self.flags,border=10)

        self.panel.Bind(wx.EVT_BUTTON,self.on_auto_scale_button,self.auto_scale_button)

    def on_chk(self,event):
        if self.chk.GetValue():
            self.panel.Validate()
            self.mod.args(float(self.num_scale.GetValue()))
            self.add_mod()
        else:
            self.remove_mod()
            
    def on_auto_scale_button(self,event):
        self.num_scale.SetValue(str(2.5812e4/view.State.datafile.dY))        

    def update(self):
        modwidget.ModWidget.update(self)
        self.num_scale.SetValue(str(self.mod.args))

    

class Scale(imod.IMod):
    """
    The mod class to scale the values in the 2d datafile array
    according to the value entered in the widget:

    args (float): The float that is multiplied with the datafile array.
    """
    def __init__(self):
        imod.IMod.__init__(self)
        self.args = self.default_args = 1.

    def do_apply(self, datafile, args):
        datafile.zdata = datafile.zdata * args
        
    def create_widget(self,panel):
        self.panel = panel
        self.widget = ScaleWidget(self,self.panel)
        return self.widget


