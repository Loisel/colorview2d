import View
import IMod

import numpy as np

"""
This mod performs a derivation of the datafile with respect to the y-axis.
"""


class Derive(IMod.IMod):
    """
    The mod class to apply the derivative of the datafile array with respect
    to the y-axis.
    """

    def __init__(self):
        IMod.IMod.__init__(self)
        
    def apply(self,datafile):

        dydata= datafile.Zdata
        dydata[:-1] = np.diff(datafile.Zdata,axis=0)

        dydata[-1] = dydata[-2]

        datafile.set_Zdata(dydata)
