import wx
import numpy as np

from Mods import IMod
#from yapsy.IPlugin import IPlugin

class Derive(IMod.IMod):

    def __init__(self):
        print "Init called, derive"
        IMod.IMod.__init__(self)
        
    def apply(self):

        datafile = self.view.datafile
        dy = datafile.dY

        dydata = np.diff(datafile.Zdata,axis=0)

        datafile.Zdata[:-1] = dydata
        datafile.Zdata[-1] = datafile.Zdata[-2]

        datafile.set_Zdata(datafile.Zdata)
