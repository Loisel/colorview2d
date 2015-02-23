from colorview2d import IMod
from colorview2d import ModWidget
from colorview2d import floatspin #FloatSpin,EVT_FLOATSPIN

import numpy as np

import wx

from skimage.filter import threshold_adaptive
from skimage import img_as_float


"""
Adaptive_Threshold
~~~~~~~~~~~~~~~~~~

A mod to extract prominent features from the datafile.
The widget provides two FloatSpin controls
to specify the size of the region where the peak value is compared to
and a minimum height of a possible peak.

"""

class Adaptive_ThresholdWidget(ModWidget.ModWidget):
    """
    The widget hosting the FloatSpin controls and the labels.

    :ival blocksize: integer speciying the size of the disk
    :ival offset: float that determines the minimum offset
    """
    def __init__(self,mod,panel):
        ModWidget.ModWidget.__init__(self,mod,panel)

        self.widgetlist = []
        self.blocksize_label = wx.StaticText(self.panel, wx.ID_ANY,
            "Blocksize: ")
        self.widgetlist.append(self.blocksize_label)
        self.blocksize_spin = floatspin.FloatSpin(self.panel, name='blocksize',
                                                    value = 0,
                                                    digits = 0
                                                )

        self.widgetlist.append(self.blocksize_spin)
        self.offset_label = wx.StaticText(self.panel, wx.ID_ANY,
            " Rel. offset: ")
        self.offset_spin = floatspin.FloatSpin(self.panel, name='offset',
            digits = 3
            )
        self.offset_spin.SetFormat("%e")
        self.widgetlist.append(self.offset_label)
        self.widgetlist.append(self.offset_spin)

        for widget in self.widgetlist:
            self.Add(widget,0,flag=self.flags)


        self.panel.Bind(floatspin.EVT_FLOATSPIN,self.on_floatspin)


    def on_chk(self,event):
        """
        Handles event fired when the checkbox is clicked.
        The values in the :class:`FloatSpin` controls are transfered to the mod.
        The mod is activated.

        :param event: The :class:`wx.EVT_CHECKBOX` event.
        """
        if self.chk.GetValue():
            self.mod.set_args((self.blocksize_spin.GetValue(),self.offset_spin.GetValue()))
            self.mod.activate()
        else:
            self.mod.deactivate()

    def update(self):
        """
        Updates the widget with the arguments of the mod.
        The super class' update is called. 
        """
        ModWidget.ModWidget.update(self)
        self.blocksize_spin.SetValue(self.mod.args[0])
        self.offset_spin.SetValue(self.mod.args[1])
        
    def on_floatspin(self,event):
        """
        Handles changes to the floatspin widget in case the mod is active.

        :param event: The event
        :type event: :class:`EVT_FLOATSPIN`
        """
        if self.mod.active:
            self.mod.deactivate()
            self.mod.set_args((self.blocksize_spin.GetValue(),self.offset_spin.GetValue()))
            self.mod.activate()
            

class Adaptive_Threshold(IMod.IMod):
    """
    The mod class. The apply routine contains the logic for applying
    the adaptive threshold filter to the datafile.
    
    :ivar args: A tuple containing the blocksize and the offset.
    """
    def __init__(self):
        IMod.IMod.__init__(self)
        self.args = self.default_args = (2.,0.)

    def apply(self,datafile):
        """
        To apply the mod we use the adaptive threshold routine of
        the :module:`skimage.filter`.
        The threshold is calculated from
        
        threshold = (1+offset)*mean

        where offset is the value defined via the widget.
        Note that the result is a binary image with values
        0 and 1.

        :param datafile gpfile: The datafile.
        """

        func = lambda arr: (1+self.args[1])*arr.mean()
        newZ = img_as_float(threshold_adaptive(np.abs(datafile.Zdata),self.args[0],method='generic', param=func))
        
        # Only if the array contains at least two different values
        # we really apply the filter
        if newZ.min() != newZ.max():
            datafile.set_Zdata(newZ)

        
        
    def create_widget(self,panel):
        """
        The widget is created and returned.

        :param panel wx.Panel: The panel the widget is created on.
        :returns: The widget.
        :rtype: :class:`CropWidget`
        """
        self.panel = panel
        self.widget = Adaptive_ThresholdWidget(self,self.panel)
        return self.widget
