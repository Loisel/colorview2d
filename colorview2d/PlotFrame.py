import wx
import numpy as np
import yaml
import logging
import matplotlib.pyplot as plt
import matplotlib as mpl
from View import View
from LineoutFrame import LineoutPanel

from pydispatch import dispatcher
import Signal

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

        # self.config = self.parent.parent.config

        # Create the mpl Figure and FigCanvas objects.
        # We add a toolbar to the canvas and add everything 
        # to a sizer

        self.fig = plt.figure(1,dpi=self.parent.parent.config['Dpi'])
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

        # Connect all events related to the plot to the respective handlers
        dispatcher.connect(self.handle_update_color, signal = Signal.PLOT_UPDATE_COLOR, sender=dispatcher.Any)
        dispatcher.connect(self.handle_change_colormap, signal = Signal.PLOT_CHANGE_COLORMAP, sender=dispatcher.Any)
        dispatcher.connect(self.handle_update_datafile, signal = Signal.PLOT_UPDATE_DATAFILE, sender=dispatcher.Any)
        dispatcher.connect(self.handle_draw_plot_anew, signal = Signal.PLOT_DRAW_ANEW, sender=self.parent.parent)
        dispatcher.connect(self.handle_update_canvas, signal = Signal.PLOT_UPDATE_CANVAS, sender=dispatcher.Any)
        dispatcher.connect(self.handle_config_changed, signal = Signal.PLOT_CHANGE_CONFIG, sender=dispatcher.Any)

    def handle_change_colormap(self,sender,colormap = None):
        self.plot.set_cmap(colormap)
        self.update()
        
    def handle_update_color(self,sender,minval = None,maxval = None):
        # import pdb; pdb.set_trace()
        self.plot.set_clim(minval,maxval)
        self.update()

    def handle_update_datafile(self,sender,datafile = None):
        self.plot.set_data(datafile.Zdata)
        self.plot.set_extent([datafile.Xleft,datafile.Xright,datafile.Ybottom,datafile.Ytop])
        self.axes.set_xlim(datafile.Xleft,datafile.Xright)
        self.axes.set_ylim(datafile.Ybottom,datafile.Ytop)
        self.update()

    def handle_update_canvas(self):
        self.update()
        
    def update(self):
        """
        The call-back function of the Plotpanel. It observes the MainPanel and the View object.
        The reaction to a notification event is specific to the caller.

        Caller is View:
          Set the data in the datafile and adjust the axes.
        Caller is MainPanel:
          Adjust the colorscale according to controls on the MainPanel
     
        """
        
        self.plot.changed()
        self.canvas.draw()



    def handle_draw_plot_anew(self,sender,view = None, config = None):
        """
        Draws a plot of the datafile object in the MainFrame.

        The plot is drawn from zero, the figure axes are cleared and
        the colorbar controls are initialized or updated, if neccessary.
        
        This routine is needed to avoid a race condition during intialization 
        in the Observer Pattern.
        
        """

        self.fig.clear()

        self.apply_config_pre_plot(config)

        self.axes = self.fig.add_subplot(111)

        self.plot = self.axes.imshow(view.get_data(),
            extent=[view.datafile.Xleft,view.datafile.Xright,view.datafile.Ybottom,view.datafile.Ytop],
            aspect='auto',
            origin='lower',
            interpolation="nearest")

        
        if not config['Cbtickformat'] == 'auto':
            self.colorbar = self.fig.colorbar(self.plot, format = FormatStrFormatter(config['Cbtickformat']))
        else:
            self.colorbar = self.fig.colorbar(self.plot)

        self.apply_config_post_plot(config)

        self.fig.tight_layout()

        self.canvas.draw()
        self.Layout()

    def apply_config_post_plot(self,config):
        self.axes.set_ylabel(config['Ylabel'])
        self.axes.set_xlabel(config['Xlabel'])

        self.colorbar.set_label(config['Cblabel'])
        if not config['Xtickformat'] == 'auto':
            self.axes.xaxis.set_major_formatter(FormatStrFormatter(config['Xtickformat']))
        if not config['Ytickformat'] == 'auto':
            self.axes.yaxis.set_major_formatter(FormatStrFormatter(config['Ytickformat']))
        self.plot.set_cmap(config['Colormap'])


    def apply_config_pre_plot(self,config):
        """
        Applies the ticks and labels stored in the MainFrame.
        """
        # import pdb; pdb.set_trace()
        # Apply plt.rcParams

        logging.info("Font now {}".format(config['Font']))
        plt.rcParams['font.family'] = config['Font']
        plt.rcParams['font.size'] = config['Fontsize']
        plt.rcParams['xtick.major.size'] = config['Xticklength']
        plt.rcParams['ytick.major.size'] = config['Yticklength']
        self.fig.set_size_inches((config['Width'],config['Height']))




    def handle_config_changed(self, sender, config = None):
        """
        Respond to a 'PLOT_UPDATE_CONFIG' event.
        Updates the plot with the settings in the config file.

        Note:
        The view object has to be passed to handle_draw_plot_anew which is not nice.
        Unfortunately it is not easy to update the font.family property of mpl without
        redrawing the whole thing.

        """
        self.handle_draw_plot_anew(self,config = config, view = self.parent.parent.view)