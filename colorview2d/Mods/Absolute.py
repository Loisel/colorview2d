import numpy as np

from colorview2d import imod

"""
This mod replaces the negative values with their positive counterparts.
"""


class Absolute(imod.IMod):
    """
    The mod class to calculate the absolute value of the datafile.
    """

    def __init__(self):
        imod.IMod.__init__(self)
        
    def do_apply(self, datafile, modargs):
        datafile.set_Zdata(np.absolute(datafile.Zdata))
