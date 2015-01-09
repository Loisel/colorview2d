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

        self.config = self.parent.parent.config

        self.init_widgetlist_left()
        self.init_widgetlist_right()

        self.Cancel = wx.Button(self,wx.ID_ANY, label = "Cancel")
        self.Apply = wx.Button(self,wx.ID_ANY,label = "Apply")

        self.HeightBoxLabel = wx.StaticText(self, wx.ID_ANY,'Height:')
        self.HeightBox = NumCtrl(self,wx.ID_ANY,
                                 value = 0,
                                 fractionWidth = 1,
                                 allowNegative = False)
        
        self.WidthBoxLabel = wx.StaticText(self, wx.ID_ANY,'Width:')
        self.WidthBox = NumCtrl(self,wx.ID_ANY,
                                value = 0,
                                fractionWidth = 1,
                                allowNegative = False)

        self.DpiBoxLabel = wx.StaticText(self, wx.ID_ANY,'Dpi:')
        self.DpiBox = NumCtrl(self,wx.ID_ANY,
                              value = 100,
                              fractionWidth = 0,
                              allowNegative = False)


        self.Bind(wx.EVT_BUTTON,self.on_cancel,self.Cancel)
        self.Bind(wx.EVT_BUTTON,self.on_apply,self.Apply)

        self.mainbox = wx.BoxSizer(wx.HORIZONTAL)
        self.leftbox = wx.BoxSizer(wx.VERTICAL)
        self.rightbox = wx.BoxSizer(wx.VERTICAL)

        self.LabelFormatBox = wx.StaticBox(self, wx.ID_ANY, 'Labels')
        self.LabelFormatBoxSizer = wx.StaticBoxSizer(self.LabelFormatBox, wx.VERTICAL)

        self.PlotBox = wx.StaticBox(self, wx.ID_ANY, 'Plotsize')
        self.PlotBoxSizer = wx.StaticBoxSizer(self.PlotBox, wx.HORIZONTAL)

        self.PlotBoxSizer.Add(self.WidthBoxLabel,0,wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, border=10)
        self.PlotBoxSizer.Add(self.WidthBox,0,wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, border=10)
        self.PlotBoxSizer.Add(self.HeightBoxLabel,0,wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, border=10)
        self.PlotBoxSizer.Add(self.HeightBox,0,wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, border=10)
        self.PlotBoxSizer.Add(self.DpiBoxLabel,0,wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, border=10)
        self.PlotBoxSizer.Add(self.DpiBox,0,wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, border=10)
        
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
        self.rightbox.Add(self.PlotBoxSizer,0)
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
        fontliststrings = [fm.FontProperties(fname=fname).get_name() for fname in fontlist]
        # remove duplicates
        fontliststrings = list(set(fontliststrings))
        fontliststrings.sort()
        
        # print fontliststrings
        
        self.fontselect = wx.ComboBox(self,
                                      size=wx.DefaultSize,
                                      choices=fontliststrings,
                                      style=wx.CB_READONLY)

        self.fontselect.SetStringSelection(self.config['Font'])
        
        self.widgetlist_right.append(self.fontselect)

        self.fontsizebox_label = wx.StaticText(self, wx.ID_ANY,
            "Font size: ")
        self.widgetlist_right.append(self.fontsizebox_label)
        self.fontsizebox = NumCtrl(self,wx.ID_ANY,
                                   fractionWidth = 0,
                                   allowNegative = False)
        
        self.fontsizebox.SetValue(self.config['Fontsize'])
        self.widgetlist_right.append(self.fontsizebox)

        self.xticksizebox_label = wx.StaticText(self, wx.ID_ANY,
            "Ticksize x: ")
        self.widgetlist_right.append(self.xticksizebox_label)
        self.xticksizebox = NumCtrl(self,wx.ID_ANY,
                                    fractionWidth = 1,
                                    allowNegative = False)

        self.xticksizebox.SetValue(self.config['Xticklength'])
        self.widgetlist_right.append(self.xticksizebox)

        self.yticksizebox_label = wx.StaticText(self, wx.ID_ANY,
            "Ticksize y: ")
        self.widgetlist_right.append(self.yticksizebox_label)
        self.yticksizebox = NumCtrl(self,wx.ID_ANY,
                                    fractionWidth = 1,
                                    allowNegative = False)

        self.yticksizebox.SetValue(self.config['Yticklength'])
        self.widgetlist_right.append(self.yticksizebox)

        self.linewidthbox_label = wx.StaticText(self, wx.ID_ANY,
            "Linewidth: ")
        self.widgetlist_right.append(self.linewidthbox_label)
        self.linewidthbox = NumCtrl(self,wx.ID_ANY,
                                    fractionWidth = 1,
                                    allowNegative = False)

        self.linewidthbox.SetValue(self.config['Linewidth'])
        self.widgetlist_right.append(self.linewidthbox)



    
    def init_widgetlist_left(self):
        self.widgetlist_left = []

        self.xtextbox_label = wx.StaticText(self, wx.ID_ANY,
            "x-axis label: ")
        self.widgetlist_left.append(self.xtextbox_label)
        self.xtextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.xtextbox.SetValue(self.config['Xlabel'])
        self.widgetlist_left.append(self.xtextbox)

        self.xformattextbox_label = wx.StaticText(self, wx.ID_ANY,
            "format: ")
        self.widgetlist_left.append(self.xformattextbox_label)
        self.xformattextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.xformattextbox.SetValue(self.config['Xtickformat'])
        self.widgetlist_left.append(self.xformattextbox)


        self.ytextbox_label = wx.StaticText(self, wx.ID_ANY,
            "y-axis label: ")
        self.widgetlist_left.append(self.ytextbox_label)
        self.ytextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.ytextbox.SetValue(self.config['Ylabel'])
        self.widgetlist_left.append(self.ytextbox)

        self.yformattextbox_label = wx.StaticText(self, wx.ID_ANY,
            "format: ")
        self.widgetlist_left.append(self.yformattextbox_label)
        self.yformattextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.yformattextbox.SetValue(self.config['Ytickformat'])
        self.widgetlist_left.append(self.yformattextbox)


        self.cbtextbox_label = wx.StaticText(self, wx.ID_ANY,
            "cb-axis label: ")
        self.widgetlist_left.append(self.cbtextbox_label)
        self.cbtextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.cbtextbox.SetValue(self.config['Cblabel'])

        self.widgetlist_left.append(self.cbtextbox)

        self.cbformattextbox_label = wx.StaticText(self, wx.ID_ANY,
            "format: ")
        self.widgetlist_left.append(self.cbformattextbox_label)
        self.cbformattextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.cbformattextbox.SetValue(self.config['Cbtickformat'])
        self.widgetlist_left.append(self.cbformattextbox)

    def on_apply(self,event):
        self.config['Xlabel'] = self.xtextbox.GetValue()
        self.config['Xtickformat'] = self.xformattextbox.GetValue()
        self.config['Ylabel'] = self.ytextbox.GetValue()
        self.config['Ytickformat'] = self.yformattextbox.GetValue()
        self.config['Cblabel'] = self.cbtextbox.GetValue()
        self.config['Cbtickformat'] = self.cbformattextbox.GetValue()
        self.config['Font'] = self.fontselect.GetStringSelection()
        self.config['Fontsize'] = self.fontsizebox.GetValue()
        self.config['Xticklength'] = self.xticksizebox.GetValue()
        self.config['Yticklength'] = self.yticksizebox.GetValue()
        self.config['Linewidth'] = self.linewidthbox.GetValue()
        self.config['Width'] = self.WidthBox.GetValue()
        self.config['Height'] = self.HeightBox.GetValue()
        self.config['Dpi'] = self.DpiBox.GetValue()
        self.parent.parent.PlotFrame.PlotPanel.draw_plot()

    def on_cancel(self,event):
        self.parent.Hide()
