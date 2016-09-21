from colorview2d import imod
from colorview2d import modwidget
from colorview2d import floatspin #FloatSpin,EVT_FLOATSPIN

import logging
import numpy as np

import wx

try:
    from skimage.filter import threshold_adaptive
    from skimage import img_as_float
except ImportError:
    logging.info('The skimage package is missing. You can not use the adaptive threshold mod.')


"""
Adaptive_Threshold
~~~~~~~~~~~~~~~~~~

A mod to extract prominent features from the datafile.
The widget provides two FloatSpin controls
to specify the size of the region where the peak value is compared to
and a minimum height of a possible peak.

"""

class Adaptive_ThresholdWidget(modwidget.ModWidget):
    """
    The widget hosting the FloatSpin controls and the labels.

    :ival blocksize: integer speciying the size of the disk
    :ival offset: float that determines the minimum offset
    """
    def __init__(self,mod,panel):
        modwidget.ModWidget.__init__(self,mod,panel)

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
            self.mod.args((self.blocksize_spin.GetValue(),self.offset_spin.GetValue()))
            self.add_mod()
        else:
            self.remove_mod()

    def update(self):
        """
        Updates the widget with the arguments of the mod.
        The super class' update is called. 
        """
        modwidget.ModWidget.update(self)
        self.blocksize_spin.SetValue(self.mod.args[0])
        self.offset_spin.SetValue(self.mod.args[1])
        
    def on_floatspin(self,event):
        """
        Handles changes to the floatspin widget in case the mod is active.

        :param event: The event
        :type event: :class:`EVT_FLOATSPIN`
        """
        if self.mod.active:
            self.remove_mod()
            self.mod.args((self.blocksize_spin.GetValue(),self.offset_spin.GetValue()))
            self.add_mod()
            

class Adaptive_Threshold(imod.IMod):
    """
    The mod class. The apply routine contains the logic for applying
    the adaptive threshold filter to the datafile.
    
    :ivar args: A tuple containing the blocksize and the offset.
    """
    def __init__(self):
        imod.IMod.__init__(self)
        self.default_args = (2.,0.)

    def do_apply(self, datafile, modargs):
        """
        To apply the mod we use the adaptive threshold routine of
        the :module:`skimage.filter`.
        The threshold is calculated from
        
        threshold = (1+offset)*mean

        where offset is the value defined via the widget.
        Note that the result is a binary image with values
        0 and 1.

        Args
            datafile (gpfile): The datafile.
            modargs (tuple): First argument is the blocksize (integer), second
                             argument ist the offset for the threshold (float)
        """

        def func(arr):
            return (1 + modargs[1]) * arr.mean()
        
        newZ = img_as_float(
            threshold_adaptive(np.abs(datafile.zdata), modargs[0], method='generic', param=func))
        
        # Only if the array contains at least two different values
        # we really apply the filter
        if newZ.min() != newZ.max():
            datafile.zdata = newZ

        
        
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
