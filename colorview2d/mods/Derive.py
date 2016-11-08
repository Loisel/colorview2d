"""
This mod performs a derivation of the data with respect to the y-axis.
"""
import numpy as np

from colorview2d import imod



class Derive(imod.IMod):
    """
    The mod class to apply the derivative of the data array with respect
    to the y-axis. The size of the data array along the y-axis is reduced by 1.
    """
    def __init__(self):
        imod.IMod.__init__(self)

    def do_apply(self, data, modargs):
        """Apply the derivative to the data array and adjust the bounds."""
        dy = data.dy
        # diff
        data.zdata = np.diff(data.zdata, axis=0)
        # new bounds
        data.yrange_bounds = (
            data.yrange_bounds[0] + dy/2.,
            data.yrange_bounds[1] - dy/2.)

