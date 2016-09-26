"""This mod replaces the negative values with their positive counterparts."""
import numpy as np

from colorview2d import imod


class Absolute(imod.IMod):
    """
    The mod class to calculate the absolute value of the datafile.
    """

    def __init__(self):
        imod.IMod.__init__(self)
        
    def do_apply(self, datafile, modargs):
        """Replace the array by its absolute valued version."""
        datafile.zdata = np.absolute(datafile.zdata)
