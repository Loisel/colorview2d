"""
This mod performs a 90 deg clockwise or anti-clockwise rotation of the datafile.
"""
from colorview2d import imod



class Rotate(imod.IMod):
    """
    The mod class to apply the rotation.
    """

    def __init__(self):
        imod.IMod.__init__(self)
        self.args = self.default_args = True

    def do_apply(self, datafile, modargs):
        """Apply a clockwise or anti-clockwise rotation of the datafile.

        Args:
            modargs (tuple): Supply a boolean value, if True, rotate clockwise.
                otherwise counter-clockwise.
        """
        if modargs:
            datafile.rotate_cw()
        else:
            datafile.rotate_ccw()
