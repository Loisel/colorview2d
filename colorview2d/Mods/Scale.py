from colorview2d import IMod
from colorview2d import View
from colorview2d import ModWidget
from colorview2d import FloatValidator

import numpy as np
import wx

"""
A mod to scale the data. 
A text control with a custom validator is applied so that 
exponential notation can be used.
"""

class ScaleWidget(ModWidget.ModWidget):
    """
    The Widget that controls the mod. 
    Hosts a TextCtrl with a custom validator.
    """
    def __init__(self,mod,panel):
        ModWidget.ModWidget.__init__(self,mod,panel)
        self.num_scale = wx.TextCtrl(self.panel,-1,"",validator = FloatValidator.FloatValidator('1e0'))
        self.auto_scale_button = wx.Button(self.panel,wx.ID_ANY,'dI/dV')        

        self.Add(self.num_scale,0,self.flags,border=10)
        self.Add(self.auto_scale_button,0,self.flags,border=10)

        self.panel.Bind(wx.EVT_BUTTON,self.on_auto_scale_button,self.auto_scale_button)

    def on_chk(self,event):
        if self.chk.GetValue():
            self.panel.Validate()
            self.mod.set_args(float(self.num_scale.GetValue()))
            self.mod.activate()
        else:
            self.mod.deactivate()
            
    def on_auto_scale_button(self,event):
        self.num_scale.SetValue(str(2.5812e4/View.State.datafile.dY))        

    def update(self):
        ModWidget.ModWidget.update(self)
        self.num_scale.SetValue(str(self.mod.args))

    

class Scale(IMod.IMod):
    """
    The mod class to scale the values in the 2d datafile array
    according to the value entered in the widget:

    args (float): The float that is multiplied with the datafile array.
    """
    def __init__(self):
        IMod.IMod.__init__(self)
        self.args = self.default_args = 1.

    def apply(self,datafile):
        datafile.set_Zdata(datafile.Zdata*self.args)

        
    def create_widget(self,panel):
        self.panel = panel
        self.widget = ScaleWidget(self,self.panel)
        return self.widget


