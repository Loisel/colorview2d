import wx
from floatspin import FloatSpin,EVT_FLOATSPIN
import toolbox as tb

class CropFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent, title="Crop x/y axes")
        self.parent = parent
        self.CropPanel = CropPanel(self)
        self.Layout()

class CropPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent = parent

        self.widgetlist = []
        datafile = self.parent.parent.view.datafile
        #datafile.report()

        self.xrangebox_label = wx.StaticText(self, wx.ID_ANY,
            "x-axis left/right: ")
        self.widgetlist.append(self.xrangebox_label)
        self.xrange_left_spin = FloatSpin(self, name='x_left',
            value=datafile.Xleft,
            min_val=datafile.Xmin,
            max_val=datafile.Xmax,
            increment = datafile.dX,
            digits = 3
            )
        self.xrange_left_spin.SetFormat("%e")
        self.widgetlist.append(self.xrange_left_spin)
        self.xrange_right_spin = FloatSpin(self, name='x_right',
            value=datafile.Xright,
            min_val=datafile.Xmin,
            max_val=datafile.Xmax,
            increment = datafile.dX,
            digits = 3
            )
        self.xrange_right_spin.SetFormat("%e")
        self.widgetlist.append(self.xrange_right_spin)

        self.yrangebox_label = wx.StaticText(self, wx.ID_ANY,
            "y-axis bottom/top: ")
        self.widgetlist.append(self.yrangebox_label)
        self.yrange_bottom_spin = FloatSpin(self, name='y_bottom',
            value=datafile.Ybottom,
            min_val=datafile.Ymin,
            max_val=datafile.Ymax,
            increment = datafile.dY,
            digits = 3
            )
        self.yrange_bottom_spin.SetFormat("%e")
        self.widgetlist.append(self.yrange_bottom_spin)
        self.yrange_top_spin = FloatSpin(self, name='y_top',
            value=datafile.Ytop,
            min_val=datafile.Ymin,
            max_val=datafile.Ymax,
            increment = datafile.dY,
            digits = 3
            )
        self.yrange_top_spin.SetFormat("%e")
        self.widgetlist.append(self.yrange_top_spin)

        self.Revert = wx.Button(self,wx.ID_ANY, label = "Revert")
        self.Apply = wx.Button(self,wx.ID_ANY,label = "Apply")
        self.Close = wx.Button(self,wx.ID_ANY,label = "Close")

        self.Bind(wx.EVT_BUTTON,self.on_revert,self.Revert)
        self.Bind(wx.EVT_BUTTON,self.on_apply,self.Apply)
        self.Bind(wx.EVT_BUTTON,self.on_close,self.Close)

        self.mainbox = wx.BoxSizer(wx.VERTICAL)

        self.RangeBox = wx.StaticBox(self, wx.ID_ANY, 'Ranges:')
        self.RangeBoxSizer = wx.StaticBoxSizer(self.RangeBox, wx.VERTICAL)

        self.RangeGridSizer = wx.GridSizer(rows=2, cols=3, hgap=5, vgap=10)
        self.RangeBoxSizer.Add(self.RangeGridSizer)

        gridflags = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL

        for widget in self.widgetlist:
            self.RangeGridSizer.Add(widget,0,flag=gridflags)

        self.mainbox.Add(self.RangeBoxSizer)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.Revert,0,flag=wx.ALIGN_CENTER|wx.ALL,border=10)
        self.hbox.Add(self.Apply,0,flag=wx.ALIGN_CENTER|wx.ALL,border=10)
        self.hbox.Add(self.Close,0,flag=wx.ALIGN_CENTER|wx.ALL,border=10)

        self.mainbox.AddSpacer(10,1)
        self.mainbox.Add(self.hbox)

        self.SetSizerAndFit(self.mainbox)
        self.mainbox.Fit(self.parent)

    def on_apply(self,event):
        xleft = self.xrange_left_spin.GetValue()
        xright = self.xrange_right_spin.GetValue()
        ytop = self.yrange_top_spin.GetValue()
        ybottom = self.yrange_bottom_spin.GetValue()


        self.parent.parent.view.remMod("crop")
        self.parent.parent.view.addMod(tb.crop(xleft,xright,ybottom,ytop))

    def on_revert(self,event):
        self.parent.parent.view.remMod("crop")

    def on_close(self,event):
        self.parent.Destroy()
