"""
This mod performs a 90 deg clockwise or anti-clockwise rotation of the data.
"""
from colorview2d import imod



class Rotate(imod.IMod):
    """
    The mod class to apply the rotation.
    """

    def __init__(self):
        imod.IMod.__init__(self)
        self.args = self.default_args = True

    def do_apply(self, data, modargs):
        """Apply a clockwise or anti-clockwise rotation of the data.

        Args:
            modargs (tuple): Supply a boolean value, if True, rotate clockwise.
                otherwise counter-clockwise.
        """
        if modargs:
            data.rotate_cw()
        else:
            data.rotate_ccw()
