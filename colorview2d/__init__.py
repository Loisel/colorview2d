"""
*colorview2d* is a plotting tool intended to be used with
scientific data (with dimensionful axes)
with an easily extendable data modification (or filtering) toolbox.

Tested with Python 2.7

Dependencies
------------
numpy, scipy, matplotlib, pyyaml, scikit.image

Homepage
--------
https://github.com/Loisel/colorview2d

Copyright (c) 2016 Alois Dirnaichner <alo.dir@gmail.com>
"""

__author__ = "Alois Dirnaichner <alo.dir@gmail.com"
__license__ = "GNU GPLv3"
__version__ = "0.6.1"
__all__ = ["datafile", "cvfig", "fileloaders"]

from colorview2d.datafile import Datafile
from colorview2d.cvfig import CvFig
from colorview2d.imod import IMod
import colorview2d.fileloaders
