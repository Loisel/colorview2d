import wx
import numpy as np
import yaml
import logging
import matplotlib.pyplot as plt
import matplotlib as mpl
import View
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
        wx.Frame.__init__(self, parent, title="Plotting "+View.State.config['datafilename'],size=(700,500))
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

        self.fig = plt.figure(1,dpi = View.State.config['Dpi'])
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
        dispatcher.connect(self.handle_update_datafile, signal = Signal.PLOT_UPDATE_DATAFILE)
        dispatcher.connect(self.handle_draw_plot_anew, signal = Signal.PLOT_DRAW_ANEW)
        dispatcher.connect(self.handle_update_canvas, signal = Signal.PLOT_UPDATE_CANVAS, sender=dispatcher.Any)
        dispatcher.connect(self.handle_config_changed, signal = Signal.PLOT_CHANGE_CONFIG, sender=dispatcher.Any)

    def handle_change_colormap(self,sender):
        self.plot.set_cmap(View.State.config['Colormap'])
        self.update()
        
    def handle_update_color(self,sender,minval = None,maxval = None):
        # import pdb; pdb.set_trace()
        self.plot.set_clim(minval,maxval)
        self.update()

    def handle_update_datafile(self,sender):
        self.plot.set_data(View.State.datafile.Zdata)
        self.plot.set_extent([View.State.datafile.Xleft,View.State.datafile.Xright,View.State.datafile.Ybottom,View.State.datafile.Ytop])
        self.axes.set_xlim(View.State.datafile.Xleft,View.State.datafile.Xright)
        self.axes.set_ylim(View.State.datafile.Ybottom,View.State.datafile.Ytop)
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



    def handle_draw_plot_anew(self,sender):
        """
        Draws a plot of the datafile object in the MainFrame.

        The plot is drawn from zero, the figure axes are cleared and
        the colorbar controls are initialized or updated, if neccessary.
        
        This routine is needed to avoid a race condition during intialization 
        in the Observer Pattern.
        
        """

        self.fig.clear()

        self.apply_config_pre_plot()

        self.axes = self.fig.add_subplot(111)

        self.plot = self.axes.imshow(View.get_data(),
            extent=[View.State.datafile.Xleft,View.State.datafile.Xright,View.State.datafile.Ybottom,View.State.datafile.Ytop],
            aspect='auto',
            origin='lower',
            interpolation="nearest")        

        self.apply_config_post_plot()

        self.fig.tight_layout()

        self.canvas.draw()
        self.Layout()

    def apply_config_post_plot(self):
        """
        The function applies the rest of the configuration to the plot.
        Note that the colorbar is created in this function because
        colorbar.ax.yaxis.set_major_formatter(FormatStrFormatter(string)) does not work properly.
        """
        self.axes.set_ylabel(View.State.config['Ylabel'])
        self.axes.set_xlabel(View.State.config['Xlabel'])

        if not View.State.config['Cbtickformat'] == 'auto':
            self.colorbar = self.fig.colorbar(self.plot, format = FormatStrFormatter(View.State.config['Cbtickformat']))
        else:
            self.colorbar = self.fig.colorbar(self.plot)
        self.colorbar.set_label(View.State.config['Cblabel'])
        if not View.State.config['Xtickformat'] == 'auto':
            self.axes.xaxis.set_major_formatter(FormatStrFormatter(View.State.config['Xtickformat']))
        if not View.State.config['Ytickformat'] == 'auto':
            self.axes.yaxis.set_major_formatter(FormatStrFormatter(View.State.config['Ytickformat']))
        self.plot.set_cmap(View.State.config['Colormap'])


    def apply_config_pre_plot(self):
        """
        Applies the ticks and labels stored in the MainFrame.
        This function is called before the actual plot is drawn.
        This pre_plot hook is necessary because the rcParams['font.family']
        attribute can not be changed after the plot is drawn.
        """

        logging.info("Font now {}".format(View.State.config['Font']))
        plt.rcParams['font.family'] = View.State.config['Font']
        plt.rcParams['font.size'] = View.State.config['Fontsize']
        plt.rcParams['xtick.major.size'] = View.State.config['Xticklength']
        plt.rcParams['ytick.major.size'] = View.State.config['Yticklength']
        self.fig.set_size_inches((View.State.config['Width'],View.State.config['Height']))




    def handle_config_changed(self, sender):
        """
        Respond to a 'PLOT_UPDATE_CONFIG' event.
        Updates the plot with the settings in the config file.

        Note:
        The view object has to be passed to handle_draw_plot_anew which is not nice.
        Unfortunately it is not easy to update the font.family property of mpl without
        redrawing the whole thing.

        """
        self.handle_draw_plot_anew(self)