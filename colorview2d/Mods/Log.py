import numpy as np
import logging

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
        
    def do_apply(self, datafile, modargs):
        logdata = datafile.zdata
        if logdata.any() <= 0:
            logging.warn('Can not apply log to negative valued array.')
        else:
            logdata = np.log(logdata)
            datafile.zdata = logdata
