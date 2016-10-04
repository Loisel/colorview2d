"""This mod calculates the logarithm of the data.zdata array.
"""
import numpy as np

from colorview2d import imod



class Log(imod.IMod):
    """
    The mod class to apply the derivative of the data array with respect
    to the y-axis.
    """

    def __init__(self):
        imod.IMod.__init__(self)

    def do_apply(self, data, modargs):
        """Calculate the natural logarithm of the data. Please make sure the
        data array does not contain negative values.
        """
        data.zdata = np.log(data.zdata)


