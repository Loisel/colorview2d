#!/bin/python

import scipy as sp

from scipy.ndimage.filters import gaussian_filter

from scipy import optimize


class modification:
    title = ""
    def __eq__(self, other):
        return self.title == other.title


class smooth(modification):

    title = "lowpass"
    
    def __init__(self,sizex,sizey):

        self.sizex = sizex
        self.sizey = sizey

    
    def apply_mod(self,datafile):
     """ blurs the image by convolving with a gaussian kernel of typical
         size n. The optional keyword argument ny allows for a different
         size in the y direction.
     """
     

     datafile.Zdata = gaussian_filter(datafile.Zdata,(self.sizex,self.sizey))


class deriv(modification):

    title = "deriv"

    
    def apply_mod(self,datafile):

        dy = datafile.dY

        dydata = -sp.diff(datafile.Zdata,axis=0)

        datafile.Zdata[:-1] = dydata
        datafile.Zdata[-1] = datafile.Zdata[-2]

 
	
