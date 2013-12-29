#!/bin/python

import scipy as sp

from scipy.ndimage.filters import gaussian_filter

from scipy import optimize


class modification:
    title = ""
    def __eq__(self, other):
        return self.title == other.title


class smooth(modification):
    """ blurs the image by convolving with a 2D gaussian kernel of size sizex * sizey.
    """

    title = "lowpass"
    
    def __init__(self,sizex,sizey):

        self.sizex = sizex
        self.sizey = sizey

    
    def apply_mod(self,datafile):     

     datafile.update(gaussian_filter(datafile.Zdata,(self.sizex,self.sizey)))


class deriv(modification):

    title = "deriv"

    
    def apply_mod(self,datafile):

        dy = datafile.dY

        dydata = -sp.diff(datafile.Zdata,axis=0)

        datafile.Zdata[:-1] = dydata
        datafile.Zdata[-1] = datafile.Zdata[-2]

        datafile.update(datafile.Zdata)

class adaptive_threshold(modification):

    title = "adaptive-threshold"

    def __init__(self,blocksize,offset):

        self.blocksize = blocksize
        self.offset = offset

    
    def apply_mod(self,datafile):

        from skimage.filter import threshold_adaptive
        from skimage import img_as_float

        datafile.update(img_as_float(threshold_adaptive(datafile.Zdata,self.blocksize,method='mean',offset=self.offset)))
