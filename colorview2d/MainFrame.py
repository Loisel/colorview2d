import wx
import numpy as np
import re
import os
import gpfile

import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties,findfont

from matplotlib.pyplot import cm
from floatspin import FloatSpin,EVT_FLOATSPIN
from floatslider import FloatSlider

from wx.lib.masked import NumCtrl,EVT_NUM

import toolbox
from View import View
from Subject import Subject

from PlotFrame import PlotFrame
from LineoutFrame import LineoutFrame
from LinecutFrame import LinecutFrame
from CropFrame import CropFrame
from SlopeExFrame import SlopeExFrame
# Experimental feature
# from BinaryFitFrame import BinaryFitFrame
from LabelticksFrame import LabelticksFrame

import Utils
import yaml
import logging
import warnings


"""
The MainFrame module hostst the MainFrame class and the MainPanel class.
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
            # Utils.resource_path adds the path to the 
            # library in win and linux
            cfgpath = Utils.resource_path('default.cv2d')
            
        # The config file is parsed, 
        # modlist is a string variable that is given to the view
        # to create the mod pipeline
        self.config,modlist = self.parse_config(cfgpath)

        # If a datafilename is specified, we use this instead of the default
        # Same for the the columns        
        if datafilename:
            self.config['datafilename'] = datafilename
            data_filepath = os.path.join(os.getcwd(),self.config['datafilename'])
            if columns:
                self.config['datafilecolumns'] = Utils.read_columns(columns)
        else:
            # The path to the datafile, either in the cwd or in the lib (default)
            # We assume that the datafile is in the same dir as the cv2d dile
            data_filepath = os.path.join(os.path.dirname(cfgpath),self.config['datafilename'])

            
        # We select the default matplotlib font
        # To that end we catch the warning -- not particularly elegant
        if self.config['Font'] == 'default':
            for font in plt.rcParams['font.sans-serif']:
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    findfont(FontProperties(family=font))
                    if len(w):
                        continue
                    else:
                        self.config['Font'] = font
                        break

        # Set title for the frame and align
        self.SetTitle(self.title+self.config['datafilename'])
        self.alignToBottomRight()

        # Create menu and status bar
        self.create_menu()
        self.create_status_bar()

        # The plot frame is created first with a dummy plot
        self.PlotFrame = PlotFrame(self)

        # The MainPanel contains all the colorbar controls
        # The PlotPanel listens to the MainPanel for changes (e.g. to the colorbar)
        self.MainPanel = MainPanel(self)
        self.MainPanel.attach(self.PlotFrame.PlotPanel)

        # The frame with the settings (font, ticks, labels, etc)
        self.LabelticksFrame = LabelticksFrame(self)

        # The view is created and signals the PlotPanel and the MainPanel
        # upon changes to the modlist and the datafile
        self.view = View(gpfile.gpfile(data_filepath,self.config['datafilecolumns']))
        self.view.attach(self.PlotFrame.PlotPanel)
        self.view.attach(self.MainPanel)

        # We have to draw the plot first before we can apply the modlist
        self.PlotFrame.PlotPanel.draw_plot()

        # The other tools are intialized
        self.LinecutFrame = LinecutFrame(self)
        self.LineoutFrame = LineoutFrame(self)
        self.SlopeExFrame = SlopeExFrame(self)

        # BinaryFitFrame and the MainPanel creation require a view to exist
        self.MainPanel.create_panel()

        # We apply the modlist to the view. We can not do that earlier, because all the
        # plot infrastructure has to be there.
        # set_list notifies the PlotPanel

        self.view.load_pipeline_string(modlist)

        self.PlotFrame.Show()
        self.PlotFrame.Layout()


    def alignToBottomRight(self):
        """
        Used to align the Main Window to the bottom right of the screen.
        """
        dw, dh = wx.DisplaySize()
        w, h = self.GetSize()
        x = dw -w
        y = dh-1.5*h
        self.SetPosition((x, y))

    def parse_config(self,cfgpath):
        """
        Load the configuration and the modlist from the config file
        specified in the YAML format.

        Returns:
          config (dict): A configuration dict.
          modlist (list): A list of modification objects from the toolbox
                          module
        """
        
        with open(cfgpath) as file:
            doclist = yaml.load_all(file)
            # The config dict is the first yaml document
            config = doclist.next()
            # The pipeline string is the second. It is optional.
            try:
                modlist = doclist.next()
            except StopIteration:
                modlist = '[]'
            logging.info('Pipeline string found: {}'.format(modlist))

            return config,modlist

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

        m_binaryfit = menu_tools.Append(wx.ID_ANY, "Segment and Fit (beta!)", "Fit to prominent data features")
        self.Bind(wx.EVT_MENU,self.on_binaryfit,m_binaryfit)


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
        self.PlotFrame.PlotPanel.axes.autoscale(False)
        self.LinecutFrame.Show()

    def on_slopex(self,event):
        """
        Shows the Frame to extract slopes.

        """
        self.SlopeExFrame.Show()


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
""".format(self.config['datafilename'],self.view.pipeline,self.Xlabel,self.Ylabel,self.Cblabel)

        dlg = wx.FileDialog(
            self,
            message="Save plot data as...",
            defaultDir=os.getcwd(),
            defaultFile=self.config['datafilename'],
            wildcard=file_choices,
            style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.view.datafile.save(path,comment)


    def on_save_pdf(self, event):
        """
        Saves the plot in pdf format.

        """
        file_choices = "PDF (*.pdf)|*.pdf"
        defaultfilename = os.path.splitext(self.config['datafilename'])[0]+'.pdf'

        dlg = wx.FileDialog(
            self,
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile=defaultfilename,
            wildcard=file_choices,
            style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.PlotFrame.PlotPanel.fig.savefig(path)

    def on_save_cv2d(self, event):
        """
        Saves a cv2d config file.

        """
        file_choices = "CV2D (*.cv2d)|*.cv2d"
        defaultfilename = os.path.splitext(self.config['datafilename'])[0]+'.cv2d'

        dlg = wx.FileDialog(
            self,
            message="Save config as...",
            defaultDir=os.getcwd(),
            defaultFile=defaultfilename,
            wildcard=file_choices,
            style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            with open(path,'w') as stream:
                # We write first the config dict
                yaml.dump(self.config,stream,explicit_start=True)
                # ... and second the pipeline string
                yaml.dump(self.view.dump_pipeline_string(),stream,explicit_start=True)
                

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
            self.config, modliststring = self.parse_config(path)
            # The datafile is replaced
            self.view.set_datafile(gpfile.gpfile(os.path.join(dirname,self.config['datafilename']),self.config['datafilecolumns']))
            self.PlotFrame.PlotPanel.draw_plot()
            # ... and the pipeline is applied
            self.view.load_pipeline_string(modliststring)

            # We make sure the title is correct
            self.SetTitle(self.title+self.view.datafile.filename)
            # The slope extraction utility has to know about the correct dimensions
            # of the datafile (the FloatSpin tools need the x/y range)
            self.SlopeExFrame.SlopeExPanel.update()
                
        
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

            dlg = Utils.SettingsDialog(self)
            if dlg.ShowModal() == wx.ID_OK:
                columns = dlg.GetColumns()
                reset_settings = dlg.GetSettingChk()
                dlg.Destroy()

            # We set the new datafile in the view
            # By changing the datafile, the view notifies its observers
            # and the plot is updated
            self.view.set_datafile(gpfile.gpfile(path,columns))
            self.PlotFrame.PlotPanel.draw_plot()

            if reset_settings:
                cfgpath = Utils.resource_path('default.cv2d')
                self.config,pipelinestring = self.parse_config(cfgpath)
                self.view.reset()

                
            self.config['datafilename'] = os.path.basename(path)

            self.SetTitle(self.title+self.view.datafile.filename)
            self.SlopeExFrame.SlopeExPanel.update()
            
class MainPanel(Subject,wx.Panel):
    """
    Panel with colorbar controls and checkboxes for the plot modifications.
    """
    def __init__(self, parent):
        Subject.__init__(self)
        wx.Panel.__init__(self, parent)
        self.parent = parent
        
        # Magic numbers for the "fine-graindedness" of the FloatSpin and FloatSlider objects
        self.spin_divider = 10000
        self.slide_divider = 1000
        

    def create_panel(self):
        """
        Create, show and layout all widgets in the panel.
        """
        
        self.colorwidgetlist = []

        view  = self.parent.view
        
        maxval = view.datafile.Zmax
        minval = view.datafile.Zmin

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

        self.colormapselect.SetStringSelection(self.parent.config['Colormap'])

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

        self.SetSizerAndFit(self.mainbox)
        self.mainbox.Fit(self)

        # And finally we add all the modification plugins

        try:
            for mod in self.parent.view.modlist[:-1]:
                self.ModBoxSizer.Add(mod.create_widget(self), 0, flag = wx.ALIGN_LEFT | wx.TOP | wx.BOTTOM, border=5)
                self.ModBoxSizer.Add(wx.StaticLine(self),0,wx.EXPAND)
            self.ModBoxSizer.Add(self.parent.view.modlist[-1].create_widget(self), 0, flag = wx.ALIGN_LEFT | wx.TOP | wx.BOTTOM,border=5)
        except IndexError:
            logging.warning('No plugins found!')


        
    def update(self,subject):
        """
        Initialize the controls for the colorbar according to the datafile.
        """
        
        maxval = subject.datafile.get_Zmax()
        minval = subject.datafile.get_Zmin()
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

        # self.ColorGridSizer.Hide(2)
        # self.ColorGridSizer.Hide(5)
        # self.ColorGridSizer.Remove(2)
        # self.ColorGridSizer.Remove(5)

        
        self.centreslider = FloatSlider(self,wx.ID_ANY,(maxval+minval)/2,minval,maxval,slide_increment,
                                    size = (200,15),
                                    name = 'centreslider')
        self.widthslider = FloatSlider(self,wx.ID_ANY,maxval-minval,0,maxval-minval,slide_increment,
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
        
        self.centrespin.SetValue((maxval+minval)/2.)
        self.widthspin.SetValue(maxval-minval)
        self.maxspin.SetValue(maxval)
        self.minspin.SetValue(minval)

        #self.widthslider.SetValue(maxval-minval)
        #self.centreslider.SetValue((minval+maxval)/2)

        self.centrespin.SetIncrement(spin_increment)
        self.widthspin.SetIncrement(spin_increment)
        self.minspin.SetIncrement(spin_increment)
        self.maxspin.SetIncrement(spin_increment)

        self.colormapselect.SetStringSelection(self.parent.config['Colormap'])

        self.notify()


        


    def on_colormapselect(self,event):
        """
        Applies a colormap selected in the dropdown menu.
        """
        
        self.parent.config['Colormap'] = str(self.colormapselect.GetValue())
        self.notify()

    def on_scroll(self,event):
        """
        Handles events sent by the slider objects in the panel.

        The values in the floatspin controls are updated and the event is passed
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
        Handles events sent by one of the floatspin controls in the panel.

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
            width = waxval-minval
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

        self.notify()

