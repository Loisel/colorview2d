import wx
import numpy as np
import re
import os
import gpfile

import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt

from matplotlib.pyplot import cm
from floatspin import FloatSpin,EVT_FLOATSPIN
from floatslider import FloatSlider

from wx.lib.masked import NumCtrl,EVT_NUM

import view

from plotframe import PlotFrame
from lineoutframe import LineoutFrame
from linecutframe import LinecutFrame
from distanceframe import DistanceFrame

from slopeexframe import SlopeExFrame
# Experimental feature
# from BinaryFitFrame import BinaryFitFrame
from labelticksframe import LabelticksFrame

from pydispatch import dispatcher
import signal

import utils
import yaml
import logging


"""
The mainframe module hostst the MainFrame class and the MainPanel class.
In the MainFrame.__init__ the view object is intialized and all other frames 
are created.
The MainPanel hosts the colorbar controls and the mod plugin widgets.
"""

class MainFrame(wx.Frame):
    """
    Central class of the application.
    
    The MainFrame class hosts all subframes, the datafile object,
    the colormap and information on ticks and labels.
    """

    title = 'colorplot utility: '

    def __init__(self,parent,cv2dpath=None,datafilename=None,columns=None):
        """
        Initialize the frame, create subframes and load a default 
        datafile object.
        
        Create Menu, MainPanel, PlotFrame, LineoutFrame, LinecutFrame and
        SlopeExFrame. All utility frames are created beforehand and viewed
        on demand.
        """
        # find a way to autosize the frame!
        # this is annoying, especially with respect to the plugins
        wx.Frame.__init__(self, None, wx.ID_ANY, size=(630,550),style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent

        
        if cv2dpath:
            # If a config file is provided, we load that one.
            # All other parameters are ignored.
            cfgpath = os.path.join(os.getcwd(),cv2dpath)
            datafilename = None
            columns = None
        else:
            # The name of the default config file is hard coded.
            # utils.resource_path adds the path to the 
            # library in win and linux
            cfgpath = utils.resource_path('default.cv2d')
            
        # The config file is parsed, 
        # modlist is a string variable that is given to the view
        # to create the mod pipeline
        view.parse_config(cfgpath)

        # If a datafilename is specified, we use this instead of the default
        # Same for the the columns        
        if datafilename:
            view.State.config['datafilename'] = datafilename
            data_filepath = os.path.join(os.getcwd(), view.State.config['datafilename'])
            if columns:
                view.State.config['datafilecolumns'] = utils.read_columns(columns)
        else:
            # The path to the datafile, either in the cwd or in the lib (default)
            # We assume that the datafile is in the same dir as the cv2d dile
            data_filepath = os.path.join(os.path.dirname(cfgpath), view.State.config['datafilename'])


        # Set title for the frame and align
        self.SetTitle(self.title+view.State.config['datafilename'])
        self.alignToBottomRight()

        # Create menu and status bar
        self.create_menu()
        self.create_status_bar()

        # The plot frame is created first with a dummy plot
        self.PlotFrame = PlotFrame(self)

        # The MainPanel contains all the colorbar controls
        # The PlotPanel listens to the MainPanel for changes (e.g. to the colorbar)
        self.MainPanel = MainPanel(self)
        # self.MainPanel.attach(self.PlotFrame.PlotPanel)

        # The frame with the settings (font, ticks, labels, etc)
        self.LabelticksFrame = LabelticksFrame(self)

        # The datafile of the global view object is set
        view.set_datafile(gpfile.Gpfile(data_filepath,view.State.config['datafilecolumns']))

        # We have to draw the plot first before we can apply the modlist
        dispatcher.send(signal.PLOT_DRAW_ANEW,self)

        # The other tools are intialized
        self.LinecutFrame = LinecutFrame(self)
        self.LineoutFrame = LineoutFrame(self)
        self.SlopeExFrame = SlopeExFrame(self)
        self.DistanceFrame = DistanceFrame(self)
        
        # Then the mod pipeline is applied (if any)
        # Creating the list of plugins (modlist).
        view.create_modlist()
        view.apply_pipeline()
        
        self.PlotFrame.Show()
        self.PlotFrame.Layout()


    def alignToBottomRight(self):
        """
        Used to align the Main Window to the bottom right of the screen.
        """
        dw, dh = wx.DisplaySize()
        w, h = self.GetSize()
        x = dw -w
        y = dh-1.2*h
        self.SetPosition((x, y))


    def create_menu(self):
        """
        Creates the Menu in the toolbar.
        """
        self.menubar = wx.MenuBar()
        menu_file = wx.Menu()
        menu_tools = wx.Menu()
        menu_axes = wx.Menu()

        m_load = menu_file.Append(wx.ID_ANY, "&Load Data\tCtrl-L", "Load data from file")
        self.Bind(wx.EVT_MENU, self.on_load_plot, m_load)
        m_loadcv2d = menu_file.Append(wx.ID_ANY, "Load &Config\tCtrl-C", "Load cv2d config file")
        self.Bind(wx.EVT_MENU, self.on_load_cv2d, m_loadcv2d)
        m_svdt = menu_file.Append(wx.ID_ANY, "&Save Data\tCtrl-S", "Save data to file")
        self.Bind(wx.EVT_MENU, self.on_save_datafile, m_svdt)
        menu_file.AppendSeparator()
        m_svpdf = menu_file.Append(wx.ID_ANY, "Save &Pdf\tCtrl-P", "Save to pdf file")
        self.Bind(wx.EVT_MENU, self.on_save_pdf, m_svpdf)
        m_svcfg = menu_file.Append(wx.ID_ANY, "Save Config", "Save cv2d config file")
        self.Bind(wx.EVT_MENU, self.on_save_cv2d, m_svcfg)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(wx.ID_ANY, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)

        m_labelticks = menu_axes.Append(wx.ID_ANY, "&Configure Plot\tCtrl-C", "Set axes labels and tick label format")
        self.Bind(wx.EVT_MENU,self.on_labelticks,m_labelticks)


        m_linecut = menu_tools.Append(wx.ID_ANY,  "Linecut &Extraction\tCtrl-E", "Extract linecut series")
        self.Bind(wx.EVT_MENU, self.on_linecut, m_linecut)

        m_slopex = menu_tools.Append(wx.ID_ANY,  "Sl&ope Extraction\tCtrl-O", "Extract linear slope")
        self.Bind(wx.EVT_MENU, self.on_slopex, m_slopex)

        m_lineout = menu_tools.Append(wx.ID_ANY,  "Linecut &Viewer\tCtrl-V", "Plot data along line")
        self.Bind(wx.EVT_MENU, self.on_lineout, m_lineout)

        m_distance = menu_tools.Append(wx.ID_ANY,  "&Distance Viewer\tCtrl-D", "Measure distances")
        self.Bind(wx.EVT_MENU, self.on_distance, m_distance)

        # m_binaryfit = menu_tools.Append(wx.ID_ANY, "Segment and Fit (beta!)", "Fit to prominent data features")
        # self.Bind(wx.EVT_MENU,self.on_binaryfit,m_binaryfit)


        menu_help = wx.Menu()
        m_about = menu_help.Append(wx.ID_ANY, "&About\tF1", "About colorview2d.")
        self.Bind(wx.EVT_MENU, self.on_about, m_about)

        self.menubar.Append(menu_file, "&File")
        self.menubar.Append(menu_axes, "&Axes")
        self.menubar.Append(menu_tools, "&Tools")
        self.menubar.Append(menu_help, "&Help")
        self.SetMenuBar(self.menubar)


    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def on_labelticks(self,event):
        """
        Show the previously created labelticks frame.
        """
        self.LabelticksFrame.Show()

    def on_lineout(self,event):
        """
        Shows the Frame to extract linecuts.
        
        """
        self.LineoutFrame.Show()

    def on_binaryfit(self,event):
        """
        Shows the fitting Frame.

        The frame is modal. A previously created fit is redrawn.
        """
        #self.BinaryFitFrame = BinaryFitFrame(self)
        #self.BinaryFitFrame.Show()

    def on_linecut(self,event):
        """
        Shows the frame to extract linecut series.

        """
        #self.PlotFrame.PlotPanel.axes.autoscale(False)
        dispatcher.send(signal.PLOT_AUTOSCALE_OFF,self)
        self.LinecutFrame.Show()

    def on_slopex(self,event):
        """
        Shows the Frame to extract slopes.

        """
        self.SlopeExFrame.Show()

    def on_distance(self,event):
        """
        Shows the Frame to measure distances.

        """
        self.DistanceFrame.Show()


    def on_save_datafile(self, event):
        """
        Saves the datafile in gnuplot format.

        The datafile is saved with information
        on the currently applied modifications and their parameters.
        """
        file_choices = "DAT (*.dat)|*.dat"


        comment = """\
# Original filename: {}
#
# data modifications: {}
#
# axes: {} | {} | {}
""".format(view.State.config['datafilename'],view.pipeline,self.Xlabel,self.Ylabel,self.Cblabel)

        dlg = wx.FileDialog(
            self,
            message="Save plot data as...",
            defaultDir=os.getcwd(),
            defaultFile=view.State.config['datafilename'],
            wildcard=file_choices,
            style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            view.State.datafile.save(path,comment)


    def on_save_pdf(self, event):
        """
        Saves the plot in pdf format.

        """
        file_choices = "PDF (*.pdf)|*.pdf"
        defaultfilename = os.path.splitext(view.State.config['datafilename'])[0]+'.pdf'

        dlg = wx.FileDialog(
            self,
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile=defaultfilename,
            wildcard=file_choices,
            style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.PlotFrame.PlotPanel.fig.set_size_inches(view.State.config['Width'], view.State.config['Height'])
            self.PlotFrame.PlotPanel.fig.savefig(path, dpi = view.State.config['Dpi'])
            self.PlotFrame.PlotPanel.Layout()

    def on_save_cv2d(self, event):
        """
        Saves a cv2d config file.

        """
        file_choices = "CV2D (*.cv2d)|*.cv2d"
        defaultfilename = os.path.splitext(view.State.config['datafilename'])[0]+'.cv2d'

        dlg = wx.FileDialog(
            self,
            message="Save config as...",
            defaultDir=os.getcwd(),
            defaultFile=defaultfilename,
            wildcard=file_choices,
            style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            view.save_config(path)
                

    def on_exit(self, event):
        """
        Exits the program.
        """
        self.Destroy()
        self.parent.Exit()

    def on_about(self, event):
        """
        Shows information about the program and lists some features.
        """
        msg = """ A 2D color plotting tool. Built using wxPython and matplotlib.

         * Automatically adjust axes and colorbar.
         * Change center, width and min or max of the colorbar live!
         * Open and save gnuplot style data files.
         * Save png and pdf files.
         * Extract series of linetraces.
         * Extract linear slopes by drawing lines in the plot.
         * Apply various modifications to the plot (e.g., median or gaussian filter)
         * Design your own modification plugins.
        """
        dlg = wx.MessageDialog(self, msg, "About", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()


    def on_load_cv2d(self,event):
        """
        Shows a file dialog to select a coloview2d config file (*.cv2d)
        The file is loaded and the pipeline is applied to the view.
        """
        
        file_choices = "CV2D (*.cv2d)|*.cv2d"

        dlg = wx.FileDialog(self,
            message="Load cv2d config file...",
            defaultDir=os.getcwd(),
            wildcard=file_choices,
            style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dirname = os.path.dirname(path)
            # The config is overwritten
            view.parse_config(path)
            # The datafile is replaced
            view.set_datafile(gpfile.Gpfile(os.path.join(dirname,view.State.config['datafilename']),view.State.config['datafilecolumns']))
            dispatcher.send(signal.PLOT_DRAW_ANEW,self)
            # ... and the pipeline is applied
            view.apply_pipeline()

            # We make sure the title is correct
            self.SetTitle(self.title+view.State.datafile.filename)
            # The slope extraction utility has to know about the correct dimensions
            # of the datafile (the FloatSpin tools need the x/y range)
            # self.SlopeExFrame.SlopeExPanel.update()
                
        
    def on_load_plot(self,event):
        """
        Shows a dialog to load datafile from gnuplot-style file on disk.

        Reads a ASCII file formatted in columns and blocks seperated by newlines.
        The first dimension (x-axis) is the value which is constant over one block.
        It is supposed to increase linearly with blocknumber.
        This value is found typically in the first column.
        The second dimension (y-axis) is varied linearly within each block.
        The third dimension contains the actual measured data (z-axis)
        and there is no preliminary assumption on the values.

        The columns connected to the axes of the datafile
        can be selected in an additional dialog.
        """
        file_choices = "DAT (*.dat)|*.dat"

        dlg = wx.FileDialog(self,
            message="Load data file...",
            defaultDir=os.getcwd(),
            wildcard=file_choices,
            style=wx.OPEN)


        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()

            columns = (0,1,2)
            # A checkbox is needed "Reset Config" or aequivalent
            # dlg = wx.TextEntryDialog(self, 'Enter the column numbers for the 3d data in the form (a,b,c)','Columns:')
            
            # dlg.SetValue("{},{},{}".format(columns[0],columns[1],columns[2]))

            dlg = utils.SettingsDialog(self)
            if dlg.ShowModal() == wx.ID_OK:
                columns = dlg.GetColumns()
                reset_settings = dlg.GetSettingChk()
                dlg.Destroy()


                if reset_settings:
                    cfgpath = utils.resource_path('default.cv2d')
                    view.parse_config(cfgpath)

                # We set the new datafile in the view
                # By changing the datafile, the view notifies its observers
                # and the plot is updated
                view.set_datafile(gpfile.Gpfile(path,columns))

                dispatcher.send(signal.PLOT_DRAW_ANEW,self)
                
                view.State.config['datafilename'] = os.path.basename(path)

                self.SetTitle(self.title+view.State.datafile.filename)
            
class MainPanel(wx.Panel):
    """
    Panel with colorbar controls and checkboxes for the plot modifications.
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        
        # Magic numbers for the "fine-graindedness" of the FloatSpin and FloatSlider objects
        self.spin_divider = 10000
        self.slide_divider = 1000
        
        dispatcher.connect(self.handle_update_colorctrl, signal = signal.PANEL_UPDATE_COLORCTRL, sender = dispatcher.Any)
        dispatcher.connect(self.handle_add_modwidgets, signal = signal.PANEL_ADD_MODWIDGETS, sender = dispatcher.Any)
        self.create_panel()
        
    def create_panel(self):
        """
        Create, show and layout all widgets in the panel.
        """
        
        self.colorwidgetlist = []

        maxval = 1.
        minval = -1.

        spin_incr = np.absolute(maxval-minval)/self.spin_divider
        slide_incr = np.absolute(maxval-minval)/self.slide_divider

        self.colormapselect_label = wx.StaticText(self, wx.ID_ANY,'Colormap')

        self.colormapselect = wx.ComboBox(self,
                                          size=wx.DefaultSize,
                                          style=wx.CB_READONLY)
        self.maps = [m for m in cm.datad if not m.endswith("_r")]
        self.maps.sort()

        for m in self.maps:
            self.colormapselect.Append(m)

        self.colormapselect.SetStringSelection(view.State.config['Colormap'])

        self.Bind(wx.EVT_COMBOBOX,self.on_colormapselect,self.colormapselect)

        self.widthspin_label = wx.StaticText(self, wx.ID_ANY,
            "Color width: ")


        self.colorwidgetlist.append(self.widthspin_label)

        self.widthspin = FloatSpin(self, name='width',
            value=maxval-minval,
            min_val=0.,
            max_val=maxval-minval,
            increment = spin_incr,
            digits = 3
            )

        self.colorwidgetlist.append(self.widthspin)

        self.widthslider = FloatSlider(self,wx.ID_ANY,maxval-minval,0,maxval-minval,slide_incr,
                                       size = (200,15),
                                       name = 'widthslider')

        self.Bind(wx.EVT_SCROLL,self.on_scroll,self.widthslider)


        self.widthspin.SetFormat("%e")

        self.centrespin_label = wx.StaticText(self, wx.ID_ANY,
            "Color center: ")

        self.colorwidgetlist.append(self.centrespin_label)

        self.centrespin = FloatSpin(self, name='centre',
            value=(maxval+minval)/2.,
            min_val=minval,
            max_val=maxval,
            increment = spin_incr,
            digits = 3)

        self.colorwidgetlist.append(self.centrespin)

        self.centreslider = FloatSlider(self,wx.ID_ANY,(maxval+minval)/2,minval,maxval,slide_incr,
                                    size = (200,15),
                                    name = 'centreslider')

        self.Bind(wx.EVT_SCROLL,self.on_scroll,self.centreslider)

        self.colorwidgetlist.append((0,0))
        self.colorwidgetlist.append(self.widthslider)
        self.colorwidgetlist.append((0,0))
        self.colorwidgetlist.append(self.centreslider)



        self.centrespin.SetFormat("%e")

        self.minspin_label = wx.StaticText(self, wx.ID_ANY,
            "Color min: ")

        self.colorwidgetlist.append(self.minspin_label)

        self.minspin = FloatSpin(self, name='min',
            value=minval,
            min_val=minval,
            max_val=maxval,
            increment = spin_incr,
            digits = 3
            )

        self.minspin.SetFormat("%e")

        self.colorwidgetlist.append(self.minspin)


        self.maxspin_label = wx.StaticText(self, wx.ID_ANY,
            "Color max: ")

        self.colorwidgetlist.append(self.maxspin_label)

        self.maxspin = FloatSpin(self, name='max',
            value=maxval,
            min_val=minval,
            max_val=maxval,
            increment = spin_incr,
            digits = 3)

        self.colorwidgetlist.append(self.maxspin)



        self.maxspin.SetFormat("%e")

        self.Bind(EVT_FLOATSPIN, self.on_floatspin)


        #
        # Layout with box sizers
        #

        self.mainbox = wx.BoxSizer(wx.HORIZONTAL)



        self.middlevbox = wx.BoxSizer(wx.VERTICAL)

        self.colormapbox = wx.BoxSizer(wx.HORIZONTAL)

        self.colormapbox.Add(self.colormapselect_label, 0,wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL,border=10)
        self.colormapbox.Add(self.colormapselect,0,wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

        self.middlevbox.Add(self.colormapbox,0,wx.ALIGN_RIGHT)
        self.middlevbox.Add(wx.StaticLine(self,wx.ID_ANY),1,wx.EXPAND)
        self.middlevbox.AddSpacer(10)


        self.gridflags = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND
        self.flags = wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL

        self.ColorGridSizer = wx.GridBagSizer(hgap=5, vgap=10)

        self.ColorGridSizer.Add(self.widthspin_label,pos=(0,0),flag=self.gridflags)
        self.ColorGridSizer.Add(self.widthspin,pos=(0,1),flag=self.gridflags)
        self.ColorGridSizer.Add(self.widthslider,pos=(0,2),span=(1,2),flag=self.gridflags)

        self.ColorGridSizer.Add(self.centrespin_label,pos=(1,0),flag=self.gridflags)
        self.ColorGridSizer.Add(self.centrespin,pos=(1,1),flag=self.gridflags)
        self.ColorGridSizer.Add(self.centreslider,pos=(1,2),span=(1,2),flag=self.gridflags)

        self.ColorGridSizer.Add(self.minspin_label,pos=(2,0),flag=self.gridflags)
        self.ColorGridSizer.Add(self.minspin,pos=(2,1),flag=self.gridflags)
        self.ColorGridSizer.Add(self.maxspin_label,pos=(2,2),flag=self.gridflags)
        self.ColorGridSizer.Add(self.maxspin,pos=(2,3),flag=self.gridflags)

        self.ColorGridSizer.AddGrowableCol(0,3)
        self.ColorGridSizer.AddGrowableCol(1,3)


        self.middlevbox.Add(self.ColorGridSizer, 0, flag = wx.ALIGN_RIGHT | wx.TOP)

        self.ModBox = wx.StaticBox(self, wx.ID_ANY, 'Image Modification')
        self.ModBoxSizer = wx.StaticBoxSizer(self.ModBox, wx.VERTICAL)


        self.middlevbox.Add(self.ModBoxSizer,0)

        self.mainbox.Add((10,10))
        self.mainbox.Add(self.middlevbox,0, flag = wx.ALIGN_RIGHT)
        self.mainbox.Add((10,10))

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)


#        self.parent.PlotFrame.PlotPanel.draw_plot()



    def handle_add_modwidgets(self,sender):
        # And finally we add all the modification plugins

        try:
            for mod in view.State.modlist[:-1]:
                self.ModBoxSizer.Add(mod.create_widget(self), 0, flag = wx.ALIGN_LEFT | wx.TOP | wx.BOTTOM, border=5)
                self.ModBoxSizer.Add(wx.StaticLine(self),0,wx.EXPAND)
            self.ModBoxSizer.Add(view.State.modlist[-1].create_widget(self), 0, flag = wx.ALIGN_LEFT | wx.TOP | wx.BOTTOM,border=5)
        except IndexError:
            logging.warning('No plugins found!')

        self.SetSizerAndFit(self.mainbox)
        self.mainbox.Fit(self)


        
    def handle_update_colorctrl(self, sender):
        """
        Initialize the controls for the colorbar according to the datafile.
        """

        # See if we have colorbar information in the config file.
        # If the config parameter does not fit within the range,
        # we reset to Zmin and Zmax default values
        try:
            maxval_config = float(view.State.config['Cbmax'])
            if maxval_config > view.State.datafile.Zmax:
                raise ValueError('The maximum value in the config ({}) is larger than Zmax ({}).'.format(maxval_config,view.State.datafile.Zmax))
        except (KeyError,ValueError) as e:
            maxval_config = view.State.datafile.Zmax
            view.State.config['Cbmax'] = maxval_config
            logging.info('Using default color range.')

        try:
            minval_config = float(view.State.config['Cbmin'])
            if minval_config < view.State.datafile.Zmin:
                raise ValueError('The minimum value in the config ({}) is smaller than Zmin ({}).'.format(minval_config,view.State.datafile.Zmin))
        except (KeyError,ValueError) as e:
            minval_config = view.State.datafile.Zmin
            view.State.config['Cbmin'] = minval_config
            logging.info('Using default color range.')

            
        maxval = view.State.datafile.Zmax
        minval = view.State.datafile.Zmin

        
        spin_increment = (maxval-minval)/self.spin_divider
        slide_increment = (maxval-minval)/self.slide_divider

        # print "max {} min {} increment {} centre {} width {}".format(maxval,minval,slide_increment,(maxval+minval)/2, maxval-minval)

        # We really have to replace this widget in order to avoid a race 
        # condition when using slider.set_range and slider.set_res

        # self.ColorGridSizer.Remove(self.widthslider)
        # self.ColorGridSizer.Remove(self.centreslider)

        self.ColorGridSizer.Hide(self.widthslider)
        self.ColorGridSizer.Hide(self.centreslider)
        self.ColorGridSizer.Detach(self.widthslider)
        self.ColorGridSizer.Detach(self.centreslider)

        centreslider_value = (maxval_config + minval_config)/2
        widthslider_value = maxval_config - minval_config
        
        self.centreslider = FloatSlider(self,wx.ID_ANY,
                                        centreslider_value, minval,maxval, slide_increment,
                                        size = (200,15),
                                        name = 'centreslider')
        self.widthslider = FloatSlider(self,wx.ID_ANY,
                                       widthslider_value, 0, maxval-minval, slide_increment,
                                       size = (200,15),
                                       name = 'widthslider')

        
        self.ColorGridSizer.Add(self.widthslider,pos=(0,2),span=(1,2),flag=self.gridflags)
        self.ColorGridSizer.Add(self.centreslider,pos=(1,2),span=(1,2),flag=self.gridflags)
        self.Bind(wx.EVT_SCROLL,self.on_scroll,self.centreslider)
        self.Bind(wx.EVT_SCROLL,self.on_scroll,self.widthslider)

        self.Layout()


        self.centrespin.SetRange(minval,maxval)
        self.widthspin.SetRange(0,maxval-minval+spin_increment)
        self.minspin.SetRange(minval,maxval)
        self.maxspin.SetRange(minval,maxval)
        
        self.centrespin.SetValue(centreslider_value)
        self.widthspin.SetValue(widthslider_value)
        self.maxspin.SetValue(maxval_config)
        self.minspin.SetValue(minval_config)

        #self.widthslider.SetValue(maxval-minval)
        #self.centreslider.SetValue((minval+maxval)/2)

        self.centrespin.SetIncrement(spin_increment)
        self.widthspin.SetIncrement(spin_increment)
        self.minspin.SetIncrement(spin_increment)
        self.maxspin.SetIncrement(spin_increment)

        self.colormapselect.SetStringSelection(view.State.config['Colormap'])

        dispatcher.send(signal.PLOT_UPDATE_COLOR,self)
        


    def on_colormapselect(self,event):
        """
        Applies a colormap selected in the dropdown menu.
        """
        
        colormap = str(self.colormapselect.GetValue())
        view.State.config['Colormap'] = colormap

        dispatcher.send(signal.PLOT_CHANGE_COLORMAP,self)

    def on_scroll(self,event):
        """
        Handles events sent by the slider objects in the panel.

        The values in the FloatSpin controls are updated and the event is passed
        through to on_floatspin.
        """

        evt_obj = event.GetEventObject()

        if evt_obj.GetName() == 'widthslider':
            width = self.widthslider.GetValue()
            self.widthspin.SetValue(width)
            event.SetEventObject(self.widthspin)
            self.on_floatspin(event)
        else:
            centre = self.centreslider.GetValue()
            self.centrespin.SetValue(centre)
            event.SetEventObject(self.centrespin)
            self.on_floatspin(event)



    def on_floatspin(self, event):
        """
        Handles events sent by one of the FloatSpin controls in the panel.

        The values in the controls are not independent, e.g. the width depends on
        maximum and minimum etc.
        The plot is updated with the new colorscale.
        """
        evt_obj = event.GetEventObject()

        centre = self.centrespin.GetValue()
        width = self.widthspin.GetValue()
        minval = self.minspin.GetValue()
        maxval = self.maxspin.GetValue()


        minval = centre-width/2.
        maxval = centre+width/2.

        if evt_obj.GetName() == 'min':
            minval = self.minspin.GetValue()
            centre = (maxval+minval)/2.
            width = maxval-minval
        if evt_obj.GetName() == 'max':
            maxval = self.maxspin.GetValue()
            centre = (maxval+minval)/2.
            width = maxval-minval

        self.centrespin.SetValue(centre)
        self.widthspin.SetValue(width)
        self.minspin.SetValue(minval)
        self.maxspin.SetValue(maxval)

        self.centreslider.SetValue(centre)
        self.widthslider.SetValue(width)

        view.State.config['Cbmax'] = maxval
        view.State.config['Cbmin'] = minval
        #print "Spinning: min {} max {}".format(minval,maxval)

        dispatcher.send(signal.PLOT_UPDATE_COLOR, self)

