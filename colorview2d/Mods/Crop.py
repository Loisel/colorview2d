from colorview2d.Mods import IMod
from colorview2d.Mods.ModWidget import ModWidget
from colorview2d.floatspin import FloatSpin,EVT_FLOATSPIN

import numpy as np

import wx



"""
A mod to crop the datafile. The widget provides four FloatSpin controls
to specify the window (xleft, xright, ybottom, ytop).
A button can be used to specify set the original size in the controls.
"""

class CropWidget(ModWidget):
    """
    The widget hosting the FloatSpin controls and the labels 
    as well as the "Auto" update button.
    """
    def __init__(self,mod,panel):
        ModWidget.__init__(self,mod,panel)

        self.widgetlist = []
        self.xrangebox_label = wx.StaticText(self.panel, wx.ID_ANY,
            "x-axis left/right: ")
        self.widgetlist.append(self.xrangebox_label)
        self.xrange_left_spin = FloatSpin(self.panel, name='x_left',
            digits = 3
            )
        self.xrange_left_spin.SetFormat("%e")
        self.widgetlist.append(self.xrange_left_spin)
        self.xrange_right_spin = FloatSpin(self.panel, name='x_right',
            digits = 3
            )
        self.xrange_right_spin.SetFormat("%e")
        self.widgetlist.append(self.xrange_right_spin)

        self.yrangebox_label = wx.StaticText(self.panel, wx.ID_ANY,
            "y-axis bottom/top: ")
        self.widgetlist.append(self.yrangebox_label)
        self.yrange_bottom_spin = FloatSpin(self.panel, name='y_bottom',
            digits = 3
            )
        self.yrange_bottom_spin.SetFormat("%e")
        self.widgetlist.append(self.yrange_bottom_spin)
        self.yrange_top_spin = FloatSpin(self.panel, name='y_top',
            digits = 3
            )
        self.yrange_top_spin.SetFormat("%e")
        self.widgetlist.append(self.yrange_top_spin)

        self.RangeBox = wx.StaticBox(self.panel, wx.ID_ANY, 'Ranges:')
        self.RangeBoxSizer = wx.StaticBoxSizer(self.RangeBox, wx.VERTICAL)

        self.RangeGridSizer = wx.GridSizer(rows=2, cols=3, hgap=5, vgap=10)
        self.RangeBoxSizer.Add(self.RangeGridSizer)

        gridflags = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL

        for widget in self.widgetlist:
            self.RangeGridSizer.Add(widget,0,flag=gridflags)

        self.Add(self.RangeBoxSizer)

        self.full_range_button = wx.Button(self.panel,wx.ID_ANY,'Auto')        

        self.Add(self.full_range_button,0,self.flags,border=10)

        self.panel.Bind(wx.EVT_BUTTON,self.on_full_range_button,self.full_range_button)


    def on_chk(self,event):
        if self.chk.GetValue():
            self.mod.set_args((self.xrange_left_spin.GetValue(),self.xrange_right_spin.GetValue(),self.yrange_bottom_spin.GetValue(),self.yrange_top_spin.GetValue()))
            self.mod.activate()
        else:
            self.mod.deactivate()

    def update(self):
        ModWidget.update(self)
        self.xrange_left_spin.SetValue(self.mod.args[0])
        self.xrange_right_spin.SetValue(self.mod.args[1])
        self.yrange_bottom_spin.SetValue(self.mod.args[2])
        self.yrange_top_spin.SetValue(self.mod.args[3])
        
    def on_num_median(self,event):
        if self.mod.active:
            self.mod.deactivate()
            self.mod.set_args((self.num_median_xwidth.GetValue(),self.num_median_ywidth.GetValue()))
            self.mod.activate()            

    def on_full_range_button(self,event):
        self.xrange_left_spin.SetValue(self.mod.view.datafile.Xleft)
        self.xrange_right_spin.SetValue(self.mod.view.datafile.Xright)
        self.yrange_bottom_spin.SetValue(self.mod.view.datafile.Ybottom)
        self.yrange_top_spin.SetValue(self.mod.view.datafile.Ytop)
            

class Crop(IMod.IMod):
    """
    The mod class. The apply routine contains the logic for cropping
    the datafile array to the new size
    
    args = (xleft, xright, ybottom, ytop).
    """
    def __init__(self):
        IMod.IMod.__init__(self)
        self.args = (0.,0.,0.,0.)

    def apply(self):
        datafile = self.view.datafile

        xleft_idx = datafile.get_xrange_idx(self.args[0])
        xright_idx = datafile.get_xrange_idx(self.args[1])
        ybottom_idx = datafile.get_yrange_idx(self.args[2])
        ytop_idx = datafile.get_yrange_idx(self.args[3])

        #print "left {} right {} bottom {} top {}".format(xleft_idx,xright_idx,ybottom_idx,ytop_idx)
        #datafile.report()

        datafile.set_xyrange(datafile.Xrange[xleft_idx:xright_idx],datafile.Yrange[ybottom_idx:ytop_idx])
        datafile.set_Zdata(datafile.get_region(xleft_idx,xright_idx,ybottom_idx,ytop_idx))

    def create_widget(self,panel):
        self.panel = panel
        self.widget = CropWidget(self,self.panel)
        return self.widget
