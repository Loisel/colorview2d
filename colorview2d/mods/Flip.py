"""This mod flips the the datafile along x or y direction."""

from colorview2d import imod


class Flip(imod.IMod):
    """
    The mod class to flip the datafile.
    """
    def __init__(self):
        imod.IMod.__init__(self)
        self.default_args = (True, )

    def do_apply(self, datafile, modargs):
        if modargs:
            datafile.flip_lr()
        else:
            datafile.flip_ud()


