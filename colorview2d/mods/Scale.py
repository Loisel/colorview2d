"""A mod to scale the data."""
from colorview2d import imod

class Scale(imod.IMod):
    """
    The mod class to scale the values in the 2d data array
    according to the value entered in the widget:

    args (float): The float that is multiplied with the data array.
    """
    def __init__(self):
        imod.IMod.__init__(self)
        self.args = self.default_args = 1.

    def do_apply(self, data, args):
        data.zdata = data.zdata * args
