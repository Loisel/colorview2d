#!/bin/python

import scipy as sp

from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.filters import median_filter
import yaml
from scipy import optimize


class modification(yaml.YAMLObject):
    removeOnLoadFile = False

    def __repr__(self):
        return "{}{}".format(self.title(),self.__dict__)

    def title(self):
        return self.__class__.__name__

    
class smooth(modification):
    """ blurs the image by convolving with a 2D gaussian kernel of size sizex * sizey.
    """

    def __init__(self,sizex,sizey):

        self.sizex = sizex
        self.sizey = sizey


    def apply_mod(self,datafile):

        datafile.set_Zdata(gaussian_filter(datafile.Zdata,(self.sizex,self.sizey)))


class deriv(modification):

    def apply_mod(self,datafile):

        dy = datafile.dY

        dydata = sp.diff(datafile.Zdata,axis=0)

        datafile.Zdata[:-1] = dydata
        datafile.Zdata[-1] = datafile.Zdata[-2]

        datafile.set_Zdata(datafile.Zdata)



class adaptive_threshold(modification):

    def __init__(self,blocksize,offset):

        self.blocksize = blocksize
        self.offset = offset


    def apply_mod(self,datafile):

        from skimage.filter import threshold_adaptive
        from skimage import img_as_float

        datafile.set_Zdata(img_as_float(threshold_adaptive(datafile.Zdata,self.blocksize,method='mean',offset=self.offset)))

class median(modification):

    def __init__(self,sizex,sizey):
        self.size = (sizex,sizey)

    def apply_mod(self,datafile):
        datafile.set_Zdata(median_filter(datafile.Zdata,size=self.size))
        
class scale(modification):

    def __init__(self,zscale):

        self.zscale = zscale

    def __repr__(self):
        return "{}(zscale={})".format(self.title(),self.zscale)

    def apply_mod(self,datafile):

        datafile.set_Zdata(datafile.Zdata*self.zscale)

class crop(modification):

    removeOnLoadFile = True

    def __init__(self,xleft,xright,ybottom,ytop):

        self.xleft = xleft
        self.xright = xright
        self.ybottom = ybottom
        self.ytop = ytop

    def apply_mod(self,datafile):
        
        xleft_idx = datafile.get_xrange_idx(self.xleft)
        xright_idx = datafile.get_xrange_idx(self.xright)
        ybottom_idx = datafile.get_yrange_idx(self.ybottom)
        ytop_idx = datafile.get_yrange_idx(self.ytop)

        #print "left {} right {} bottom {} top {}".format(xleft_idx,xright_idx,ybottom_idx,ytop_idx)
        #datafile.report()

        datafile.set_xyrange(datafile.Xrange[xleft_idx:xright_idx],datafile.Yrange[ybottom_idx:ytop_idx])
        datafile.set_Zdata(datafile.get_region(xleft_idx,xright_idx,ybottom_idx,ytop_idx))
