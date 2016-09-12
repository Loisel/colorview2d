from colorview2d import imod
from colorview2d import modwidget
from colorview2d import floatspin #FloatSpin,EVT_FLOATSPIN
from colorview2d import view

import numpy as np

import wx



"""
Crop
~~~~

A mod to crop the datafile. The widget provides four FloatSpin controls
to specify the window (xleft, xright, ybottom, ytop).
A button can be used to specify set the original size in the controls.

"""

class CropWidget(modwidget.ModWidget):
    """
    The widget hosting the FloatSpin controls and the labels 
    as well as the "Auto" update button.

    :ivar xrange_left_spin: A :class:`FloatSpin` object to contain the x value on the left.
    :ivar xrange_right_spin: A :class:`FloatSpin` object to contain the x value on the right.
    :ivar xrange_bottom_spin: A :class:`FloatSpin` object to contain the x value on the bottom.
    :ivar xrange_top_spin: A :class:`FloatSpin` object to contain the x value on the top.
    :ivar full_range_button: A :class:`wx.Button` to set the ranges of the full plot.
    """
    def __init__(self,mod,panel):
        modwidget.ModWidget.__init__(self,mod,panel)

        self.widgetlist = []
        self.xrangebox_label = wx.StaticText(self.panel, wx.ID_ANY,
            "x-axis left/right: ")
        self.widgetlist.append(self.xrangebox_label)
        self.xrange_left_spin = floatspin.FloatSpin(self.panel, name='x_left',
            digits = 3
            )
        self.xrange_left_spin.SetFormat("%e")
        self.widgetlist.append(self.xrange_left_spin)
        self.xrange_right_spin = floatspin.FloatSpin(self.panel, name='x_right',
            digits = 3
            )
        self.xrange_right_spin.SetFormat("%e")
        self.widgetlist.append(self.xrange_right_spin)

        self.yrangebox_label = wx.StaticText(self.panel, wx.ID_ANY,
            "y-axis bottom/top: ")
        self.widgetlist.append(self.yrangebox_label)
        self.yrange_bottom_spin = floatspin.FloatSpin(self.panel, name='y_bottom',
            digits = 3
            )
        self.yrange_bottom_spin.SetFormat("%e")
        self.widgetlist.append(self.yrange_bottom_spin)
        self.yrange_top_spin = floatspin.FloatSpin(self.panel, name='y_top',
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
        """
        Handles event fired when the checkbox is clicked.
        The values in the :class:`FloatSpin` controls are transfered to the mod.
        The mod is activated.

        :param event: The :class:`wx.EVT_CHECKBOX` event.
        """
        if self.chk.GetValue():
            self.mod.args((self.xrange_left_spin.GetValue(),self.xrange_right_spin.GetValue(),self.yrange_bottom_spin.GetValue(),self.yrange_top_spin.GetValue()))
            self.add_mod()
        else:
            self.remove_mod()

    def update(self):
        """
        Updates the widget with the arguments of the mod.
        The super class' update is called. 
        """
        modwidget.ModWidget.update(self)
        self.xrange_left_spin.SetValue(self.mod.args[0])
        self.xrange_right_spin.SetValue(self.mod.args[1])
        self.yrange_bottom_spin.SetValue(self.mod.args[2])
        self.yrange_top_spin.SetValue(self.mod.args[3])
        
    def on_num_median(self,event):
        """
        Handles changes to the :class:`FloaSpin` controls.

        :param event: The event that this method is bound to.
        :type event: :class:`EVT_FLOATSPIN`
        """
        if self.mod.active:
            self.remove_mod()
            self.mod.args((self.num_median_xwidth.GetValue(),self.num_median_ywidth.GetValue()))
            self.add_mod()            

    def on_full_range_button(self,event):
        """
        Handles clicks on the full_range_button.
        Uses the global state object :class:`view.State` to set the correct bounds.

        :param event: The event
        :type event: :class:`wx.EVT_BUTTON`
        """
        self.xrange_left_spin.SetValue(view.State.datafile.Xleft)
        self.xrange_right_spin.SetValue(view.State.datafile.Xright)
        self.yrange_bottom_spin.SetValue(view.State.datafile.Ybottom)
        self.yrange_top_spin.SetValue(view.State.datafile.Ytop)
            

class Crop(imod.IMod):
    """
    The mod class. The apply routine contains the logic for cropping
    the datafile array to the new size
    
    :ivar args: A 4-tuple containing the corners of the cropped region.
    """
    def __init__(self):
        imod.IMod.__init__(self)
        self.default_args = (0., 0., 0., 0.)

    def do_apply(self, datafile, modargs):
        """
        To apply the mod we use the builtin crop routine of the datafile,
        a :class:`gpfile`.

        :param datafile gpfile: The datafile.
        """
        datafile.crop(modargs[0], modargs[1], modargs[2], modargs[3])
        
    def create_widget(self,panel):
        """
        The widget is created and returned.

        :param panel wx.Panel: The panel the widget is created on.
        :returns: The widget.
        :rtype: :class:`CropWidget`
        """
        self.panel = panel
        self.widget = CropWidget(self,self.panel)
        return self.widget
