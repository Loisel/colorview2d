"""This mod replaces the negative values with their positive counterparts."""
import numpy as np

from colorview2d import imod


class Absolute(imod.IMod):
    """
    The mod class to calculate the absolute value of the data.
    """

    def __init__(self):
        imod.IMod.__init__(self)
        
    def do_apply(self, data, modargs):
        """Replace the array by its absolute valued version."""
        data.zdata = np.absolute(data.zdata)
