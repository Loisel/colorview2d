"""
This mod performs a median filter on the data. The window size for the
filter is specified by wx.lib.masked.NumCtrl widgets.
"""
from colorview2d import imod

from scipy.ndimage.filters import median_filter



class Median(imod.IMod):
    """Median filter class."""
    def __init__(self):
        imod.IMod.__init__(self)
        self.default_args = (0., 0.)

    def do_apply(self, data, modargs):
        """ Applies a median filter to the data."""
        data.zdata = median_filter(data.zdata, size=modargs)
