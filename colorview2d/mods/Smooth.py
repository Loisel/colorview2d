"""
This mod performs a gaussian filter on the data. The window size for the
filter is specified by wx.lib.masked.NumCtrl widgets.
"""

from scipy.ndimage.filters import gaussian_filter
from colorview2d import imod


class Smooth(imod.IMod):
    """
    The modification class. Convolutes a gaussian window of size

    args = (xsize, ysize)

    with the datafile array.
    """
    def __init__(self):
        imod.IMod.__init__(self)
        self.default_args = (0., 0.)

    def do_apply(self, datafile, args):
        datafile.zdata = gaussian_filter(datafile.zdata, args)


