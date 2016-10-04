"""This mod flips the the data along x or y direction."""

from colorview2d import imod


class Flip(imod.IMod):
    """
    The mod class to flip the data.
    """
    def __init__(self):
        imod.IMod.__init__(self)
        self.default_args = (True, )

    def do_apply(self, data, modargs):
        if modargs:
            data.flip_lr()
        else:
            data.flip_ud()


