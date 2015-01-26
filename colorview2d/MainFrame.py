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

from FloatValidator import FloatValidator
import Utils
import yaml
import logging
import warnings


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
        
        Create Menu, MainPanel and PlotFrame.
        """
        wx.Frame.__init__(self, None, wx.ID_ANY, size=(430,360),style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent

        # The name of the default config file is hard coded.
        # We first initialize the cv2dpath to point to the correct config file
        
        if cv2dpath:
            cfgpath = os.path.join(os.getcwd(),cv2dpath)
            datafilename = None
            columns = None
        else:
            cfgpath = Utils.resource_path('default.cv2d')
            
        # The config file is parsed, modlist is a local variable that then given to the view
            
        self.config,modlist = self.parse_config(cfgpath)

        # If a datafilename is specified, we use this instead of the default
        # Same for the the columns
        
        if datafilename:
            self.config['datafilename'] = datafilename
            if columns:
                self.config['datafilecolumns'] = Utils.read_columns(columns)

        # The path to the datafile, either in the cwd or in the lib (default)
    
        data_filepath = os.path.join(os.path.dirname(cfgpath),self.config['datafilename'])

        # We select the default matplotlib font
        
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

        self.view.set_list(modlist)

        self.PlotFrame.Show()
        self.PlotFrame.Layout()


    def alignToBottomRight(self):
        """
        Used to align the Main Window to the bottom right of the screen.
        """
        dw, dh = wx.DisplaySize()
        w, h = self.GetSize()
        x = dw - w
        y = dh-2*h
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
        import toolbox
        
        with open(cfgpath) as file:
            doclist = yaml.load_all(file)
            config = doclist.next()
            modlist = [mod for mod in doclist]
            logging.info('Modlist found: {}'.format(modlist))

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

        m_rotatecw = menu_axes.Append(wx.ID_ANY, "Rotate cw", "Permutate the axes clockwise: x to y")
        self.Bind(wx.EVT_MENU, self.on_rotatecw, m_rotatecw)
        m_rotateccw = menu_axes.Append(wx.ID_ANY, "Rotate ccw", "Permutate the axes counter-clockwise: y to x")
        self.Bind(wx.EVT_MENU, self.on_rotateccw, m_rotateccw)

        m_cropaxes = menu_axes.Append(wx.ID_ANY, "Crop", "Crop x/y axes")
        self.Bind(wx.EVT_MENU, self.on_cropaxes, m_cropaxes)

        m_linecut = menu_tools.Append(wx.ID_ANY,  "Linecut &Extraction\tCtrl-E", "Extract linecut series")
        self.Bind(wx.EVT_MENU, self.on_linecut, m_linecut)

        m_slopex = menu_tools.Append(wx.ID_ANY,  "Sl&ope Extraction\tCtrl-O", "Extract linear slope")
        self.Bind(wx.EVT_MENU, self.on_slopex, m_slopex)

        m_lineout = menu_tools.Append(wx.ID_ANY,  "Linecut &Viewer\tCtrl-V", "Plot data along line")
        self.Bind(wx.EVT_MENU, self.on_lineout, m_lineout)

        m_binaryfit = menu_tools.Append(wx.ID_ANY, "Segment and Fit (beta!)", "Fit to prominent data features")
        self.Bind(wx.EVT_MENU,self.on_binaryfit,m_binaryfit)


        menu_help = wx.Menu()
        m_about = menu_help.Append(wx.ID_ANY, "&About\tF1", "About the demo")
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

    def on_rotatecw(self,event):
        """
        Rotate the datafile and the connected plot clockwise by 90 degrees.
        
        The original datafile is also replaced.
        To restore the original datafile, the file has to be rotated counter clockwise
        or reloaded.
        """
        
        #self.view.reset()
        self.view.rotate_cw()
        #self.view.notify()

    def on_rotateccw(self,event):
        """
        Rotate the datafile counter clockwise.
        """

        #self.view.reset()
        self.view.rotate_ccw()
        #self.view.notify()

    def on_cropaxes(self,event):
        """
        Creates and shows the Crop Frame.

        This frame thus only lives as long as it is shown.
        """
        self.CropFrame = CropFrame(self)
        self.CropFrame.Show()

    def on_lineout(self,event):
        """
        Shows the Frame to extract linecuts.
        
        """
        #self.PlotFrame.PlotPanel.axes.autoscale(False)
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
        # self.SlopeExFrame.Layout()



    def on_save_datafile(self, event):
        """
        Saves the datafile in gnuplot format.

        The datafile is saved with information
        on the currently applied modifications and their parameters.
        There is no information on cropping or rotating saved.
        """
        file_choices = "DAT (*.dat)|*.dat"

        modlist = ', '.join([mod.title() for mod in self.view.modlist])


        comment = """\
