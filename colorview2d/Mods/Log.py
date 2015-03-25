import numpy as np

from colorview2d import imod

"""
This mod performs a derivation of the datafile with respect to the y-axis.
"""


class Log(imod.IMod):
    """
    The mod class to apply the derivative of the datafile array with respect
    to the y-axis.
    """

    def __init__(self):
        imod.IMod.__init__(self)
        
    def apply(self,datafile):

        logdata = datafile.Zdata
        logdata[logdata <= 0.] = 1.
        logdata = np.log(logdata)
        datafile.set_Zdata(logdata)
