#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
colorview2d
~~~~~~~~~~~

A GUI driven application to visualize and analyze 3D
datasets. Available tools include linear slope extraction,
linecut series extraction and fitting of (almost) arbitrary 2d
functions to prominent features in the 3d dataset.

:copyright: 2014 by Alois Dirnaichner, see AUTHORS for more details
:license: GPLv3, see LICENSE for more details
"""

import wx
import gpfile
import copy
import os
import sys
import numpy as np
import re
import matplotlib
matplotlib.use('WXAgg')

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import wx.lib.mixins.listctrl as listmix
from wx.lib.agw.floatspin import FloatSpin,EVT_FLOATSPIN
from wx.lib.masked import NumCtrl,EVT_NUM
from FloatSlider import FloatSlider

from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar

from matplotlib.ticker import FormatStrFormatter

import parser
import toolbox as tb


class Modlist():
    """
    A container for data manipulation objects (mods).
    It is associated with the parent frame and
    calls a function (restore_datafile) of the frame object.
    """
    
    modlist = []
    def __init__(self,frame):
        """ Initialization requires the parent frame object """
        self.frame = frame

    def addMod(self,mod):
        """ Adds a modification object to the list """
        #print "Try to add {}".format(mod)
        if not any(mymod.title == mod.title for mymod in self.modlist):
            self.modlist.append(mod)

    def remMod(self,title):
        """
        Removes a modification object from the list using a
        strin identifier.

        Keyword arguments:
        title -- string specifying the modification
        """
        
        for mod in self.modlist:
            if mod.title == title:
                self.modlist.remove(mod)

    def applyModlist(self):
        """
        Applies the modlist to the frames datafile.
        The datafile is first reverted to its original state,
        then mods are applied in the order they were added.
        """
        self.frame.restore_datafile()
        #print "Modlist {}".format(self.modlist)
        for mod in self.modlist:
#            print "Applying mod {}".format(mod.title)
            mod.apply_mod(self.frame.datafile)



class MainFrame(wx.Frame):
    """
    The MainFrame class hosts all subframes, the datafile object,
    the colormap and information on ticks and labels.
    """

    title = 'colorplot utility: '
    datafilename = 'demo.dat'
    Colormap = 'jet'
    Xlabel = 'x-axis'
    Ylabel = 'y-axis'
    Cblabel = 'colorscale'

    Xtickformat = 'auto'
    Ytickformat = 'auto'
    Cbtickformat = 'auto'

    def __init__(self):
        """
        Initialize the frame and create a default datafile object.
        Create Menu, MainPanel and PlotFrame.
        """
        wx.Frame.__init__(self, None, wx.ID_ANY, self.title+self.datafilename,size=(440,330))

        self.alignToBottomRight()
        self.modlist = Modlist(self)

        self.datafile = gpfile.gpfile(self.datafilename,(0,1,2))
        self.orig_datafile = self.datafile.deep_copy()

        #self.datafile.report()

        self.create_menu()
        self.create_status_bar()

        self.PlotFrame = PlotFrame(self)

        self.MainPanel = MainPanel(self)

        self.LinecutFrame = LinecutFrame(self)
        self.LabelticksFrame = LabelticksFrame(self)

#        self.PlotFrame.PlotPanel.draw_plot()
        self.BinaryFitFrame = BinaryFitFrame(self)

        self.PlotFrame.Show()
        self.PlotFrame.Layout()
        #self.PlotFrame.Maximize()

    def alignToBottomRight(self):
        dw, dh = wx.DisplaySize()
        w, h = self.GetSize()
        x = dw - w
        y = dh-2*h
        self.SetPosition((x, y))

    def restore_datafile(self):
        self.datafile = self.orig_datafile.deep_copy()

    def create_menu(self):
        self.menubar = wx.MenuBar()
        menu_file = wx.Menu()
        menu_tools = wx.Menu()
        menu_axes = wx.Menu()

        m_load = menu_file.Append(wx.ID_ANY, "&Load Data\tCtrl-L", "Load data from file")
        self.Bind(wx.EVT_MENU, self.on_load_plot, m_load)
        m_expt = menu_file.Append(wx.ID_ANY, "&Save Data\tCtrl-S", "Save data to file")
        self.Bind(wx.EVT_MENU, self.on_save_datafile, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(wx.ID_ANY, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)

        m_labelticks = menu_axes.Append(wx.ID_ANY, "Labels and &Ticks\tCtrl-T", "Set axes labels and tick label format")
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

        m_binaryfit = menu_tools.Append(wx.ID_ANY, "Segment and Fit", "Fit to prominent data features")
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
        self.LabelticksFrame.Show()

    def on_rotatecw(self,event):
        self.restore_datafile()
        self.datafile.rotate_cw()
        self.orig_datafile = self.datafile.deep_copy()
        #self.MainPanel.update_plot()
        self.PlotFrame.PlotPanel.draw_plot()

    def on_rotateccw(self,event):
        self.restore_datafile()
        self.datafile.rotate_ccw()
        self.orig_datafile = self.datafile.deep_copy()
        #self.MainPanel.update_plot()
        self.PlotFrame.PlotPanel.draw_plot()

    def on_cropaxes(self,event):
        self.CropFrame = CropFrame(self)
        self.CropFrame.Show()

    def on_lineout(self,event):
        self.LineoutFrame = LineoutFrame(self)
        self.LineoutFrame.Show()

    def on_binaryfit(self,event):
        self.BinaryFitFrame.Show()
        self.PlotFrame.PlotPanel.axes.autoscale(False)
        if hasattr(self.BinaryFitFrame.BinaryFitPanel,'lineplot'):
            self.PlotFrame.PlotPanel.axes.add_line(self.BinaryFitFrame.BinaryFitPanel.lineplot)
        self.MainPanel.update_plot()

        self.BinaryFitFrame.MakeModal(True)

    def on_linecut(self,event):
        self.PlotFrame.PlotPanel.axes.autoscale(False)
        self.LinecutFrame.Show()

    def on_slopex(self,event):
        self.SlopeExFrame = SlopeExFrame(self)
        self.SlopeExFrame.Show()
        self.SlopeExFrame.Layout()



    def on_save_datafile(self, event):
        file_choices = "DAT (*.dat)|*.dat"

        modlist = ', '.join([mod.title for mod in self.modlist.modlist])

        comment = "# Original filename: {}\n\
#\n\
# data modifications: {}\n\
#\n\
# axes: {} | {} | {}\n".format(self.datafilename,modlist,self.Xlabel,self.Ylabel,self.Cblabel)

        dlg = wx.FileDialog(
            self,
            message="Save plot data as...",
            defaultDir=os.getcwd(),
            defaultFile=self.datafilename,
            wildcard=file_choices,
            style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.datafile.save(path,comment)

    def on_exit(self, event):
        self.Destroy()

    def on_about(self, event):
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

    def read_columns(self,string):
        p = re.compile('(\d+),(\d+),(\d+)')
        m = p.match(string)

        if m:
            column = (int(m.groups()[0]),int(m.groups()[1]),int(m.groups()[2]))
            return column
        else:
            raise InputError('Not a valid column string: {}'.format(string))

    def on_load_plot(self,event):
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
                columns = self.read_columns(dlg.GetValue())
                dlg.Destroy()

            self.datafile = gpfile.gpfile(path,columns)

            self.orig_datafile = self.datafile.deep_copy()

            self.datafilename = os.path.basename(path)
            self.SetTitle(self.title+self.datafilename)

            self.PlotFrame.PlotPanel.draw_plot()


class PlotFrame(wx.Frame):
    def __init__(self,parent):
        self.parent = parent
        wx.Frame.__init__(self, parent, title="Plotting "+parent.datafilename,size=(700,500))
        self.PlotPanel = PlotPanel(self)
        self.Layout()

class PlotPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        # Create the mpl Figure and FigCanvas objects.
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 75
        self.fig = plt.figure(1,dpi=self.dpi)

        self.draw_plot()

    def draw_plot(self):

        self.parent.parent.modlist.applyModlist()

        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        self.canvas = FigCanvas(self, wx.ID_ANY, self.fig)
        self.toolbar = NavigationToolbar(self.canvas)

        self.mainbox = wx.BoxSizer(wx.VERTICAL)
        self.mainbox.Add(self.toolbar,0)

        datafile = self.parent.parent.datafile

        #print "Max: {} Min: {}".format(datafile.Zmax,datafile.Zmin)

        self.plot = self.axes.imshow(datafile.Zdata,
            extent=[datafile.Xleft,datafile.Xright,datafile.Ybottom,datafile.Ytop],
            aspect='auto',
            interpolation="nearest")

        self.axes.set_ylabel(self.parent.parent.Ylabel)
        self.axes.set_xlabel(self.parent.parent.Xlabel)

        self.fig.tight_layout()

        self.colorbar = self.fig.colorbar(self.plot)
        self.colorbar.set_label(self.parent.parent.Cblabel)

        self.canvas.draw()

        self.mainbox.Add(self.canvas, 1,flag =  wx.EXPAND)

        if hasattr(self.parent.parent,'MainPanel'):
            #print "Call init:"
            self.parent.parent.MainPanel.init_colorspinctrls()


        self.SetSizer(self.mainbox)
        self.mainbox.Fit(self)

    def set_labelticks(self):
        self.axes.set_ylabel(self.parent.parent.Ylabel)
        self.axes.set_xlabel(self.parent.parent.Xlabel)

        self.colorbar.set_label(self.parent.parent.Cblabel)

        if not self.parent.parent.Xtickformat == 'auto':
            self.axes.xaxis.set_major_formatter(FormatStrFormatter(self.parent.parent.Xtickformat))
        if not self.parent.parent.Ytickformat == 'auto':
            self.axes.yaxis.set_major_formatter(FormatStrFormatter(self.parent.parent.Ytickformat))
        if not self.parent.parent.Cbtickformat == 'auto':
            self.colorbar.yaxis.set_major_formatter(FormatStrFormatter(self.parent.parent.Cbtickformat))
            self.colorbar.update_ticks()

class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent


        # The spins
        #

        self.colorwidgetlist = []


        maxval = self.parent.datafile.Zmax
        minval = self.parent.datafile.Zmin

        self.spin_divider = 10000
        self.slide_divider = 1000

        spin_incr = np.absolute(maxval-minval)/self.spin_divider
        slide_incr = np.absolute(maxval-minval)/self.slide_divider

        self.colormapselect_label = wx.StaticText(self, wx.ID_ANY,'Colormap')

        self.colormapselect = wx.ComboBox(self,
                                          size=wx.DefaultSize,
                                          style=wx.CB_READONLY)
        self.maps = [m for m in plt.cm.datad if not m.endswith("_r")]
        self.maps.sort()

        for m in self.maps:
            self.colormapselect.Append(m)

        self.colormapselect.SetStringSelection(self.parent.Colormap)

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


        self.chk_deriv = wx.CheckBox(self, wx.ID_ANY, 'Derive')
        self.Bind(wx.EVT_CHECKBOX,self.on_chk_deriv,self.chk_deriv)


        self.chk_lowpass =  wx.CheckBox(self, wx.ID_ANY, 'Lowpass')
        self.num_lowpass_xwidth = NumCtrl(self,
                                          fractionWidth = 1,
                                          allowNegative = False)
        self.num_lowpass_ywidth = NumCtrl(self,
                                          fractionWidth = 1,
                                          allowNegative = False)

        self.chk_scale =  wx.CheckBox(self, wx.ID_ANY, 'Scale')
        self.num_scale = wx.TextCtrl(self,-1,"",validator = FloatValidator())
        self.Bind(wx.EVT_CHECKBOX,self.on_chk_scale,self.chk_scale)


        self.Bind(wx.EVT_CHECKBOX,self.on_chk_lowpass,self.chk_lowpass)
        self.Bind(EVT_NUM,self.on_num_lowpass,self.num_lowpass_ywidth)
        self.Bind(EVT_NUM,self.on_num_lowpass,self.num_lowpass_xwidth)

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


        gridflags = wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND
        flags = wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL

        self.ColorGridSizer = wx.GridBagSizer(hgap=5, vgap=10)

        self.ColorGridSizer.Add(self.widthspin_label,pos=(0,0),flag=gridflags)
        self.ColorGridSizer.Add(self.widthspin,pos=(0,1),flag=gridflags)
        self.ColorGridSizer.Add(self.widthslider,pos=(0,2),span=(1,2),flag=gridflags)

        self.ColorGridSizer.Add(self.centrespin_label,pos=(1,0),flag=gridflags)
        self.ColorGridSizer.Add(self.centrespin,pos=(1,1),flag=gridflags)
        self.ColorGridSizer.Add(self.centreslider,pos=(1,2),span=(1,2),flag=gridflags)

        self.ColorGridSizer.Add(self.minspin_label,pos=(2,0),flag=gridflags)
        self.ColorGridSizer.Add(self.minspin,pos=(2,1),flag=gridflags)
        self.ColorGridSizer.Add(self.maxspin_label,pos=(2,2),flag=gridflags)
        self.ColorGridSizer.Add(self.maxspin,pos=(2,3),flag=gridflags)

        self.ColorGridSizer.AddGrowableCol(0,3)
        self.ColorGridSizer.AddGrowableCol(1,3)


        self.middlevbox.Add(self.ColorGridSizer, 0, flag = wx.ALIGN_CENTER | wx.TOP)

        # The box with smooth
        self.ModBox = wx.StaticBox(self, wx.ID_ANY, 'Image Modification')
        self.ModBoxSizer = wx.StaticBoxSizer(self.ModBox, wx.VERTICAL)

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.hbox3.Add(self.chk_lowpass,0,flags,border=10)
        self.hbox3.Add(self.num_lowpass_xwidth,0,flags,border=10)
        self.hbox3.Add(self.num_lowpass_ywidth,0,flags,border=10)

        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        self.hbox4.Add(self.chk_deriv,0,flags,border=10)

        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)

        self.hbox5.Add(self.chk_scale,0,flags,border=10)
        self.hbox5.Add(self.num_scale,0,flags,border=10)


        self.middlevbox.AddSpacer(10)
        self.ModBoxSizer.Add(self.hbox3, 0, flag = wx.ALIGN_LEFT | wx.TOP)
        self.ModBoxSizer.AddSpacer(10)
        self.ModBoxSizer.Add(self.hbox4, 0, flag = wx.ALIGN_LEFT | wx.TOP)
        self.ModBoxSizer.AddSpacer(10)
        self.ModBoxSizer.Add(self.hbox5, 0, flag = wx.ALIGN_LEFT | wx.TOP)

        self.middlevbox.Add(self.ModBoxSizer,0)

        self.mainbox.Add((10,10))
        self.mainbox.Add(self.middlevbox,0, flag = wx.ALIGN_RIGHT)
        self.mainbox.Add((10,10))

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)


#        self.parent.PlotFrame.PlotPanel.draw_plot()

        self.SetSizerAndFit(self.mainbox)
        self.mainbox.Fit(self)

    def init_colorspinctrls(self):
        maxval = self.parent.datafile.Zmax
        minval = self.parent.datafile.Zmin
        spin_increment = (maxval-minval)/self.spin_divider
        slide_increment = (maxval-minval)/self.slide_divider

        #print "max {} min {} increment {} centre {} width {}".format(maxval,minval,spin_increment,(maxval+minval)/2, maxval-minval)
        self.widthslider.SetRes(slide_increment)
        self.centreslider.SetRes(slide_increment)

        self.centrespin.SetRange(minval,maxval)
        self.widthspin.SetRange(0,maxval-minval+spin_increment)
        self.minspin.SetRange(minval,maxval)
        self.maxspin.SetRange(minval,maxval)

        self.widthslider.SetRange(0,maxval-minval+slide_increment)
        self.centreslider.SetRange(minval,maxval)

        self.centrespin.SetValue((maxval+minval)/2.)
        self.widthspin.SetValue(maxval-minval)
        self.maxspin.SetValue(maxval)
        self.minspin.SetValue(minval)

        self.widthslider.SetValue(maxval-minval)
        self.centreslider.SetValue((minval+maxval)/2)

        self.centrespin.SetIncrement(spin_increment)
        self.widthspin.SetIncrement(spin_increment)
        self.minspin.SetIncrement(spin_increment)
        self.maxspin.SetIncrement(spin_increment)


    def on_chk_scale(self,event):
        if self.chk_scale.GetValue():
            self.Validate()
            self.parent.modlist.addMod(tb.scale(float(self.num_scale.GetValue())))
        else:
            self.parent.modlist.remMod("scale")

        self.parent.modlist.applyModlist()

        self.init_colorspinctrls()

        self.update_plot()

    def on_colormapselect(self,event):

        self.parent.Colormap = self.colormapselect.GetValue()
        self.update_plot()

    def on_scroll(self,event):

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
        if self.chk_deriv.GetValue():
            self.parent.modlist.addMod(tb.deriv())

        else:
            self.parent.modlist.remMod("deriv")

        self.parent.modlist.applyModlist()

        self.init_colorspinctrls()

        self.update_plot()

    def on_chk_lowpass(self,event):
        if self.chk_lowpass.GetValue():
            self.parent.modlist.addMod(tb.smooth(self.num_lowpass_xwidth.GetValue(),self.num_lowpass_ywidth.GetValue()))
        else:
            self.parent.modlist.remMod("lowpass")

        self.parent.modlist.applyModlist()

        self.init_colorspinctrls()
        self.update_plot()

    def on_num_lowpass(self,event):
        if self.chk_lowpass.GetValue():
            self.parent.modlist.remMod("lowpass")
            self.parent.modlist.addMod(tb.smooth(self.num_lowpass_xwidth.GetValue(),self.num_lowpass_ywidth.GetValue()))

        self.parent.modlist.applyModlist()
        self.update_plot()



    def on_floatspin(self, event):
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
            if minval < centre - width/2.:
                centre = minval + width/2.
                maxval = centre + width/2.
            if minval > centre - width/2.:
                width = 2*(centre-minval)
                maxval = minval + width
        if evt_obj.GetName() == 'max':
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

        self.update_plot()



    def update_plot(self):
        """ Redraws the figure
        """
        width = self.widthspin.GetValue()
        centre = self.centrespin.GetValue()

        plotpanel = self.parent.PlotFrame.PlotPanel

        # clear the axes and redraw the plot anew
        #
        #self.axes.clear()

        plotpanel.plot.set_extent([self.parent.datafile.Xleft,self.parent.datafile.Xright,self.parent.datafile.Ybottom,self.parent.datafile.Ytop])

        plotpanel.axes.set_xlim(self.parent.datafile.Xleft,self.parent.datafile.Xright)
        plotpanel.axes.set_ylim(self.parent.datafile.Ybottom,self.parent.datafile.Ytop)

        plotpanel.plot.set_data(self.parent.datafile.Zdata)

        cbar_min = centre - width/2.
        cbar_max = centre + width/2.

        plotpanel.plot.set_cmap(self.parent.Colormap)
        plotpanel.plot.set_clim(cbar_min,cbar_max)

        plotpanel.plot.changed()

        #self.colorbar.update_normal(self.plot)
        plotpanel.canvas.draw()


class LabelticksFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent, title="Axes and tick labels")
        self.parent = parent
        panel = LabelticksPanel(self)
        self.Layout()

class LabelticksPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent = parent

        self.widgetlist = []

        self.xtextbox_label = wx.StaticText(self, wx.ID_ANY,
            "x-axis label: ")
        self.widgetlist.append(self.xtextbox_label)
        self.xtextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.xtextbox.SetValue(self.parent.parent.Xlabel)
        self.widgetlist.append(self.xtextbox)

        self.xformattextbox_label = wx.StaticText(self, wx.ID_ANY,
            "format: ")
        self.widgetlist.append(self.xformattextbox_label)
        self.xformattextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.xformattextbox.SetValue('auto')
        self.widgetlist.append(self.xformattextbox)


        self.ytextbox_label = wx.StaticText(self, wx.ID_ANY,
            "y-axis label: ")
        self.widgetlist.append(self.ytextbox_label)
        self.ytextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.ytextbox.SetValue(self.parent.parent.Ylabel)
        self.widgetlist.append(self.ytextbox)

        self.yformattextbox_label = wx.StaticText(self, wx.ID_ANY,
            "format: ")
        self.widgetlist.append(self.yformattextbox_label)
        self.yformattextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.yformattextbox.SetValue('auto')
        self.widgetlist.append(self.yformattextbox)


        self.cbtextbox_label = wx.StaticText(self, wx.ID_ANY,
            "cb-axis label: ")
        self.widgetlist.append(self.cbtextbox_label)
        self.cbtextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.cbtextbox.SetValue(self.parent.parent.Cblabel)

        self.widgetlist.append(self.cbtextbox)

        self.cbformattextbox_label = wx.StaticText(self, wx.ID_ANY,
            "format: ")
        self.widgetlist.append(self.cbformattextbox_label)
        self.cbformattextbox = wx.TextCtrl(self,wx.ID_ANY)
        self.cbformattextbox.SetValue('auto')
        self.widgetlist.append(self.cbformattextbox)


        self.Cancel = wx.Button(self,wx.ID_ANY, label = "Cancel")
        self.Apply = wx.Button(self,wx.ID_ANY,label = "Apply")

        self.Bind(wx.EVT_BUTTON,self.on_cancel,self.Cancel)
        self.Bind(wx.EVT_BUTTON,self.on_apply,self.Apply)

        self.mainbox = wx.BoxSizer(wx.VERTICAL)
        self.gridbox = wx.GridSizer(3,2,5,5)

        for widget in self.widgetlist:
            self.gridbox.Add(widget,0,wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER, border=10)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.Apply,0,wx.ALL|wx.ALIGN_CENTER,border=10)
        self.hbox.Add(self.Cancel,0,wx.ALL|wx.ALIGN_CENTER,border=10)

        self.mainbox.Add(self.gridbox,0)
        self.mainbox.Add(self.hbox,0,wx.EXPAND)

        self.SetSizerAndFit(self.mainbox)
        self.mainbox.Fit(self.parent)

    def on_apply(self,event):
        self.parent.parent.Xlabel = self.xtextbox.GetValue()
        self.parent.parent.Ylabel = self.ytextbox.GetValue()
        self.parent.parent.Cblabel = self.cbtextbox.GetValue()

        self.parent.parent.Xtickformat = self.xformattextbox.GetValue()
        self.parent.parent.Ytickformat = self.yformattextbox.GetValue()
        self.parent.parent.Cbtickformat = self.cbformattextbox.GetValue()

        self.parent.parent.PlotFrame.PlotPanel.set_labelticks()
        self.parent.parent.MainPanel.update_plot()

    def on_cancel(self,event):
        self.parent.Hide()

class CropFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent, title="Crop x/y axes")
        self.parent = parent
        self.CropPanel = CropPanel(self)
        self.Layout()

class CropPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent = parent

        self.widgetlist = []
        datafile = self.parent.parent.datafile
        #datafile.report()

        self.xrangebox_label = wx.StaticText(self, wx.ID_ANY,
            "x-axis left/right: ")
        self.widgetlist.append(self.xrangebox_label)
        self.xrange_left_spin = FloatSpin(self, name='x_left',
            value=datafile.Xleft,
            min_val=datafile.Xmin,
            max_val=datafile.Xmax,
            increment = datafile.dX,
            digits = 3
            )
        self.xrange_left_spin.SetFormat("%e")
        self.widgetlist.append(self.xrange_left_spin)
        self.xrange_right_spin = FloatSpin(self, name='x_right',
            value=datafile.Xright,
            min_val=datafile.Xmin,
            max_val=datafile.Xmax,
            increment = datafile.dX,
            digits = 3
            )
        self.xrange_right_spin.SetFormat("%e")
        self.widgetlist.append(self.xrange_right_spin)

        self.yrangebox_label = wx.StaticText(self, wx.ID_ANY,
            "y-axis bottom/top: ")
        self.widgetlist.append(self.yrangebox_label)
        self.yrange_bottom_spin = FloatSpin(self, name='y_bottom',
            value=datafile.Ybottom,
            min_val=datafile.Ymin,
            max_val=datafile.Ymax,
            increment = datafile.dY,
            digits = 3
            )
        self.yrange_bottom_spin.SetFormat("%e")
        self.widgetlist.append(self.yrange_bottom_spin)
        self.yrange_top_spin = FloatSpin(self, name='y_top',
            value=datafile.Ytop,
            min_val=datafile.Ymin,
            max_val=datafile.Ymax,
            increment = datafile.dY,
            digits = 3
            )
        self.yrange_top_spin.SetFormat("%e")
        self.widgetlist.append(self.yrange_top_spin)

        self.Revert = wx.Button(self,wx.ID_ANY, label = "Revert")
        self.Apply = wx.Button(self,wx.ID_ANY,label = "Apply")
        self.Close = wx.Button(self,wx.ID_ANY,label = "Close")

        self.Bind(wx.EVT_BUTTON,self.on_revert,self.Revert)
        self.Bind(wx.EVT_BUTTON,self.on_apply,self.Apply)
        self.Bind(wx.EVT_BUTTON,self.on_close,self.Close)

        self.mainbox = wx.BoxSizer(wx.VERTICAL)

        self.RangeBox = wx.StaticBox(self, wx.ID_ANY, 'Ranges:')
        self.RangeBoxSizer = wx.StaticBoxSizer(self.RangeBox, wx.VERTICAL)

        self.RangeGridSizer = wx.GridSizer(rows=2, cols=3, hgap=5, vgap=10)
        self.RangeBoxSizer.Add(self.RangeGridSizer)

        gridflags = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL

        for widget in self.widgetlist:
            self.RangeGridSizer.Add(widget,0,flag=gridflags)

        self.mainbox.Add(self.RangeBoxSizer)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.Revert,0,flag=wx.ALIGN_CENTER|wx.ALL,border=10)
        self.hbox.Add(self.Apply,0,flag=wx.ALIGN_CENTER|wx.ALL,border=10)
        self.hbox.Add(self.Close,0,flag=wx.ALIGN_CENTER|wx.ALL,border=10)

        self.mainbox.AddSpacer(10,1)
        self.mainbox.Add(self.hbox)

        self.SetSizerAndFit(self.mainbox)
        self.mainbox.Fit(self.parent)

    def on_apply(self,event):
        xleft = self.xrange_left_spin.GetValue()
        xright = self.xrange_right_spin.GetValue()
        ytop = self.yrange_top_spin.GetValue()
        ybottom = self.yrange_bottom_spin.GetValue()


        self.parent.parent.modlist.remMod("crop")
        self.parent.parent.modlist.addMod(tb.crop(xleft,xright,ybottom,ytop))

        self.parent.parent.modlist.applyModlist()
        self.parent.parent.MainPanel.update_plot()

    def on_revert(self,event):
        self.parent.parent.modlist.remMod("crop")
        self.parent.parent.modlist.applyModlist()
        self.parent.parent.MainPanel.update_plot()

    def on_close(self,event):
        self.parent.Destroy()

class LinecutFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent, title="Linecut series extraction")
        self.parent = parent
        panel = LinecutPanel(self)
        self.Layout()


class LinecutPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent = parent

        self.axes = self.parent.parent.PlotFrame.PlotPanel.axes
        self.canvas = parent.parent.PlotFrame.PlotPanel.canvas

        self.mainbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.radiox = wx.RadioButton(self, wx.ID_ANY, name="radiox",
            label="Cuts along x-axis: ", style=wx.RB_GROUP)
        self.radioy = wx.RadioButton(self, wx.ID_ANY, name="radioy",
            label="Cuts along y-axis: ")

        self.radiox.SetValue(True)

        self.Bind(wx.EVT_RADIOBUTTON, self.on_radioxy)

        flags = wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        self.hbox1.Add(self.radiox, 0, flag=flags, border=10)
        self.hbox1.Add(self.radioy, 0, flag=flags, border=10)

        self.mainbox.Add(self.hbox1)




        x_maxval = self.parent.parent.datafile.Xmax
        x_minval = self.parent.parent.datafile.Xmin
        y_maxval = self.parent.parent.datafile.Ymax
        y_minval = self.parent.parent.datafile.Ymin

        #self.parent.parent.datafile.report()

        x_mininterval = np.absolute(self.parent.parent.datafile.dX)
        y_mininterval = np.absolute(self.parent.parent.datafile.dY)

        self.x_minspin_label = wx.StaticText(self, wx.ID_ANY,
            "X range min: ")

        self.x_minspin = FloatSpin(self, name='x_min',
            value=x_minval,
            min_val=x_minval,
            max_val=x_maxval-x_mininterval,
            increment = x_mininterval,
            digits = 3
            )

        self.x_minspin.SetFormat("%e")

        self.x_maxspin_label = wx.StaticText(self, wx.ID_ANY,
            "X range max: ")

        self.x_maxspin = FloatSpin(self, name='x_max',
            value=x_maxval,
            min_val=x_minval+x_mininterval,
            max_val=x_maxval,
            increment = x_mininterval,
            digits = 3)

        self.x_maxspin.SetFormat("%e")

        self.x_intervalspin_label = wx.StaticText(self, wx.ID_ANY,
            "Interval width (x axis): ")

        self.x_intervalspin = FloatSpin(self, name='x_interval',
            value=np.absolute(x_maxval-x_minval)/10,
            min_val=x_mininterval,
            max_val=np.absolute(x_maxval-x_minval),
            increment = x_mininterval,
            digits = 3
            )

        self.x_intervalspin.SetFormat("%e")
        self.x_intervalspin.Enable(False)

        self.Bind(EVT_FLOATSPIN, self.on_floatspin)

        self.y_minspin_label = wx.StaticText(self, wx.ID_ANY,
            "Y range min: ")

        self.y_minspin = FloatSpin(self, name='y_min',
            value=y_minval,
            min_val=y_minval,
            max_val=y_maxval-y_mininterval,
            increment = y_mininterval,
            digits = 3
            )

        self.y_minspin.SetFormat("%e")

        self.y_maxspin_label = wx.StaticText(self, wx.ID_ANY,
            "Y range max: ")

        self.y_maxspin = FloatSpin(self, name='y_max',
            value=y_maxval,
            min_val=y_minval+y_mininterval,
            max_val=y_maxval,
            increment = y_mininterval,
            digits = 3)

        self.y_maxspin.SetFormat("%e")

        self.y_intervalspin_label = wx.StaticText(self, wx.ID_ANY,
            "Interval width (y axis): ")

        self.y_intervalspin = FloatSpin(self, name='y_interval',
            value=np.absolute(y_maxval-y_minval)/10,
            min_val=y_mininterval,
            max_val=np.absolute(y_maxval-y_minval),
            increment = y_mininterval,
            digits = 3
            )

        self.y_intervalspin.SetFormat("%e")

        self.Bind(EVT_FLOATSPIN, self.on_floatspin)


        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.hbox2.Add(self.x_maxspin_label,0,flag = flags, border = 10)
        self.hbox2.Add(self.x_maxspin,0,flag = flags, border = 10)
        self.hbox2.Add(self.x_minspin_label,0,flag = flags, border = 10)
        self.hbox2.Add(self.x_minspin,0,flag = flags, border = 10)
        self.hbox2.Add(self.x_intervalspin_label,0,flag = flags, border = 10)
        self.hbox2.Add(self.x_intervalspin,0,flag = flags, border = 10)

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.hbox3.Add(self.y_maxspin_label,0,flag = flags, border = 10)
        self.hbox3.Add(self.y_maxspin,0,flag = flags, border = 10)
        self.hbox3.Add(self.y_minspin_label,0,flag = flags, border = 10)
        self.hbox3.Add(self.y_minspin,0,flag = flags, border = 10)
        self.hbox3.Add(self.y_intervalspin_label,0,flag = flags, border = 10)
        self.hbox3.Add(self.y_intervalspin,0,flag = flags, border = 10)

        self.mainbox.AddSpacer(10,1)
        self.mainbox.Add(self.hbox2)
        self.mainbox.AddSpacer(10,1)
        self.mainbox.Add(self.hbox3)

        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        self.filenamebox_label = wx.StaticText(self, wx.ID_ANY,
            "Filename ({} for x/y val): ")

        self.filenamebox = wx.TextCtrl(self,wx.ID_ANY,"Linecut_y={}.dat")

        self.hbox4.Add(self.filenamebox_label,0,flag=flags, border = 10)
        self.hbox4.Add(self.filenamebox,1,flag = flags, border = 10)

        #self.SetSizerAndFit(self.hbox3)

        self.mainbox.AddSpacer(10,1)
        self.mainbox.Add(self.hbox4,0,flag=wx.EXPAND)

        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)

        self.Cancel = wx.Button(self,wx.ID_ANY, label = "Cancel")
        self.Save = wx.Button(self,wx.ID_ANY,label = "Save linecuts")

        self.Bind(wx.EVT_BUTTON,self.on_cancel,self.Cancel)
        self.Bind(wx.EVT_BUTTON,self.on_save,self.Save)

        self.hbox5.Add(self.Save,0,flag = flags, border = 10)
        self.hbox5.Add(self.Cancel,0, flag = flags, border = 10)

        self.mainbox.AddSpacer(10,1)
        self.mainbox.Add(self.hbox5)

        self.linelist = []

        self.SetSizerAndFit(self.mainbox)
        self.mainbox.Fit(self.parent)

    def on_save(self, event):

        datafile = self.parent.parent.datafile
        total_xrange = datafile.Xrange
        total_yrange = datafile.Yrange

        if self.radioy.GetValue():

            total_mininterval = np.absolute(total_xrange[1]-total_xrange[0])

            x_start = datafile.get_xrange_idx(self.x_minspin.GetValue())
            x_end = datafile.get_xrange_idx(self.x_maxspin.GetValue())
            x_step = int(self.x_intervalspin.GetValue()/total_mininterval)

            y_start = datafile.get_yrange_idx(self.y_minspin.GetValue())
            y_end = datafile.get_yrange_idx(self.y_maxspin.GetValue())

            position = x_start
            while position <= x_end:

                fname = self.filenamebox.GetValue()
                #fname.replace("$","{}".format(total_xrange[position]))

                print "Zdata shape : {}".format(datafile.Zdata[:,position].shape)
                print "Yrange shape : {}".format(total_yrange.shape)


                linecut = np.vstack([total_yrange[y_start:y_end],self.parent.parent.datafile.Zdata[y_start:y_end,position]])
                print linecut.shape
                np.savetxt(fname.format(total_xrange[position]),linecut.T)

                position += x_step

        if self.radiox.GetValue():

            total_mininterval = np.absolute(total_yrange[1]-total_yrange[0])

            y_start = datafile.get_yrange_idx(self.y_minspin.GetValue())
            y_end = datafile.get_yrange_idx(self.y_maxspin.GetValue())
            y_step = int(self.y_intervalspin.GetValue()/total_mininterval)

            x_start = datafile.get_xrange_idx(self.x_minspin.GetValue())
            x_end = datafile.get_xrange_idx(self.x_maxspin.GetValue())

            position = y_start
            while position <= y_end:

                fname = self.filenamebox.GetValue()
                #fname.replace("$","{}".format(total_xrange[position]))

                print "Zdata shape : {}".format(datafile.Zdata[position,x_start:x_end].shape)
                print "Xrange shape : {}".format(total_xrange[x_start:x_end].shape)


                linecut = np.vstack([total_xrange[x_start:x_end],self.parent.parent.datafile.Zdata[position,x_start:x_end]])
                print linecut.shape
                np.savetxt(fname.format(total_yrange[position]),linecut.T)

                position += y_step


    def on_cancel(self, event):
        if self.linelist:
            for line in self.linelist:
                line.remove()
        self.canvas.draw()
        self.axes.autoscale(True)

        self.parent.Hide()

    def on_radioxy(self, event):
        evt_obj = event.GetEventObject()

        if evt_obj.GetName == "radiox":
            self.y_intervalspin.Enable(True)
            self.x_intervalspin.Enable(False)
            self.filenamebox.SetValue("Linecut_y={}.dat")
        if evt_obj.GetName() == "radioy":
            self.x_intervalspin.Enable(True)
            self.y_intervalspin.Enable(False)
            self.filenamebox.SetValue("Linecut_x={}.dat")


    def on_floatspin(self,event):
        evt_obj = event.GetEventObject()
        if "x_" in evt_obj.GetName():
            maxval = self.x_maxspin.GetValue()
            minval = self.x_minspin.GetValue()
            interval = self.x_intervalspin.GetValue()
        else:
            maxval = self.y_maxspin.GetValue()
            minval = self.y_minspin.GetValue()
            interval = self.y_intervalspin.GetValue()

        if "min" in evt_obj.GetName():
            if maxval-interval < minval:
                interval = maxval-minval
        if "max" in evt_obj.GetName():
            if minval+interval > maxval:
                interval = maxval-minval
        if "interval" in evt_obj.GetName():
            if maxval-minval < interval:
                maxval = minval + interval

        if "x_" in evt_obj.GetName():
            self.x_maxspin.SetValue(maxval)
            self.x_minspin.SetValue(minval)
            self.x_intervalspin.SetValue(interval)
        else:
            self.y_maxspin.SetValue(maxval)
            self.y_minspin.SetValue(minval)
            self.y_intervalspin.SetValue(interval)

        self.drawGrid()

    def drawGrid(self):
        datafile = self.parent.parent.datafile
        total_xrange = datafile.Xrange
        total_yrange = datafile.Yrange

        if self.linelist:
            for line in self.linelist:
                line.remove()

        self.linelist = []

        if self.radioy.GetValue():

            x_start = self.x_minspin.GetValue()
            x_end = self.x_maxspin.GetValue()
            x_step = self.x_intervalspin.GetValue()

            y_start = self.y_minspin.GetValue()
            y_end = self.y_maxspin.GetValue()


            position = x_start
            while position <= x_end:
                self.linelist.append(self.axes.plot([position,position],[y_start,y_end])[0])

                position += x_step

        if self.radiox.GetValue():

            y_start = self.y_minspin.GetValue()
            y_end = self.y_maxspin.GetValue()
            y_step = self.y_intervalspin.GetValue()

            x_start = self.x_minspin.GetValue()
            x_end = self.x_maxspin.GetValue()


            position = y_start
            while position <= y_end:
                self.linelist.append(self.axes.plot([x_start,x_end],[position,position])[0])

                position += y_step

        self.canvas.draw()

class LineoutFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent, title="Line trace tool",size=(800,600))
        self.parent = parent
        self.LineoutPanel = LineoutPanel(self)
        self.Layout()


class LineoutPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent = parent


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

        self.axes.set_ylabel(self.parent.parent.Cblabel)

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
        self.parent.parent.PlotFrame.PlotPanel.axes.autoscale(True)
        self.parent.parent.MainPanel.update_plot()
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

        self.parent.parent.PlotFrame.PlotPanel.canvas.draw()


    def draw_linetrace(self):

        datafile = self.parent.parent.datafile

        idx1 = self.closest_idx(self.x1,datafile.Xrange)
        idx2 = self.closest_idx(self.x2,datafile.Xrange)

        idy1 = self.closest_idx(self.y1,datafile.Yrange)
        idy2 = self.closest_idx(self.y2,datafile.Yrange)

        if np.abs(idx2 - idx1) > np.abs(idy2 - idy1):
            x_range = np.linspace(idx1,idx2,int(np.absolute(idx2-idx1)+1)).astype(int)
            y_range = np.array([self.closest_idx(self.currentline.get_y(xval),datafile.Yrange) for xval in datafile.Xrange[x_range]])

        else:
            y_range = np.linspace(idy1,idy2,int(np.absolute(idy2-idy1)+1)).astype(int)
            x_range = np.array([self.closest_idx(self.currentline.get_x(yval),datafile.Xrange) for yval in datafile.Yrange[y_range]])


        dataview = datafile.Zdata[datafile.Bsize-y_range,x_range]

        self.axes.plot(dataview)
        self.canvas.draw()

        self.linelist.append(self.currentline)
        self.currentline = MyLine(self.parent.parent.PlotFrame.PlotPanel.axes)



    def closest_idx(self,val,array):
        return (np.abs(array-val)).argmin()


class SlopeExFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent, title="Linear slope extraction",size=(430,320))
        self.parent = parent
        self.SlopeExPanel = SlopeExPanel(self)
        self.Layout()


class SlopeExPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent = parent

        self.parent.parent.PlotFrame.PlotPanel.axes.autoscale(False)
        self.currentline = MyLine(self.parent.parent.PlotFrame.PlotPanel.axes)
        self.linelist = []

        self.lineindex = -1

        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None

        self.cid = parent.parent.PlotFrame.PlotPanel.canvas.mpl_connect('button_press_event',self.on_click)

        # the line spin-control widgets

        self.pointwidgetlist = []

        max_xval = self.parent.parent.datafile.Xmax
        min_xval = self.parent.parent.datafile.Xmin
        max_yval = self.parent.parent.datafile.Ymax
        min_yval = self.parent.parent.datafile.Ymin

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

        self.commenttext = wx.StaticText(self,wx.ID_ANY,"Comment:")
        self.commenttextbox = wx.TextCtrl(self,wx.ID_ANY)

        # the line list widget

        self.linelistbox = VariableListCtrl(self,wx.ID_ANY,size=(250,160), style = wx.LC_REPORT|wx.BORDER_SUNKEN)

        self.linelistbox.InsertColumn(0,'x-shift',width=70)
        self.linelistbox.InsertColumn(1,'slope',width=70)
        self.linelistbox.InsertColumn(2,'comment')

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

        self.CoordGridSizer = wx.GridSizer(rows=2, cols=4, hgap=5, vgap=10)

        gridflags = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL

        for widget in self.pointwidgetlist:
            self.CoordGridSizer.Add(widget,flag = gridflags)

        self.CoordBoxSizer.Add(self.CoordGridSizer)

        self.middlevbox.Add(self.CoordBoxSizer)
        self.middlevbox.AddSizer((-1,10))

        self.listhbox = wx.BoxSizer(wx.HORIZONTAL)
        self.listvbox_left = wx.BoxSizer(wx.VERTICAL)
        self.listvbox_right = wx.BoxSizer(wx.VERTICAL)

        self.listvbox_left.Add(self.linelistbox,1,wx.ALL|wx.EXPAND,border=10)

        self.listvbox_right.Add(self.commenttext,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,border = 5)
        self.listvbox_right.Add(self.commenttextbox,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,border = 5)

        self.listvbox_right.Add(self.addlinebutton,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,border = 5)
        self.listvbox_right.Add(self.removelinebutton,0,wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        self.listvbox_right.Add(self.savelistbutton,0,wx.ALIGN_CENTER_VERTICAL| wx.ALL, border = 5)

        self.listhbox.Add(self.listvbox_left)
        self.listhbox.Add(self.listvbox_right,1,wx.EXPAND)

        self.middlevbox.Add(self.listhbox,1,wx.EXPAND)

        self.middlevbox.Add(wx.StaticLine(self, -1))
        self.middlevbox.Add(self.close_button,flag = wx.ALIGN_CENTER)

        self.mainbox.Add((10,10))
        self.mainbox.Add(self.middlevbox)
        self.mainbox.Add((10,10))

        self.SetSizerAndFit(self.mainbox)

    def on_addline(self,event):
        if self.x1 != self.x2:
            self.lineindex += 1

            comment = self.commenttextbox.GetValue()

            self.currentline.set_comment(comment)
            self.linelist.append(self.currentline)

            self.linelistbox.InsertStringItem(self.lineindex,"{0:.2e}".format(self.linelist[self.lineindex].get_shift()))
            self.linelistbox.SetStringItem(self.lineindex,1,"{0:.2e}".format(self.linelist[self.lineindex].get_slope()))
            self.linelistbox.SetStringItem(self.lineindex,2,self.linelist[self.lineindex].get_comment())

            self.parent.parent.PlotFrame.PlotPanel.canvas.draw()

            self.currentline = MyLine(self.parent.parent.PlotFrame.PlotPanel.axes)



    def on_removeline(self,event):
        if self.linelist:

            self.linelistbox.DeleteItem(self.lineindex)
            self.lineindex -= 1

            self.linelist.pop().removeline()

            self.parent.parent.PlotFrame.PlotPanel.canvas.draw()

    def on_savelist(self,event):
        file_choices = "DAT (*.dat)|*.dat"
        datafilename = self.parent.parent.datafilename

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
            outfile.write("# Linear slopes extracted from {} \n\
# line shift (x-axis) | slope | comment\n".format(datafilename))
            for line in self.linelist:
                outfile.write("{}\t{}\t#{}\n".format(line.get_shift(),line.get_slope(),line.get_comment()))


    def on_close(self,event):
        self.currentline.removeline()
        if self.linelist:
            for line in self.linelist:
                line.removeline()

        self.parent.parent.PlotFrame.PlotPanel.axes.autoscale(True)
        self.parent.parent.MainPanel.update_plot()
        self.parent.Destroy()

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

    def on_click(self,event):
        if event.inaxes!=self.currentline.axes: return

        if event.button == 1:
            self.x1 = event.xdata
            self.y1 = event.ydata
        if event.button == 3:
            self.x2 = event.xdata
            self.y2 = event.ydata

        if self.x1 and self.x2:
            self.update_spinctrl()
            self.draw_line()


    def draw_line(self):
        self.currentline.set_data(self.x1,self.x2, self.y1,self.y2)
        #self.currentline.figure.tight_layout()
        #self.currentline.figure.canvas.draw()
        #self.parent.parent.PlotFrame.PlotPanel.fig.tight_layout()
        self.parent.parent.PlotFrame.PlotPanel.canvas.draw()
        #self.parent.Layout()

    def update_spinctrl(self):
        self.x1spin.SetValue(self.x1)
        self.y1spin.SetValue(self.y1)
        self.x2spin.SetValue(self.x2)
        self.y2spin.SetValue(self.y2)

class BinaryFitFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent, title="Segmentation and Fitting")
        self.parent = parent
        self.BinaryFitPanel = BinaryFitPanel(self)
        self.Layout()


class BinaryFitPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent = parent


        self.mainbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.chk_threshold = wx.CheckBox(self, wx.ID_ANY, 'Apply adaptive threshold')
        self.Bind(wx.EVT_CHECKBOX,self.on_chk_threshold,self.chk_threshold)

        self.blocksize_label = wx.StaticText(self, wx.ID_ANY,
            "Blocksize: ")
        self.offset_label = wx.StaticText(self, wx.ID_ANY,
            "Offset: ")

        maxval = self.parent.parent.datafile.Zmax
        minval = self.parent.parent.datafile.Zmin
        maxsize = np.amin([self.parent.parent.datafile.Bsize,self.parent.parent.datafile.Bnum])/2
        width = maxval-minval
        spin_incr = width/1000

        self.blocksize_spin = wx.SpinCtrl(self, wx.ID_ANY,
                                          value = '1',
                                          min = 1,
                                          max = maxsize.astype(int),
                                          name = 'thr_blocksize')
        self.Bind(wx.EVT_SPINCTRL,self.on_spin,self.blocksize_spin)
        self.offset_spin =  FloatSpin(self, name='thr_offset',
            value=0,
            min_val=-width,
            max_val=width,
            increment = spin_incr,
            digits = 3)

        self.offset_spin.SetFormat("%e")
        self.Bind(EVT_FLOATSPIN, self.on_spin)

        flags = wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        self.hbox1.Add(self.chk_threshold, 0, flag=flags, border=10)
        self.hbox1.Add(self.blocksize_label, 0, flag=flags, border=10)
        self.hbox1.Add(self.blocksize_spin, 0, flag=flags, border=10)

        self.hbox2.Add((0,0),1)
        self.hbox2.Add(self.offset_label, 0, flag=flags, border=10)
        self.hbox2.Add(self.offset_spin, 0, flag=flags, border=10)


        self.ModBox = wx.StaticBox(self, wx.ID_ANY, 'Image Segmentation')
        self.ModBoxSizer = wx.StaticBoxSizer(self.ModBox, wx.VERTICAL)

        self.ModBoxSizer.Add(self.hbox1,0)
        self.ModBoxSizer.AddSpacer(10)
        self.ModBoxSizer.Add(self.hbox2,0,flag=wx.EXPAND)

        self.mainbox.Add(self.ModBoxSizer,0,flag=wx.LEFT|wx.RIGHT,border=10)

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.formulactrl_label = wx.StaticText(self, wx.ID_ANY,
            "Formula: ")
        self.formulactrl = wx.TextCtrl(self,wx.ID_ANY)
        self.compile_button = wx.Button(self,wx.ID_ANY, label = "Compile")
        self.Bind(wx.EVT_BUTTON,self.on_compile,self.compile_button)

        self.hbox3.Add(self.formulactrl_label,0,flag=wx.TOP|wx.ALIGN_CENTER_VERTICAL, border = 10)
        self.hbox3.Add(self.formulactrl,1,flag=wx.TOP, border = 10)
        self.hbox3.Add(self.compile_button,0,flag=wx.TOP, border = 10)

        self.mainbox.Add((-1,10))
        self.mainbox.Add(self.hbox3,0,wx.EXPAND)


        self.ParBox = wx.StaticBox(self, wx.ID_ANY, 'Parameter')
        self.ParBoxSizer = wx.StaticBoxSizer(self.ParBox, wx.VERTICAL)

        self.ParBoxDict = {}

        for pnum in np.arange(10):
            phbox = wx.BoxSizer(wx.HORIZONTAL)
            name = "P{}".format(pnum)
            self.ParBoxDict[name] = ParameterControl(self,name,phbox)

            self.ParBoxSizer.Add(phbox)

        self.delta_y_spin =  FloatSpin(self, name='delta_y',
            value=self.parent.parent.datafile.Ymax - self.parent.parent.datafile.Ymin,
            min_val=0,
            max_val=self.parent.parent.datafile.Ymax - self.parent.parent.datafile.Ymin,
            increment = self.parent.parent.datafile.dY,
            digits = 3)


        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        self.Fit = wx.Button(self,wx.ID_ANY, label = "Fit")
        self.Bind(wx.EVT_BUTTON,self.on_fit,self.Fit)
        self.Save = wx.Button(self,wx.ID_ANY,label = "Save")
        self.Bind(wx.EVT_BUTTON,self.on_save,self.Save)

        self.hbox4.Add(self.delta_y_spin,0,flag= wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_CENTER_VERTICAL, border = 10)
        self.hbox4.Add(self.Fit,0,flag= wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_CENTER_VERTICAL, border = 10)
        self.hbox4.Add(self.Save,0,flag= wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_CENTER_VERTICAL, border = 10)


        self.mainbox.Add(self.ParBoxSizer,0)
        self.mainbox.Add(self.hbox4,0)

        self.savecancelbox = wx.BoxSizer(wx.HORIZONTAL)

        self.Close = wx.Button(self,wx.ID_ANY, label = "Close")

        self.Bind(wx.EVT_BUTTON,self.on_close,self.Close)

        self.savecancelbox.Add(self.Close, 0, flag= wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_CENTER_VERTICAL, border = 10)

        self.mainbox.Add(self.savecancelbox,0)

        self.SetSizerAndFit(self.mainbox)
        self.mainbox.Fit(self.parent)

        self.Xrange = self.parent.parent.datafile.Xrange


    def on_save(self, event):
        file_choices = "DAT (*.dat)|*.dat"

        datafilename = self.parent.parent.datafilename

        dlg = wx.FileDialog(
            self,
            message="Save function and parameter to...",
            defaultDir=os.getcwd(),
            defaultFile="fitfunction.dat",
            wildcard=file_choices,
            style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()

        with open(path, 'a') as outfile:
            outfile.write("# Fitted function to data in {} \n\
# Function Body\n\
{}\n\
# Parameters:\n".format(datafilename,self.formula.get_fxp()))
            for k,p in self.formula.pdict.iteritems():
                outfile.write("{}\t{}\t\n".format(p.name,p.value))

            outfile.write("\n\
# Function with parameters:\n\
{}\n\n".format(self.formula.get_fx()))




    def on_compile(self,event):
        self.axes = self.parent.parent.PlotFrame.PlotPanel.axes
        self.axes.autoscale(False)
        self.Xrange = self.parent.parent.datafile.Xrange
        self.lineplot, = self.axes.plot(self.Xrange,np.zeros(self.Xrange.size))

        fstring = self.formulactrl.GetValue()
        self.formula = parser.parse(fstring)


        for num,k in enumerate(self.formula.pdict):
            self.ParBoxDict['P'+str(num)].set_name(k)
            self.ParBoxDict['P'+str(num)].enable(True)

        for n in range(num+1,10):
            self.ParBoxDict['P'+str(n)].enable(False)


    def on_close(self, event):
        self.parent.parent.modlist.remMod("adaptive-threshold")
        self.parent.parent.modlist.applyModlist()
        if hasattr(self,'lineplot'):
            self.lineplot.remove()

        self.parent.parent.PlotFrame.PlotPanel.axes.autoscale(True)

        self.parent.parent.MainPanel.update_plot()
        self.parent.MakeModal(False)
        self.parent.Hide()

    def on_chk_threshold(self, event):
        if self.chk_threshold.GetValue():
            self.parent.parent.modlist.addMod(tb.adaptive_threshold(self.blocksize_spin.GetValue(),self.offset_spin.GetValue()))
        else:
            self.parent.parent.modlist.remMod("adaptive-threshold")

        self.parent.parent.modlist.applyModlist()

        #self.parent.parent.MainPanel.init_colorspinctrls()

        self.parent.parent.MainPanel.update_plot()

    def on_spin(self,event):
        evt_obj = event.GetEventObject()

        if evt_obj.GetName().startswith('thr_'):
            if self.chk_threshold.GetValue():
                self.parent.parent.modlist.remMod("adaptive-threshold")
                self.parent.parent.modlist.addMod(tb.adaptive_threshold(self.blocksize_spin.GetValue(),self.offset_spin.GetValue()))
                self.parent.parent.modlist.applyModlist()
                self.parent.parent.MainPanel.update_plot()

        elif evt_obj.GetName().startswith('par_'):
            ctrl = self.ParBoxDict[evt_obj.GetName().split('_',1)[1]]

            ctrl.update()
            parm = ctrl.get_name()
            val = ctrl.get_value()

            #print "Parameter {}, Value {}".format(parm,val)

            self.formula.setp({parm:val})
            #self.formula.print_fx()
            self.draw_function()

        elif evt_obj.GetName().startswith('incr_'):
            ctrl = self.ParBoxDict[evt_obj.GetName().split('_',1)[1]]
            ctrl.update()

    def draw_function(self):

        self.func_y = np.array([ self.formula.eval(x) for x in self.Xrange])

        self.lineplot.set_ydata(self.func_y)
        self.parent.parent.PlotFrame.PlotPanel.canvas.draw()

    def update_controls(self):
        for p in self.ParBoxDict:
            try:
                #print "Set Key {}".format(self.ParBoxDict[p].get_name())
                self.ParBoxDict[p].set_value(self.formula.pdict[self.ParBoxDict[p].get_name()].value)
            except KeyError as e:
                #print "Key not found: ",e.message
                pass


    def on_fit(self,event):
        from lmfit import Minimizer, Parameters, report_errors
        if self.chk_threshold.GetValue():
            datafile = self.parent.parent.datafile
            # Get indices of values that dy from function
            delta_y = self.delta_y_spin.GetValue()
            y_indexrange = int(delta_y/datafile.dY)
            if y_indexrange <= 1:
                y_indexrange = 1

            points_all = np.vstack(np.where(datafile.Zdata)).T
            func_points = self.func_y[points_all[:,1]]

            yrange = datafile.Yrange[::-1]
            points_sel = points_all[abs(yrange[points_all[:,0]] - func_points) < delta_y]

            def residual(params,xrange,data):
                self.formula.init_f()
                func_y = np.array([ self.formula.eval(x) for x in xrange])

                return func_y - data


            Min = Minimizer(residual, self.formula.pdict, fcn_args=(datafile.Xrange[points_sel[:,1]],yrange[points_sel[:,0]]))

            result = Min.fmin()

            report_errors(self.formula.pdict)

            self.update_controls()
            self.draw_function()





class ParameterControl():
    def __init__(self,parent,name,BoxSizer):
        self.parent = parent
        self.name = name
        self.box = BoxSizer
        self.label = wx.StaticText(self.parent, wx.ID_ANY,
            "{} / Increment: ".format(name))

        self.value = 0
        self.increment = 1
        self.value_spin = FloatSpin(self.parent, name="par_"+name,
            value=0,
            increment = self.increment,
            digits = 3)
        self.value_spin.SetFormat("%e")
        self.value_spin.Enable(False)

        self.incr_spin = FloatSpin(self.parent, name="incr_"+name,
            value=0,
            increment = 1,
            digits = 1)

        self.incr_spin.Enable(False)

        self.parent.Bind(EVT_FLOATSPIN, self.parent.on_spin)

        self.lock_check = wx.CheckBox(self.parent, name="lock_"+name)
        self.parent.Bind(wx.EVT_CHECKBOX,self.on_lock, self.lock_check)
        self.lock_check.Enable(False)

        self.box.Add(self.label)
        self.box.Add(self.value_spin)
        self.box.Add(self.incr_spin)
        self.box.Add(self.lock_check)

    def on_lock(self,event):
        self.parent.formula.pdict[self.name].vary = not self.lock_check.GetValue()

    def set_name(self,name):
        self.name = name
        self.label.SetLabel(name)

    def get_name(self):
        return self.name
    def get_value(self):
        return self.value

    def enable(self,Bool):
        self.value_spin.Enable(Bool)
        self.incr_spin.Enable(Bool)
        self.lock_check.Enable(Bool)

    def set_value(self,value):
        self.value = value
        self.value_spin.SetValue(value)

    def set_increment(self,increment):
        self.increment = increment
        self.incr_spin.SetValue(self.increment)
        self.value_spin.SetIncrement(10.**self.increment)

    def update(self):
        self.value = self.value_spin.GetValue()
        self.increment = self.incr_spin.GetValue()

        self.value_spin.SetIncrement(10.**self.increment)


class MyLine():
    def __init__(self,axes,x1 = 0, y1 = 0, x2 = 0, y2 = 0, comment=""):
        self.x1 = x1
        self.y1 = y1
        self.y2 = y2
        self.x2 = x2
        self.comment = comment

        self.axes = axes
        self.line, = self.axes.plot([self.x1,self.x2],[self.y1,self.y2])
        self.commenttext = self.axes.text(self.x1,self.y1-0.5,self.comment)



    def removeline(self):
        self.commenttext.remove()
        self.line.remove()

    def set_data(self,x1,x2,y1,y2):
        self.x1 = x1
        self.y1 = y1
        self.y2 = y2
        self.x2 = x2

        self.line.set_data([x1,x2],[y1,y2])

    def set_comment(self,comment):
        self.comment = comment
        self.commenttext.remove()
        self.commenttext = self.axes.text(self.x1,self.y1-0.5,self.comment)

    def get_slope(self):
        return (self.y2 - self.y1)/(self.x2-self.x1)

    def get_shift(self):
        return -self.y1/self.get_slope() + self.x1

    def get_y(self,x):
        return self.get_slope()*(x-self.get_shift())
    def get_x(self,y):
        return y/self.get_slope()+self.get_shift()

    def get_comment(self):
        return self.comment

class VariableListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)



class FloatValidator(wx.PyValidator):
    """ This validator is used to ensure that the user has entered something
        into the text object editor dialog's text field.
    """
    def __init__(self):
        """ Standard constructor.
        """
        wx.PyValidator.__init__(self)



    def Clone(self):
        """ Standard cloner.

            Note that every validator must implement the Clone() method.
        """
        return FloatValidator()

    def Validate(self, win):
        textCtrl = self.GetWindow()
        num_string = textCtrl.GetValue()
        try:
            float(num_string)
        except:
            textCtrl.SetValue("1e0")
            return False
        return True


    def TransferToWindow(self):
        """ Transfer data from validator to window.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True # Prevent wxDialog from complaining.


    def TransferFromWindow(self):
        """ Transfer data from window to validator.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True # Prevent wxDialog from complaining.

class Colorview2d(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
 
    def OnInit(self):
        # create frame here
        frame = MainFrame()
        frame.Show()
        frame.Layout()
        return True
    
if __name__ == '__main__':
    app = Colorview2d()
    app.MainLoop()
