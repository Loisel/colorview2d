"""
Crop
~~~~

A mod to crop the data. The widget provides four FloatSpin controls
to specify the window (xleft, xright, ybottom, ytop).
A button can be used to specify set the original size in the controls.

"""
from colorview2d import imod

class Crop(imod.IMod):
    """
    The mod class. The apply routine contains the logic for cropping
    the data array to the new size
    
    :ivar args: A 4-tuple containing the corners of the cropped region.
    """
    def __init__(self):
        imod.IMod.__init__(self)
        self.default_args = (0., 0., 0., 0.)

    def do_apply(self, data, modargs):
        """
        To apply the mod we use the builtin crop routine of the data,
        a :class:`gpfile`.

        Args:
            data (colorview2d.Data): The datafile.
        """
        data.crop(modargs)