# Original filename: {}
#
# data modifications: {}
#
# axes: {} | {} | {}
""".format(self.config['datafilename'],modlist,self.Xlabel,self.Ylabel,self.Cblabel)

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
            plt.savefig(path)

    def on_save_cv2d(self, event):
        """
        Saves the plot in cv2d config format.

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

                yaml.dump(self.config,stream,explicit_start=True)

                stream.write(self.view.dump_list())
                

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
         * Save png files.
         * Extract series of linetraces.
         * Extract linear slopes by drawing lines in the plot.
         * Apply derivation or lowpass filtering to your data.
        """
        dlg = wx.MessageDialog(self, msg, "About", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()


    def on_load_cv2d(self,event):
        
        file_choices = "CV2D (*.cv2d)|*.cv2d"

        dlg = wx.FileDialog(self,
            message="Load cv2d config file...",
            defaultDir=os.getcwd(),
            wildcard=file_choices,
            style=wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dirname = os.path.dirname(path)
            with open(path) as stream:
                doclist = yaml.load_all(stream)
                self.config = doclist.next()
                #import pdb;pdb.set_trace()
                
                self.view.set_datafile(gpfile.gpfile(os.path.join(dirname,self.config['datafilename']),self.config['datafilecolumns']))
                self.PlotFrame.PlotPanel.draw_plot()
                self.view.set_list([mod for mod in doclist])


            self.SetTitle(self.title+self.view.datafile.filename)
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
            dlg = wx.TextEntryDialog(self, 'Enter the column numbers for the 3d data in the form (a,b,c)','Columns:')
            dlg.SetValue("{},{},{}".format(columns[0],columns[1],columns[2]))
            if dlg.ShowModal() == wx.ID_OK:
                columns = Utils.read_columns(dlg.GetValue())
                dlg.Destroy()

            # We set the new datafile in the view
            # By changing the datafile, the view notifies its observers
            # and the plot is updated
            self.view.set_datafile(gpfile.gpfile(path,columns))

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

        self.spin_divider = 10000
        self.slide_divider = 1000
        
        # self.create_panel()

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


        self.middlevbox.Add(self.ColorGridSizer, 0, flag = wx.ALIGN_CENTER | wx.TOP)

        self.ModBox = wx.StaticBox(self, wx.ID_ANY, 'Image Modification')
        self.ModBoxSizer = wx.StaticBoxSizer(self.ModBox, wx.VERTICAL)
        

        self.middlevbox.AddSpacer(10)
        self.ModBoxSizer.Add(self.smooth_widget(), 0, flag = wx.ALIGN_LEFT | wx.TOP)
        self.ModBoxSizer.AddSpacer(10)
        self.ModBoxSizer.Add(self.median_widget(), 0, flag = wx.ALIGN_LEFT | wx.TOP)
        self.ModBoxSizer.AddSpacer(10)
        self.ModBoxSizer.Add(self.derive_widget(), 0, flag = wx.ALIGN_LEFT | wx.TOP)
        self.ModBoxSizer.AddSpacer(10)
        self.ModBoxSizer.Add(self.scale_widget(), 0, flag = wx.ALIGN_LEFT | wx.TOP)

        self.middlevbox.Add(self.ModBoxSizer,0)

        self.mainbox.Add((10,10))
        self.mainbox.Add(self.middlevbox,0, flag = wx.ALIGN_RIGHT)
        self.mainbox.Add((10,10))

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)


#        self.parent.PlotFrame.PlotPanel.draw_plot()

        self.SetSizerAndFit(self.mainbox)
        self.mainbox.Fit(self)

    def derive_widget(self):
        # The box with derive

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.chk_deriv = wx.CheckBox(self, wx.ID_ANY, 'Derive')
        hbox.Add(self.chk_deriv,0,self.flags,border=10)

        self.Bind(wx.EVT_CHECKBOX,self.on_chk_deriv,self.chk_deriv)        

        return hbox

    def scale_widget(self):
        # The box with scale
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.chk_scale =  wx.CheckBox(self, wx.ID_ANY, 'Scale')
        self.num_scale = wx.TextCtrl(self,-1,"",validator = FloatValidator('1e0'))
        self.auto_scale_button = wx.Button(self,wx.ID_ANY,'dI/dV')        

        hbox.Add(self.chk_scale,0,self.flags,border=10)
        hbox.Add(self.num_scale,0,self.flags,border=10)
        hbox.Add(self.auto_scale_button,0,self.flags,border=10)

        self.Bind(wx.EVT_CHECKBOX,self.on_chk_scale,self.chk_scale)
        self.Bind(wx.EVT_BUTTON,self.on_auto_scale_button,self.auto_scale_button)

        return hbox
        
    def smooth_widget(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.chk_smooth =  wx.CheckBox(self, wx.ID_ANY, 'Smooth')
        self.num_smooth_xwidth = NumCtrl(self,
                                          fractionWidth = 1,
                                          allowNegative = False)
        self.num_smooth_ywidth = NumCtrl(self,
                                          fractionWidth = 1,
                                          allowNegative = False)

        hbox.Add(self.chk_smooth,0,self.flags,border=10)
        hbox.Add(self.num_smooth_xwidth,0,self.flags,border=10)
        hbox.Add(self.num_smooth_ywidth,0,self.flags,border=10)

        self.Bind(wx.EVT_CHECKBOX,self.on_chk_smooth,self.chk_smooth)
        self.Bind(EVT_NUM,self.on_num_smooth,self.num_smooth_ywidth)
        self.Bind(EVT_NUM,self.on_num_smooth,self.num_smooth_xwidth)

        return hbox

    def median_widget(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.chk_median =  wx.CheckBox(self, wx.ID_ANY, 'Median')
        self.num_median_xwidth = NumCtrl(self,
                                          fractionWidth = 1,
                                          allowNegative = False)
        self.num_median_ywidth = NumCtrl(self,
                                          fractionWidth = 1,
                                          allowNegative = False)

        hbox.Add(self.chk_median,0,self.flags,border=10)
        hbox.Add(self.num_median_xwidth,0,self.flags,border=10)
        hbox.Add(self.num_median_ywidth,0,self.flags,border=10)

        self.Bind(wx.EVT_CHECKBOX,self.on_chk_median,self.chk_median)
        self.Bind(EVT_NUM,self.on_num_median,self.num_median_ywidth)
        self.Bind(EVT_NUM,self.on_num_median,self.num_median_xwidth)

        return hbox
        
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

        # Tell plot panel to update plot

        self.chk_deriv.SetValue(subject.hasMod('deriv'))
        self.chk_scale.SetValue(subject.hasMod('scale'))
            
        self.chk_smooth.SetValue(subject.hasMod('smooth'))
        self.chk_median.SetValue(subject.hasMod('median'))

        self.notify()


    def on_chk_scale(self,event):
        """
        Scales the datafile's z-axis.

        Bound to the scale checkbox. The value is provided by a text ctrl.
        """
        if self.chk_scale.GetValue():
            self.Validate()
            self.parent.view.addMod(toolbox.scale(float(self.num_scale.GetValue())))
        else:
            self.parent.view.remMod("scale")

    def on_auto_scale_button(self,event):
        self.num_scale.SetValue(str(2.5812e4/self.parent.view.datafile.dY))        


    def on_colormapselect(self,event):
        """
        Applies a colormap selected in the dropdown menu.
        """
        
        self.parent.config['Colormap'] = self.colormapselect.GetValue()
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




    def on_chk_deriv(self,event):
        """
        Derives the datafile (z-axis) with respect to the y-axis.

        Bound to the deriv checkbox.
        """
        if self.chk_deriv.GetValue():
            self.parent.view.addMod(toolbox.deriv())

        else:
            self.parent.view.remMod("deriv")


    def on_chk_smooth(self,event):
        """
        Applies a lowpass filter to the data in the datafile (z-axis).

        Bound to the lowpass checkbox. The parameters for the filtering are
        provided by the num_smooth controls.
        """
        if self.chk_smooth.GetValue():
            self.parent.view.addMod(toolbox.smooth(self.num_smooth_xwidth.GetValue(),self.num_smooth_ywidth.GetValue()))
        else:
            self.parent.view.remMod("smooth")


    def on_num_smooth(self,event):
        """
        Applies a lowpass filter with new parameters given the lowpass box is checked.
        """
        if self.chk_smooth.GetValue():
            self.parent.view.remMod("smooth")
            self.parent.view.addMod(toolbox.smooth(self.num_smooth_xwidth.GetValue(),self.num_smooth_ywidth.GetValue()))

    def on_chk_median(self,event):
        """
        Applies a median filter to the data in the datafile (z-axis).

        Bound to the median checkbox. The parameters for the filtering are
        provided by the num_median controls.
        """
        if self.chk_median.GetValue():
            self.parent.view.addMod(toolbox.median(self.num_median_xwidth.GetValue(),self.num_median_ywidth.GetValue()))
        else:
            self.parent.view.remMod("median")


    def on_num_median(self,event):
        """
        Applies a median filter with new parameters given the median box is checked.
        """
        if self.chk_median.GetValue():
            self.parent.view.remMod("median")
            self.parent.view.addMod(toolbox.median(self.num_median_xwidth.GetValue(),self.num_median_ywidth.GetValue()))



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


        ## if evt_obj.GetName() == 'width':
        ##     if centre-width/2. < minval:
        ##         centre = minval + width/2.
        ##     if centre+width/2. > maxval:
        ##         centre = maxval - width/2.
        ## if evt_obj.GetName() == 'centre':
        ##     if centre-width/2. < minval:
        ##         width = (centre - minval)*2.
        ##     if centre+width/2. > maxval:
        ##         width = (maxval - centre)*2.

        minval = centre-width/2.
        maxval = centre+width/2.

        if evt_obj.GetName() == 'min':
            minval = self.minspin.GetValue()
            if minval < centre - width/2.:
                centre = minval + width/2.
                maxval = centre + width/2.
            if minval > centre - width/2.:
                width = 2*(centre-minval)
                maxval = minval + width
        if evt_obj.GetName() == 'max':
            maxval = self.maxspin.GetValue()
            if maxval > centre + width/2.:
                centre = maxval-width/2.
                minval = centre-width/2.
            if maxval < centre + width/2.:
                width = 2*(maxval-centre)
                minval = maxval - width
                

        self.centrespin.SetValue(centre)
        self.widthspin.SetValue(width)
        self.minspin.SetValue(minval)
        self.maxspin.SetValue(maxval)

        self.centreslider.SetValue(centre)
        self.widthslider.SetValue(width)

        self.notify()

