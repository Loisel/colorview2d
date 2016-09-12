import numpy as np

from colorview2d import imod

"""
This mod performs a derivation of the datafile with respect to the y-axis.
"""


class Derive(imod.IMod):
    """
    The mod class to apply the derivative of the datafile array with respect
    to the y-axis.
    """

    def __init__(self):
        imod.IMod.__init__(self)

    def do_apply(self, datafile, modargs):
        dydata= datafile.Zdata
        dydata[:-1] = np.diff(datafile.Zdata, axis=0)

        dydata[-1] = dydata[-2]

        datafile.set_Zdata(dydata)
