"""
Adaptive_Threshold
~~~~~~~~~~~~~~~~~~

A mod to extract prominent features from the data.
The widget provides two FloatSpin controls
to specify the size of the region where the peak value is compared to
and a minimum height of a possible peak.

"""
import numpy as np
import logging

from colorview2d import imod

from skimage.filter import threshold_adaptive
from skimage import img_as_float


class Adaptive_Threshold(imod.IMod):
    """
    The mod class. The apply routine contains the logic for applying
    the adaptive threshold filter to the data.
    
    :ivar args: A tuple containing the blocksize and the offset.
    """
    def __init__(self):
        imod.IMod.__init__(self)
        self.default_args = (2.,0.)

    def do_apply(self, data, modargs):
        """
        To apply the mod we use the adaptive threshold routine of
        the :module:`skimage.filter`.
        The threshold is calculated from
        
        threshold = (1+offset)*mean

        where offset is the value defined via the widget.
        Note that the result is a binary image with values
        0 and 1.

        Args
            data (colorview2d.Data): The data.
            modargs (tuple): First argument is the blocksize (integer), second
                             argument ist the offset for the threshold (float)
        """

        def func(arr):
            return (1 + modargs[1]) * arr.mean()
        
        newZ = img_as_float(
            threshold_adaptive(np.abs(data.zdata), modargs[0], method='generic', param=func))
        
        # Only if the array contains at least two different values
        # we really apply the filter
        if newZ.min() != newZ.max():
            data.zdata = newZ
        else:
            logging.info('Adaptive thresholding not applied, filter parameters blocksize %d'
                         ' and offset %d not sensitive to features in the data.', modargs[0], modargs[1])

