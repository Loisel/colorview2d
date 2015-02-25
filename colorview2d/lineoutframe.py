import wx

import numpy as np
import matplotlib.pyplot as plt
from utils import Line

from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar

import signal
from pydispatch import dispatcher

import view

class LineoutFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent, title="Line trace tool",size=(800,600))
        self.parent = parent
        self.LineoutPanel = LineoutPanel(self)
        self.Layout()
        self.Bind(wx.EVT_SHOW,self.LineoutPanel.on_show)


class LineoutPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)

        self.parent = parent

        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None

        self.resolution = 6.

        self.linelist = []

        self.fig = plt.figure()

        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        self.canvas = FigCanvas(self, wx.ID_ANY, self.fig)
        self.toolbar = NavigationToolbar(self.canvas)

        self.plotpanel = self.parent.parent.PlotFrame.PlotPanel

        self.mainbox = wx.BoxSizer(wx.VERTICAL)
        self.mainbox.Add(self.toolbar,0)

        self.fig.tight_layout()

        #self.canvas.draw()

        self.mainbox.Add(self.canvas, 1,flag =  wx.EXPAND)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.plotbutton = wx.Button(self, label="Plot")
        self.closebutton = wx.Button(self, label="Close")

        self.Bind(wx.EVT_BUTTON,self.on_close,self.closebutton)
        self.Bind(wx.EVT_BUTTON,self.on_plot,self.plotbutton)

        self.hbox.Add(self.plotbutton,0,wx.ALL|wx.ALIGN_CENTER,border = 10)
        self.hbox.Add(self.closebutton,0,wx.ALL|wx.ALIGN_CENTER,border = 10)

        self.mainbox.Add(self.hbox,0)

        self.SetSizer(self.mainbox)
        self.mainbox.Fit(self)

        #self.parent.parent.PlotFrame.PlotPanel.axes.autoscale(False)

        
    def on_show(self,event):
        """
        Called on frame show and hide. Used to prepare the line plot panel,
        adjust the axes, prevent the autoscale of the plotpanel and
        connect the mouse click to the on_click routine.

        Attributes:
          event (EVT_SHOW): a hide/show event object
        
        """
        
        if event.GetShow():

            self.axes.cla()            
            self.axes.set_ylabel(view.State.config['Cblabel'])
            self.axes.set_xlabel(r'$\sqrt{\Delta_x^2+\Delta_y^2}$')
            self.fig.tight_layout()
            self.canvas.draw()

            self.left = False
            self.right = False

            #self.plotpanel.draw_plot()
            dispatcher.send(signal.PLOT_UPDATE_CANVAS,self)
            
            self.plotpanel.axes.autoscale(False)

            self.cid = self.plotpanel.canvas.mpl_connect('button_press_event',self.on_click)
            
        else:
            self.plotpanel.axes.autoscale(True)
            self.cid = self.plotpanel.canvas.mpl_disconnect(self.cid)
        
    def on_plot(self,event):
        self.draw_linetrace()

    def on_close(self,event):
        if hasattr(self,'currentline'):
            self.currentline.removeline()
            delattr(self,'currentline')
        if self.linelist:
            for line in self.linelist:
                line.removeline()
        self.linelist = []

        dispatcher.send(signal.PLOT_UPDATE_CANVAS,self)
        self.parent.Hide()

    def on_click(self,event):

        if event.inaxes!=self.plotpanel.axes: return

        if event.button == 1:
            self.x1 = event.xdata
            self.y1 = event.ydata
            self.left = True
        if event.button == 3:
            self.x2 = event.xdata
            self.y2 = event.ydata
            self.right = True
        if self.left and self.right:
            self.draw_line()


    def draw_line(self):
        #import pdb;pdb.set_trace()

        if not hasattr(self, 'currentline'):
            self.currentline = Line(self.plotpanel.axes,self.x1,self.x2, self.y1,self.y2)
        else:
            self.currentline.set_data(self.x1,self.x2, self.y1,self.y2)

        dispatcher.send(signal.PLOT_UPDATE_CANVAS,self)

        #self.parent.parent.PlotFrame.PlotPanel.canvas.draw()


    def draw_linetrace(self):

        datafile = view.State.datafile

        idx1 = self.closest_idx(self.x1,datafile.Xrange)
        idx2 = self.closest_idx(self.x2,datafile.Xrange)

        idy1 = self.closest_idx(self.y1,datafile.Yrange)
        idy2 = self.closest_idx(self.y2,datafile.Yrange)

        
        if idx1 == idx2:
            x_range_int = [idx1]
            y_range_int = range(idy1,idy2+1,np.sign(idy2-idy1))
        elif idy1 == idy2:
            x_range_int = range(idx1,idx2+1,np.sign(idx2-idx1))
            y_range_int = [idy1]            
        elif np.abs(idx2 - idx1) > np.abs(idy2 - idy1):
            # x_range = range(idx1,idx2+1,np.sign(idx2-idx1))
            # y_range = np.array([self.closest_idx(self.currentline.get_y(xval),datafile.Yrange) for xval in datafile.Xrange[x_range]])
            x_range = np.linspace(datafile.Xrange[idx1],datafile.Xrange[idx2],abs(idx2-idx1)*self.resolution)
            y_range_int = np.array([self.closest_idx(self.currentline.get_y(xval),datafile.Yrange) for xval in x_range])
            x_range_int = [self.closest_idx(x_val,datafile.Xrange) for x_val in x_range]
            
        else:
            # y_range = range(idy1,idy2,np.sign(idy2-idy1))
            # x_range = np.array([self.closest_idx(self.currentline.get_x(yval),datafile.Xrange) for yval in datafile.Yrange[y_range]])
            y_range = np.linspace(datafile.Yrange[idy1],datafile.Yrange[idy2],abs(idy2-idy1)*self.resolution)
            x_range_int = np.array([self.closest_idx(self.currentline.get_x(yval),datafile.Xrange) for yval in y_range])
            y_range_int = [self.closest_idx(y_val,datafile.Yrange) for y_val in y_range]


        dataview = datafile.Zdata[y_range_int,x_range_int]

        distance = np.linspace(0,np.sqrt(((y_range_int[-1]-y_range_int[0])*datafile.dY)**2+((x_range_int[-1]-x_range_int[0])*datafile.dX)**2),dataview.shape[0])

        self.axes.plot(distance,dataview)
        self.canvas.draw()

        self.linelist.append(self.currentline)
        delattr(self,'currentline')
        self.right = False
        self.left = False



    def closest_idx(self,val,array):
        return (np.abs(array-val)).argmin()
