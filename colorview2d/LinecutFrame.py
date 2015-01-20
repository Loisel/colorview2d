import wx
import os
import numpy as np
from floatspin import FloatSpin,EVT_FLOATSPIN
from Utils import resource_path

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

        self.datafile = self.parent.parent.view.datafile 

        #self.parent.parent.datafile.report()

        x_mininterval = np.absolute(self.datafile.dX)
        y_mininterval = np.absolute(self.datafile.dY)

        self.x_minspin_label = wx.StaticText(self, wx.ID_ANY,
            "X range left: ")

        self.x_minspin = FloatSpin(self, name='x_min',
            value=self.datafile.Xleft,
            min_val=self.datafile.Xmin,
            max_val=self.datafile.Xmax-x_mininterval,
            increment = x_mininterval,
            digits = 3
            )

        self.x_minspin.SetFormat("%e")

        self.x_maxspin_label = wx.StaticText(self, wx.ID_ANY,
            "X range right: ")

        self.x_maxspin = FloatSpin(self, name='x_max',
            value=self.datafile.Xright,
            min_val=self.datafile.Xmin+x_mininterval,
            max_val=self.datafile.Xmax,
            increment = x_mininterval,
            digits = 3)

        self.x_maxspin.SetFormat("%e")

        self.x_intervalspin_label = wx.StaticText(self, wx.ID_ANY,
            "Interval width (x axis): ")

        self.x_intervalspin = FloatSpin(self, name='x_interval',           
                                        value=np.absolute(self.datafile.Xmax-self.datafile.Xmin)/10,
                                        min_val=x_mininterval,
                                        max_val=np.absolute(self.datafile.Xmax-self.datafile.Xmin)-x_mininterval,
                                        increment = x_mininterval,
                                        digits = 3
                                    )

        self.x_intervalspin.SetFormat("%e")
        self.x_intervalspin.Enable(False)

        self.Bind(EVT_FLOATSPIN, self.on_floatspin)

        self.y_minspin_label = wx.StaticText(self, wx.ID_ANY,
            "Y range bottom: ")

        self.y_minspin = FloatSpin(self, name='y_min',
            value=self.datafile.Ybottom,
            min_val=self.datafile.Ymin,
            max_val=self.datafile.Ymax-y_mininterval,
            increment = y_mininterval,
            digits = 3
            )

        self.y_minspin.SetFormat("%e")

        self.y_maxspin_label = wx.StaticText(self, wx.ID_ANY,
            "Y range max: ")

        self.y_maxspin = FloatSpin(self, name='y_max',
            value=self.datafile.Ytop,
            min_val=self.datafile.Ymin+y_mininterval,
            max_val=self.datafile.Ymax,
            increment = y_mininterval,
            digits = 3)

        self.y_maxspin.SetFormat("%e")

        self.y_intervalspin_label = wx.StaticText(self, wx.ID_ANY,
            "Interval width (y axis): ")

        self.y_intervalspin = FloatSpin(self, name='y_interval',
                                        value=np.absolute(self.datafile.Ymax-self.datafile.Ymin)/10,
                                        min_val=y_mininterval,
                                        max_val=np.absolute(self.datafile.Ymax-self.datafile.Ymin)-y_mininterval,
                                        increment = y_mininterval,
                                        digits = 3)

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
        """
        Save the linecut series to files specified by the string in
        filenamebox. Curly brackets {} serve as a placeholder for the
        running variable.

        Arguments:
          event (wx.EVT_BUTTON): mouse click event emitted by the save button

        """

        fname = self.filenamebox.GetValue()

        dialog = wx.DirDialog(None, "Choose a directory to save the linetraces:",style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)

        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            fname = os.path.join(path,fname)
        else:
            return

            
        #print "Total zdata shape {}".format(self.datafile.Zdata.shape)
        total_xrange = self.datafile.Xrange
        total_yrange = self.datafile.Yrange

        x_left_idx = self.datafile.get_xrange_idx(self.x_minspin.GetValue())
        x_right_idx = self.datafile.get_xrange_idx(self.x_maxspin.GetValue())
        x_sign = np.sign(x_right_idx-x_left_idx)

        y_bottom_idx = self.datafile.get_yrange_idx(self.y_minspin.GetValue())
        y_top_idx = self.datafile.get_yrange_idx(self.y_maxspin.GetValue())
        y_sign = np.sign(y_top_idx-y_bottom_idx)

        if self.radioy.GetValue():

            total_mininterval = np.absolute(total_xrange[1]-total_xrange[0])

            x_step_idx = int(self.x_intervalspin.GetValue()/total_mininterval)

            # print "x_start_idx {} x_end {} x_step {} ystart {} yend {}".format(x_left_idx,x_right_idx,x_step_idx,y_bottom_idx,y_top_idx)

            position = x_left_idx
            while position*x_sign <= x_right_idx*x_sign:

                xval = total_xrange[position]
                
                #fname.replace("$","{}".format(total_xrange[position]))

                #print "Zdata shape : {}".format(self.datafile.Zdata[:,position].shape)
                #print "Yrange shape : {}".format(total_yrange.shape)

                linecut = np.vstack([total_yrange[y_bottom_idx:y_top_idx:y_sign],self.datafile.Zdata[y_bottom_idx:y_top_idx:y_sign,position]])
                # print linecut.shape
                
                with open(fname.format(xval),'w') as file:
                    file.write("# Linecut along y axis at x = {}\n".format(xval))
                    np.savetxt(file,linecut.T)

                position += x_step_idx*x_sign
                if x_sign == 0:
                    break

        if self.radiox.GetValue():

            total_mininterval = np.absolute(total_yrange[1]-total_yrange[0])

            y_step_idx = int(self.y_intervalspin.GetValue()/total_mininterval)

            ## print "x start: {} / x end: {}".format(x_start_idx,x_end)
            ## print "y start: {} / y end: {} / y step: {}".format(y_start,y_end,y_step)

            position = y_bottom_idx
            while position*y_sign <= y_top_idx*y_sign:

                yval = total_yrange[position]

                # print "y position {}".format(position)
                # print "Zdata shape : {}".format(self.datafile.Zdata[position,x_start_idx:x_end].shape)
                # print "Xrange shape : {}".format(total_xrange[x_start_idx:x_end].shape)


                linecut = np.vstack([total_xrange[x_left_idx:x_right_idx:x_sign],self.datafile.Zdata[position,x_left_idx:x_right_idx:x_sign]])

                with open(fname.format(yval),'w') as file:
                    file.write("# Linecut along x axis at y = {}\n".format(yval))
                    np.savetxt(file,linecut.T)

                position += y_step_idx*y_sign
                if y_sign == 0:
                    break

    def on_cancel(self, event):
        if self.linelist:
            for line in self.linelist:
                line.remove()
        self.linelist = []
        
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

        total_xrange = self.datafile.Xrange
        total_yrange = self.datafile.Yrange

        if self.linelist:
            for line in self.linelist:
                line.remove()

        self.linelist = []

        if self.radioy.GetValue():

            x_start = self.x_minspin.GetValue()
            x_end = self.x_maxspin.GetValue()

            sign = np.sign(x_end-x_start)

            # If xstart == xend, sign should be 0

            x_step = self.x_intervalspin.GetValue()*sign

            y_start = self.y_minspin.GetValue()
            y_end = self.y_maxspin.GetValue()

            position = x_start
            while position*sign <= x_end*sign:
                self.linelist.append(self.axes.plot([position,position],[y_start,y_end])[0])
                position += x_step
                if x_step == 0:
                    break

        if self.radiox.GetValue():

            y_start = self.y_minspin.GetValue()
            y_end = self.y_maxspin.GetValue()
            sign = np.sign(y_end-y_start)

            y_step = self.y_intervalspin.GetValue()*sign

            x_start = self.x_minspin.GetValue()
            x_end = self.x_maxspin.GetValue()


            position = y_start
            while position*sign <= y_end*sign:
                self.linelist.append(self.axes.plot([x_start,x_end],[position,position])[0])

                position += y_step
                if y_step == 0:
                    break

        self.canvas.draw()
