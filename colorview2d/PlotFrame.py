import wx
import numpy as np
import yaml
import matplotlib.pyplot as plt
import matplotlib as mpl
from View import View

from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar

from matplotlib.ticker import FormatStrFormatter


class PlotFrame(wx.Frame):
    """
    The plot frame hosts the panel for the 2D colorplot.
    """
    
    def __init__(self,parent):
        """
        Initialize the panel.
        """
        self.parent = parent
        wx.Frame.__init__(self, parent, title="Plotting "+self.parent.config['datafilename'],size=(700,500))
        self.PlotPanel = PlotPanel(self)
        self.Layout()

class PlotPanel(wx.Panel):
    """
    The plot panel hosts the canvas on which the 2D colorplot is drawn.
    """
    
    def __init__(self, parent):
        """
        Creates the mpl figure with a fixed 75 dpi and draws a first (dummy) plot.
        """
        wx.Panel.__init__(self, parent)
        self.parent = parent

        self.config = self.parent.parent.config

        # Create the mpl Figure and FigCanvas objects.
        # We add a toolbar to the canvas and add everything 
        # to a sizer

        self.fig = plt.figure(1,dpi=self.config['Dpi'])
        self.axes = self.fig.add_subplot(111)
        self.canvas = FigCanvas(self, wx.ID_ANY, self.fig)

        self.toolbar = NavigationToolbar(self.canvas)

        self.mainbox = wx.BoxSizer(wx.VERTICAL)
        self.mainbox.Add(self.toolbar,0)
        self.mainbox.Add(self.canvas, 1,flag =  wx.EXPAND)

        # The Sizer mainbox determines the size of the Panel
        self.SetSizer(self.mainbox)

        # We load a dummy image
        self.plot = self.axes.imshow(np.random.random((2,2)))

        # Call all sizing routines
        self.Layout()

    def update(self,subject=None):
        from View import View
        from MainFrame import MainPanel
        """
        The call-back function of the Plotpanel. It observes the MainPanel and the View object.
        The reaction to a notification event is specific to the caller.

        Caller is View:
          Set the data in the datafile and adjust the axes.
        Caller is MainPanel:
          Adjust the colorscale according to controls on the MainPanel
     
        """
        
        if isinstance(subject,View):
            self.plot.set_data(subject.get_data())
            self.plot.set_extent([subject.datafile.Xleft,subject.datafile.Xright,subject.datafile.Ybottom,subject.datafile.Ytop])

            self.axes.set_xlim(subject.datafile.Xleft,subject.datafile.Xright)
            self.axes.set_ylim(subject.datafile.Ybottom,subject.datafile.Ytop)
            
        elif isinstance(subject,MainPanel):
            width = subject.widthspin.GetValue()
            centre = subject.centrespin.GetValue()

            cbar_min = centre - width/2.
            cbar_max = centre + width/2.

            self.plot.set_cmap(self.config['Colormap'])
            self.plot.set_clim(cbar_min,cbar_max)

        self.plot.changed()
        self.canvas.draw()


    def draw_plot(self):
        """
        Draws a plot of the datafile object in the MainFrame.

        The plot is drawn from zero, the figure axes are cleared and
        the colorbar controls are initialized or updated, if neccessary.
        
        This routine is needed to avoid a race condition during intialization 
        in the Observer Pattern.
        
        """

        self.fig.clear()

        self.fig.set_size_inches((self.config['Width'],self.config['Height']))

        self.apply_config()

        self.axes = self.fig.add_subplot(111)


        view = self.parent.parent.view

        self.plot = self.axes.imshow(view.get_data(),
            extent=[view.datafile.Xleft,view.datafile.Xright,view.datafile.Ybottom,view.datafile.Ytop],
            aspect='auto',
            origin='lower',
            interpolation="nearest")
  
        self.plot.set_cmap(self.config['Colormap'])
        self.colorbar = plt.colorbar(self.plot)

        self.set_labels()

        self.fig.tight_layout()

        self.canvas.draw()
        self.Layout()

    def set_labels(self):
        self.axes.set_ylabel(self.config['Ylabel'])
        self.axes.set_xlabel(self.config['Xlabel'])

        self.colorbar.set_label(self.config['Cblabel'])
        if not self.config['Xtickformat'] == 'auto':
            self.axes.xaxis.set_major_formatter(FormatStrFormatter(self.config['Xtickformat']))
        if not self.config['Ytickformat'] == 'auto':
            self.axes.yaxis.set_major_formatter(FormatStrFormatter(self.config['Ytickformat']))
        if not self.config['Cbtickformat'] == 'auto':
            self.colorbar.yaxis.set_major_formatter(FormatStrFormatter(self.config['Cbtickformat']))
            self.colorbar.update_ticks()


    def apply_config(self):
        """
        Applies the ticks and labels stored in the MainFrame.
        """
        import pdb; pdb.set_trace()
        # Apply plt.rcParams

        print "Font now {}".format(self.config['Font'])
        plt.rcParams['font.family'] = self.config['Font']
        plt.rcParams['font.size'] = self.config['Fontsize']
        plt.rcParams['xtick.major.size'] = self.config['Xticklength']
        plt.rcParams['ytick.major.size'] = self.config['Yticklength']



