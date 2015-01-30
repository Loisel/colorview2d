from Mods.ModWidget import ModWidget
from FloatValidator import FloatValidator
import wx

class ScaleWidget(ModWidget):
    def __init__(self,mod,panel):
        ModWidget.__init__(self,mod,panel)
        self.num_scale = wx.TextCtrl(self.panel,-1,"",validator = FloatValidator('1e0'))
        self.auto_scale_button = wx.Button(self.panel,wx.ID_ANY,'dI/dV')        

        self.Add(self.num_scale,0,self.flags,border=10)
        self.Add(self.auto_scale_button,0,self.flags,border=10)

        self.panel.Bind(wx.EVT_BUTTON,self.on_auto_scale_button,self.auto_scale_button)

    def on_chk(self,event):
        ModWidget.on_chk(self,event)
        self.Validate()

    def on_auto_scale_button(self,event):
        self.num_scale.SetValue(str(2.5812e4/self.mod.view.datafile.dY))        

        