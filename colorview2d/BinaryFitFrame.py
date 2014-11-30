import wx
import os
import numpy as np
import matplotlib.pyplot as plt
from floatspin import FloatSpin,EVT_FLOATSPIN
import toolbox as tb
from View import View

import parser

from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar


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

        # self.leftbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxplot = wx.BoxSizer(wx.HORIZONTAL)

        self.blocksize_label = wx.StaticText(self, wx.ID_ANY,
            "Blocksize: ")
        self.offset_label = wx.StaticText(self, wx.ID_ANY,
            "Offset: ")

        self.view = self.parent.parent.view
        self.Xrange = self.view.datafile.Xrange

        maxval = self.view.get_data().max()
        minval = self.view.get_data().min()
        maxsize = np.amin([self.view.datafile.Bsize,self.view.datafile.Bnum])/2
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

        self.plot_button = wx.Button(self,wx.ID_ANY, label = "Apply")

        flags = wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL

        self.hbox1.Add(self.blocksize_label, 0, flag=flags, border=10)
        self.hbox1.Add(self.blocksize_spin, 0, flag=flags, border=10)

        self.hbox2.Add((0,0),1)
        self.hbox2.Add(self.offset_label, 0, flag=flags, border=10)
        self.hbox2.Add(self.offset_spin, 0, flag=flags, border=10)
        self.hbox2.Add(self.plot_button,0,flag=flags, border=10)


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
        self.Bind(wx.EVT_BUTTON,self.on_plot,self.plot_button)

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
            value=self.parent.parent.view.datafile.Ymax - self.parent.parent.view.datafile.Ymin,
            min_val=0,
            max_val=self.parent.parent.view.datafile.Ymax - self.parent.parent.view.datafile.Ymin,
            increment = self.parent.parent.view.datafile.dY,
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
        #self.mainbox.Fit(self.parent)

        # Call all sizing routines
        self.Layout()



    def on_save(self, event):
        file_choices = "DAT (*.dat)|*.dat"

        datafilename = self.view.datafilename

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
        self.axes.autoscale(False)
        self.Xrange = self.view.datafile.Xrange
        self.lineplot, = self.axes.plot(self.Xrange,np.zeros(self.Xrange.size))

        fstring = self.formulactrl.GetValue()
        self.formula = parser.parse(fstring)


        for num,k in enumerate(self.formula.pdict):
            self.ParBoxDict['P'+str(num)].set_name(k)
            self.ParBoxDict['P'+str(num)].enable(True)

        for n in range(num+1,10):
            self.ParBoxDict['P'+str(n)].enable(False)


    def on_close(self, event):

        if hasattr(self,'lineplot'):
            self.lineplot.remove()

        self.view.remMod('adaptive-threshold')
        self.parent.Destroy()

    def on_plot(self,event):

        self.view.addMod(tb.adaptive_threshold(self.blocksize_spin.GetValue(),self.offset_spin.GetValue()))

    def on_spin(self,event):
        evt_obj = event.GetEventObject()
        if evt_obj.GetName().startswith('par_'):
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
        self.canvas.draw()

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

        datafile = self.view.datafile
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
