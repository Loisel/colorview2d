import wx

class LabelticksFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent, title="Axes and tick labels")
        self.parent = parent
        panel = LabelticksPanel(self)
        self.Layout()

class LabelticksPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent = parent

        self.widgetlist = []

        self.xtextbox_label = wx.StaticText(self, wx.ID_ANY,
            "x-axis label: ")
        self.widgetlist.append(self.xtextbox_label)
        self.xtextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.xtextbox.SetValue(self.parent.parent.Xlabel)
        self.widgetlist.append(self.xtextbox)

        self.xformattextbox_label = wx.StaticText(self, wx.ID_ANY,
            "format: ")
        self.widgetlist.append(self.xformattextbox_label)
        self.xformattextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.xformattextbox.SetValue('auto')
        self.widgetlist.append(self.xformattextbox)


        self.ytextbox_label = wx.StaticText(self, wx.ID_ANY,
            "y-axis label: ")
        self.widgetlist.append(self.ytextbox_label)
        self.ytextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.ytextbox.SetValue(self.parent.parent.Ylabel)
        self.widgetlist.append(self.ytextbox)

        self.yformattextbox_label = wx.StaticText(self, wx.ID_ANY,
            "format: ")
        self.widgetlist.append(self.yformattextbox_label)
        self.yformattextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.yformattextbox.SetValue('auto')
        self.widgetlist.append(self.yformattextbox)


        self.cbtextbox_label = wx.StaticText(self, wx.ID_ANY,
            "cb-axis label: ")
        self.widgetlist.append(self.cbtextbox_label)
        self.cbtextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.cbtextbox.SetValue(self.parent.parent.Cblabel)

        self.widgetlist.append(self.cbtextbox)

        self.cbformattextbox_label = wx.StaticText(self, wx.ID_ANY,
            "format: ")
        self.widgetlist.append(self.cbformattextbox_label)
        self.cbformattextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.cbformattextbox.SetValue('auto')
        self.widgetlist.append(self.cbformattextbox)


        self.Cancel = wx.Button(self,wx.ID_ANY, label = "Cancel")
        self.Apply = wx.Button(self,wx.ID_ANY,label = "Apply")

        self.Bind(wx.EVT_BUTTON,self.on_cancel,self.Cancel)
        self.Bind(wx.EVT_BUTTON,self.on_apply,self.Apply)

        self.mainbox = wx.BoxSizer(wx.VERTICAL)
        self.gridbox = wx.GridSizer(3,2,5,5)

        for widget in self.widgetlist:
            self.gridbox.Add(widget,0,wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER, border=10)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.Apply,0,wx.ALL|wx.ALIGN_CENTER,border=10)
        self.hbox.Add(self.Cancel,0,wx.ALL|wx.ALIGN_CENTER,border=10)

        self.mainbox.Add(self.gridbox,0)
        self.mainbox.Add(self.hbox,0,wx.EXPAND)

        self.SetSizerAndFit(self.mainbox)
        self.mainbox.Fit(self.parent)

    def on_apply(self,event):
        self.parent.parent.Xlabel = self.xtextbox.GetValue()
        self.parent.parent.Ylabel = self.ytextbox.GetValue()
        self.parent.parent.Cblabel = self.cbtextbox.GetValue()

        self.parent.parent.Xtickformat = self.xformattextbox.GetValue()
        self.parent.parent.Ytickformat = self.yformattextbox.GetValue()
        self.parent.parent.Cbtickformat = self.cbformattextbox.GetValue()

        self.parent.parent.PlotFrame.PlotPanel.set_labelticks()
        self.parent.parent.MainPanel.update(self)

    def on_cancel(self,event):
        self.parent.Hide()
