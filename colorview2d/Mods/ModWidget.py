import wx

class ModWidget(wx.BoxSizer):

    flags = wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL


    def __init__(self,mod,panel):
        wx.BoxSizer.__init__(self,wx.HORIZONTAL)
        self.mod = mod
        self.panel = panel
        self.title = self.mod.title
        self.chk = wx.CheckBox(self.panel, wx.ID_ANY, self.title)
        self.Add(self.chk,0,self.flags,border=10)
        self.panel.Bind(wx.EVT_CHECKBOX,self.on_chk,self.chk)

    def update(self):
        pass

    def on_chk(self,event):
        if self.chk.GetValue():
            self.mod.activate()
        else:
            self.mod.deactivate()

    
        