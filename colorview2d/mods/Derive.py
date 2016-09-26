"""
This mod performs a derivation of the datafile with respect to the y-axis.
"""
import numpy as np

from colorview2d import imod



class Derive(imod.IMod):
    """
    The mod class to apply the derivative of the datafile array with respect
    to the y-axis.
    """
    def __init__(self):
        imod.IMod.__init__(self)

    def do_apply(self, datafile, modargs):
        dydata = datafile.zdata
        dydata[:-1] = np.diff(datafile.zdata, axis=0)

        dydata[-1] = dydata[-2]

        datafile.zdata = dydata
