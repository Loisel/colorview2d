import wx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wx.lib.masked import NumCtrl,EVT_NUM
from FloatValidator import FloatValidator

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

        self.init_widgetlist_left()
        self.init_widgetlist_right()

        self.Cancel = wx.Button(self,wx.ID_ANY, label = "Cancel")
        self.Apply = wx.Button(self,wx.ID_ANY,label = "Apply")

        self.Bind(wx.EVT_BUTTON,self.on_cancel,self.Cancel)
        self.Bind(wx.EVT_BUTTON,self.on_apply,self.Apply)

        self.mainbox = wx.BoxSizer(wx.HORIZONTAL)
        self.leftbox = wx.BoxSizer(wx.VERTICAL)
        self.rightbox = wx.BoxSizer(wx.VERTICAL)

        self.LabelFormatBox = wx.StaticBox(self, wx.ID_ANY, 'Labels')
        self.LabelFormatBoxSizer = wx.StaticBoxSizer(self.LabelFormatBox, wx.VERTICAL)

        self.FontFormatBox = wx.StaticBox(self, wx.ID_ANY, 'Font, ticks and lines')
        self.FontFormatBoxSizer = wx.StaticBoxSizer(self.FontFormatBox, wx.VERTICAL)

        
        
        self.gridbox_left = wx.GridSizer(3,2,5,5)
        self.gridbox_right = wx.GridSizer(3,2,5,5)

        for widget in self.widgetlist_left:
            self.gridbox_left.Add(widget,0,wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, border=10)
        for widget in self.widgetlist_right:
            self.gridbox_right.Add(widget,0,wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, border=10)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.Apply,0,wx.ALL|wx.ALIGN_CENTER,border=10)
        self.hbox.Add(self.Cancel,0,wx.ALL|wx.ALIGN_CENTER,border=10)

        self.LabelFormatBoxSizer.Add(self.gridbox_left,0)
        self.FontFormatBoxSizer.Add(self.gridbox_right,0)

        self.leftbox.Add(self.LabelFormatBoxSizer,0)
        self.rightbox.Add(self.FontFormatBoxSizer,0)
        self.leftbox.Add(self.hbox,0,wx.EXPAND)

        self.mainbox.Add(self.leftbox,0)
        self.mainbox.Add(self.rightbox,0)

        self.SetSizerAndFit(self.mainbox)
        self.mainbox.Fit(self.parent)

    def init_widgetlist_right(self):
        self.widgetlist_right = []

        # get list of available fonts and put it inside the widget
        fontlist = fm.get_fontconfig_fonts()

        self.fontselect_label = wx.StaticText(self, wx.ID_ANY,'Font:')

        self.widgetlist_right.append(self.fontselect_label)

        # Set default font in the widget
        default_font = plt.rcParams['font.sans-serif'][0]
        self.fontselect = wx.ComboBox(self,
                                      value=default_font,
                                      size=wx.DefaultSize,
                                      style=wx.CB_READONLY)

        for fname in fontlist:
            self.fontselect.Append(fm.FontProperties(fname=fname).get_name())

        
        self.widgetlist_right.append(self.fontselect)

        self.fontsizebox_label = wx.StaticText(self, wx.ID_ANY,
            "Font size: ")
        self.widgetlist_right.append(self.fontsizebox_label)
        self.fontsizebox = NumCtrl(self,wx.ID_ANY,
                                   fractionWidth = 0,
                                   allowNegative = False)
        
        self.fontsizebox.SetValue(plt.rcParams['font.size'])
        self.widgetlist_right.append(self.fontsizebox)

        self.xticksizebox_label = wx.StaticText(self, wx.ID_ANY,
            "Ticksize x: ")
        self.widgetlist_right.append(self.xticksizebox_label)
        self.xticksizebox = NumCtrl(self,wx.ID_ANY,
                                    fractionWidth = 1,
                                    allowNegative = False)

        self.xticksizebox.SetValue(plt.rcParams['xtick.major.size'])
        self.widgetlist_right.append(self.xticksizebox)

        self.yticksizebox_label = wx.StaticText(self, wx.ID_ANY,
            "Ticksize y: ")
        self.widgetlist_right.append(self.yticksizebox_label)
        self.yticksizebox = NumCtrl(self,wx.ID_ANY,
                                    fractionWidth = 1,
                                    allowNegative = False)

        self.yticksizebox.SetValue(plt.rcParams['ytick.major.size'])
        self.widgetlist_right.append(self.yticksizebox)

        self.xtickstepbox_label = wx.StaticText(self, wx.ID_ANY,
            "Tick spacing x: ")
        self.widgetlist_right.append(self.xtickstepbox_label)
        self.xtickstepbox = wx.TextCtrl(self,wx.ID_ANY,
                                    name = 'xtickstepbox',
                                    validator = FloatValidator('0e0'))
        self.xtickstepbox.SetValue('0')
        self.widgetlist_right.append(self.xtickstepbox)

        self.ytickstepbox_label = wx.StaticText(self, wx.ID_ANY,
            "Tick spacing y: ")
        self.widgetlist_right.append(self.ytickstepbox_label)
        self.ytickstepbox = wx.TextCtrl(self,wx.ID_ANY,
                                    name = 'ytickstepbox',
                                    validator = FloatValidator('0e0'))
        

        self.ytickstepbox.SetValue('0')
        self.widgetlist_right.append(self.ytickstepbox)

        self.linewidthbox_label = wx.StaticText(self, wx.ID_ANY,
            "Linewidth: ")
        self.widgetlist_right.append(self.linewidthbox_label)
        self.linewidthbox = NumCtrl(self,wx.ID_ANY,
                                    fractionWidth = 1,
                                    allowNegative = False)

        self.linewidthbox.SetValue(plt.rcParams['axes.linewidth'])
        self.widgetlist_right.append(self.linewidthbox)

        self.ytickstepbox.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.xtickstepbox.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)


        
    def OnKillFocus(self,event):
        evt_obj = event.GetEventObject()
        print "Loosing focus, control {}".format(evt_obj.GetName())

        if evt_obj.GetName() in ['xtickstepbox','ytickstepbox']:
            self.Validate()

        event.Skip()

    def init_widgetlist_left(self):
        self.widgetlist_left = []

        self.xtextbox_label = wx.StaticText(self, wx.ID_ANY,
            "x-axis label: ")
        self.widgetlist_left.append(self.xtextbox_label)
        self.xtextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.xtextbox.SetValue(self.parent.parent.Xlabel)
        self.widgetlist_left.append(self.xtextbox)

        self.xformattextbox_label = wx.StaticText(self, wx.ID_ANY,
            "format: ")
        self.widgetlist_left.append(self.xformattextbox_label)
        self.xformattextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.xformattextbox.SetValue('auto')
        self.widgetlist_left.append(self.xformattextbox)


        self.ytextbox_label = wx.StaticText(self, wx.ID_ANY,
            "y-axis label: ")
        self.widgetlist_left.append(self.ytextbox_label)
        self.ytextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.ytextbox.SetValue(self.parent.parent.Ylabel)
        self.widgetlist_left.append(self.ytextbox)

        self.yformattextbox_label = wx.StaticText(self, wx.ID_ANY,
            "format: ")
        self.widgetlist_left.append(self.yformattextbox_label)
        self.yformattextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.yformattextbox.SetValue('auto')
        self.widgetlist_left.append(self.yformattextbox)


        self.cbtextbox_label = wx.StaticText(self, wx.ID_ANY,
            "cb-axis label: ")
        self.widgetlist_left.append(self.cbtextbox_label)
        self.cbtextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.cbtextbox.SetValue(self.parent.parent.Cblabel)

        self.widgetlist_left.append(self.cbtextbox)

        self.cbformattextbox_label = wx.StaticText(self, wx.ID_ANY,
            "format: ")
        self.widgetlist_left.append(self.cbformattextbox_label)
        self.cbformattextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.cbformattextbox.SetValue('auto')
        self.widgetlist_left.append(self.cbformattextbox)

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
