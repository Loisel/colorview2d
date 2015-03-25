import wx
import os

import numpy as np
import wx.lib.mixins.listctrl as listmix
from floatspin import FloatSpin,EVT_FLOATSPIN

from utils import DistanceLine

import signal
from pydispatch import dispatcher

import view

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

class DistanceFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent, title="Linear slope extraction",size=(400,320))
        self.parent = parent
        self.DistancePanel = DistancePanel(self)
        self.Layout()
        self.Bind(wx.EVT_SHOW,self.DistancePanel.on_show)


class DistancePanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)

        self.parent = parent

        self.plotpanel = self.parent.parent.PlotFrame.PlotPanel

        self.linelist = []
        self.lineindex = -1

        # the line spin-control widgets

        self.create_pointwidgets()

        # the line list widget

        self.linelistbox = VariableListCtrl(self,wx.ID_ANY,size=(140,180), style = wx.LC_REPORT|wx.BORDER_SUNKEN)

        self.linelistbox.InsertColumn(0,'dx',width=70)
        self.linelistbox.InsertColumn(1,'dy',width=70)

        self.addlinebutton = wx.Button(self, label="Add Line")
        self.removelinebutton = wx.Button(self, label="Remove last Line")
        self.savelistbutton = wx.Button(self, label="Save List")

        self.Bind(wx.EVT_BUTTON,self.on_addline,self.addlinebutton)
        self.Bind(wx.EVT_BUTTON,self.on_removeline,self.removelinebutton)
        self.Bind(wx.EVT_BUTTON,self.on_savelist,self.savelistbutton)


        # close button

        self.close_button = wx.Button(self,wx.ID_CLOSE, "Close")

        self.Bind(wx.EVT_BUTTON,self.on_close,self.close_button)

        # End of widget definition
        # Formatting ...

        self.mainbox = wx.BoxSizer(wx.HORIZONTAL)

        self.middlevbox = wx.BoxSizer(wx.VERTICAL)

        self.CoordBox = wx.StaticBox(self, wx.ID_ANY, 'Point coordinates')
        self.CoordBoxSizer = wx.StaticBoxSizer(self.CoordBox, wx.VERTICAL)

        self.CoordGridSizer = wx.GridSizer(rows=2, cols=4, vgap=2)

        gridflags = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL

        for widget in self.pointwidgetlist:
            self.CoordGridSizer.Add(widget, 0, flag = gridflags)

        self.CoordBoxSizer.Add(self.CoordGridSizer)

        self.middlevbox.Add(self.CoordBoxSizer, 0)
        self.middlevbox.AddSizer((-1,10))

        self.listhbox = wx.BoxSizer(wx.HORIZONTAL)
        self.listvbox_left = wx.BoxSizer(wx.VERTICAL)
        self.listvbox_right = wx.BoxSizer(wx.VERTICAL)

        self.listvbox_left.Add(self.linelistbox,1,wx.ALL|wx.EXPAND,border=10)

        self.listvbox_right.Add(self.addlinebutton,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,border = 5)
        self.listvbox_right.Add(self.removelinebutton,0,wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        self.listvbox_right.Add(self.savelistbutton,0,wx.ALIGN_CENTER_VERTICAL| wx.ALL, border = 5)
        self.listvbox_right.Add(wx.StaticLine(self, -1))
        self.listvbox_right.Add(self.close_button,flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=5)

        self.listhbox.Add(self.listvbox_left)
        self.listhbox.Add(self.listvbox_right,1,wx.EXPAND)

        self.middlevbox.Add(self.listhbox,1,wx.EXPAND)


        self.mainbox.Add((10,10))
        self.mainbox.Add(self.middlevbox)


        self.SetSizerAndFit(self.mainbox)

        dispatcher.connect(self.handle_new_plot, signal.PLOT_DRAW_ANEW, sender = dispatcher.Any)
        
    def handle_new_plot(self):
        self.linelist = []
        self.lineindex = -1

        self.linelistbox.DeleteAllItems()
        max_xval = view.State.datafile.Xmax
        min_xval = view.State.datafile.Xmin
        max_yval = view.State.datafile.Ymax
        min_yval = view.State.datafile.Ymin
        incr_x = np.absolute(max_xval-min_xval)/1000
        incr_y = np.absolute(max_yval-min_yval)/1000
        self.x1spin.SetRange(min_xval,max_xval)
        self.x1spin.SetIncrement(incr_x)
        self.x2spin.SetRange(min_xval,max_xval)
        self.x2spin.SetIncrement(incr_x)
        self.y1spin.SetRange(min_yval,max_yval)
        self.y1spin.SetIncrement(incr_y)
        self.y2spin.SetRange(min_yval,max_yval)
        self.y1spin.SetIncrement(incr_y)

        

    def create_pointwidgets(self):

        self.pointwidgetlist = []
        
        max_xval = view.State.datafile.Xmax
        min_xval = view.State.datafile.Xmin
        max_yval = view.State.datafile.Ymax
        min_yval = view.State.datafile.Ymin

        incr_x = np.absolute(max_xval-min_xval)/1000
        incr_y = np.absolute(max_yval-min_yval)/1000

        self.x1spin_label = wx.StaticText(self, wx.ID_ANY,
            "x1: ")


        self.pointwidgetlist.append(self.x1spin_label)

        self.x1spin = FloatSpin(self, name='x1',
            value=0,
            min_val=min_xval,
            max_val=max_xval,
            increment = incr_x,
            digits = 3
            )

        self.pointwidgetlist.append(self.x1spin)

        self.x1spin.SetFormat("%e")

        self.y1spin_label = wx.StaticText(self, wx.ID_ANY,
            "y1:")

        self.pointwidgetlist.append(self.y1spin_label)

        self.y1spin = FloatSpin(self, name='y1',
            value=0,
            min_val=min_yval,
            max_val=max_yval,
            increment = incr_y,
            digits = 3)

        self.pointwidgetlist.append(self.y1spin)

        self.y1spin.SetFormat("%e")

        self.x2spin_label = wx.StaticText(self, wx.ID_ANY,
            "x2:")

        self.pointwidgetlist.append(self.x2spin_label)

        self.x2spin = FloatSpin(self, name='x2',
            value=0,
            min_val=min_xval,
            max_val=max_xval,
            increment = incr_x,
            digits = 3
            )

        self.x2spin.SetFormat("%e")

        self.pointwidgetlist.append(self.x2spin)

        self.y2spin_label = wx.StaticText(self, wx.ID_ANY,
            "y2:")

        self.pointwidgetlist.append(self.y2spin_label)

        self.y2spin = FloatSpin(self, name='y2',
            value=0,
            min_val=min_yval,
            max_val=max_yval,
            increment = incr_y,
            digits = 3)

        self.pointwidgetlist.append(self.y2spin)

        self.y2spin.SetFormat("%e")

        self.Bind(EVT_FLOATSPIN, self.on_floatspin)


        
    def on_show(self,event):
        """
        Called on frame show and hide. Used to prepare the line plot panel,
        adjust the axes, prevent the autoscale of the plotpanel and
        connect the mouse click to the on_click routine.

        Attributes:
          event (EVT_SHOW): a hide/show event object
        
        """

        if event.GetShow():

            #import pdb;pdb.set_trace()
            
            dispatcher.send(signal.PLOT_AUTOSCALE_OFF,self)

            self.left = False
            self.right = False

            if self.linelist:
                for line in self.linelist:
                    line.addline(self.plotpanel.axes)
                        
            dispatcher.send(signal.PLOT_UPDATE_CANVAS,self)

            self.press_cid = self.plotpanel.canvas.mpl_connect('button_press_event',self.on_press)
            self.motion_cid = self.plotpanel.canvas.mpl_connect('motion_notify_event',self.on_motion)
            self.release_cid = self.plotpanel.canvas.mpl_connect('button_release_event',self.on_release)
            
        else:
            dispatcher.send(signal.PLOT_AUTOSCALE_ON,self)

            self.press_cid = self.plotpanel.canvas.mpl_disconnect(self.press_cid)
            self.motion_cid = self.plotpanel.canvas.mpl_disconnect(self.motion_cid)
            self.release_cid = self.plotpanel.canvas.mpl_disconnect(self.release_cid)

    def on_addline(self, event):

        self.lineindex += 1

        self.linelist.append(self.currentline)

        self.linelistbox.InsertStringItem(self.lineindex,"{0:.3e}".format(self.linelist[self.lineindex].dx))
        self.linelistbox.SetStringItem(self.lineindex,1,"{0:.3e}".format(self.linelist[self.lineindex].dy))

        delattr(self,'currentline')

        dispatcher.send(signal.PLOT_UPDATE_CANVAS,self)


    def on_removeline(self,event):
        if self.linelist:

            self.linelistbox.DeleteItem(self.lineindex)
            self.lineindex -= 1

            self.linelist.pop().removeline()

            dispatcher.send(signal.PLOT_UPDATE_CANVAS,self)

    def on_savelist(self,event):
        file_choices = "DAT (*.dat)|*.dat"
        datafilename = view.State.config['datafilename']

        dlg = wx.FileDialog(
            self,
            message="Save extracted slopes as...",
            defaultDir=os.getcwd(),
            defaultFile="slopes.dat",
            wildcard=file_choices,
            style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()

            with open(path, 'a') as outfile:
                outfile.write("# Distances extracted from {} \n\
    # dx | dy \n".format(datafilename))
                for line in self.linelist:
                    outfile.write("{}\t{}\n".format(line.dx,line.dy))


    def on_close(self,event):
        if hasattr(self,'currentline'):
            self.currentline.removeline()
            delattr(self,'currentline')

        if self.linelist:
            for line in self.linelist:
                line.removeline()
        #self.linelist = []

        dispatcher.send(signal.PLOT_UPDATE_CANVAS,self)

        self.parent.Hide()

    def on_floatspin(self,event):
        evt_obj = event.GetEventObject()

        if evt_obj.GetName() == "x1":
            self.x1 = evt_obj.GetValue()
        if evt_obj.GetName() == "y1":
            self.y1 = evt_obj.GetValue()
        if evt_obj.GetName() == "x2":
            self.x2 = evt_obj.GetValue()
        if evt_obj.GetName() == "y2":
            self.y2 = evt_obj.GetValue()

        if self.x1 and self.x2:
            self.draw_line()

    def on_press(self,event):
        if event.inaxes!=self.plotpanel.axes: return

        #import pdb;pdb.set_trace()

        self.x1 = event.xdata
        self.x2 = event.xdata
        self.y1 = event.ydata
        self.y2 = event.ydata
        
        if event.button == 1:
            self.left = True
            self.currentline = DistanceLine(self.plotpanel.axes, self.x1, self.x2, self.y1, self.y2, True)
        elif event.button == 3:
            self.right = True
            self.currentline = DistanceLine(self.plotpanel.axes, self.x1, self.x2, self.y1, self.y2, False)
            
    def on_motion(self,event):
        if event.inaxes!=self.plotpanel.axes:
            self.left = False
            self.right = False
            return

        if self.left:
            self.y2 = self.y1
            self.x2 = event.xdata
            self.update_spinctrl()
            self.draw_line()
        if self.right:
            self.x2 = self.x1
            self.y2 = event.ydata
            self.update_spinctrl()
            self.draw_line()


            
    def on_release(self,event):
        if event.inaxes!=self.plotpanel.axes:
            return
        if event.button == 1:
            self.left = False
        if event.button == 3:
            self.right = False
            #import pdb;pdb.set_trace()

        self.currentline.set_distancelabel()
        self.draw_line()

    def draw_line(self):
        if hasattr(self,'currentline'):
            self.currentline.set_data(self.x1,self.x2, self.y1,self.y2)

        #self.currentline.figure.tight_layout()
        #self.currentline.figure.canvas.draw()
        #self.parent.parent.PlotFrame.PlotPanel.fig.tight_layout()
        dispatcher.send(signal.PLOT_UPDATE_CANVAS,self)
        #self.parent.Layout()

    def update_spinctrl(self):
        self.x1spin.SetValue(self.x1)
        self.y1spin.SetValue(self.y1)
        self.x2spin.SetValue(self.x2)
        self.y2spin.SetValue(self.y2)


class VariableListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
