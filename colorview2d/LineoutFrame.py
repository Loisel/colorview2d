import wx
from Subject import Subject
import numpy as np
import matplotlib.pyplot as plt
from MyLine import MyLine

from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar


class LineoutFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent, title="Line trace tool",size=(800,600))
        self.parent = parent
        self.LineoutPanel = LineoutPanel(self)
        self.Layout()


class LineoutPanel(wx.Panel,Subject):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        Subject.__init__(self)

        self.parent = parent
        self.attach(self.parent.parent.PlotFrame.PlotPanel)

        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None

        self.linelist = []

        self.fig = plt.figure()

        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        self.canvas = FigCanvas(self, wx.ID_ANY, self.fig)
        self.toolbar = NavigationToolbar(self.canvas)

        self.mainbox = wx.BoxSizer(wx.VERTICAL)
        self.mainbox.Add(self.toolbar,0)

        self.axes.set_ylabel(self.parent.parent.config['Cblabel'])

        self.fig.tight_layout()

        self.canvas.draw()

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

        self.parent.parent.PlotFrame.PlotPanel.axes.autoscale(False)
        self.currentline = MyLine(self.parent.parent.PlotFrame.PlotPanel.axes)
        self.cid = parent.parent.PlotFrame.PlotPanel.canvas.mpl_connect('button_press_event',self.on_click)
        

    def on_plot(self,event):
        self.draw_linetrace()
    def on_close(self,event):
        self.currentline.removeline()
        if self.linelist:
            for line in self.linelist:
                line.removeline()

        self.notify()
        self.parent.parent.PlotFrame.PlotPanel.axes.autoscale(True)

        self.parent.Destroy()

    def on_click(self,event):
        if event.inaxes!=self.currentline.axes: return

        if event.button == 1:
            self.x1 = event.xdata
            self.y1 = event.ydata
        if event.button == 3:
            self.x2 = event.xdata
            self.y2 = event.ydata
        if self.x1 and self.x2:
            self.draw_line()


    def draw_line(self):
        self.currentline.set_data(self.x1,self.x2, self.y1,self.y2)
        self.notify()

        #self.parent.parent.PlotFrame.PlotPanel.canvas.draw()


    def draw_linetrace(self):

        datafile = self.parent.parent.view.datafile

        idx1 = self.closest_idx(self.x1,datafile.Xrange)
        idx2 = self.closest_idx(self.x2,datafile.Xrange)

        idy1 = self.closest_idx(self.y1,datafile.Yrange)
        idy2 = self.closest_idx(self.y2,datafile.Yrange)

        
        if idx1 == idx2:
            x_range = [idx1]
            y_range = range(idy1,idy2+1,np.sign(idy2-idy1))
        elif idy1 == idy2:
            x_range = range(idx1,idx2+1,np.sign(idx2-idx1))
            y_range = [idy1]            
        elif np.abs(idx2 - idx1) > np.abs(idy2 - idy1):
            x_range = range(idx1,idx2+1,np.sign(idx2-idx1))
            # x_range = np.linspace(idx1,idx2,int(np.absolute(idx2-idx1)+1)).astype(int)
            y_range = np.array([self.closest_idx(self.currentline.get_y(xval),datafile.Yrange) for xval in datafile.Xrange[x_range]])

        else:
            y_range = range(idy1,idy2,np.sign(idy2-idy1))
            x_range = np.array([self.closest_idx(self.currentline.get_x(yval),datafile.Xrange) for yval in datafile.Yrange[y_range]])


        dataview = datafile.Zdata[y_range,x_range]

        self.axes.plot(dataview)
        self.canvas.draw()

        self.linelist.append(self.currentline)
        self.currentline = MyLine(self.parent.parent.PlotFrame.PlotPanel.axes)



    def closest_idx(self,val,array):
        return (np.abs(array-val)).argmin()
