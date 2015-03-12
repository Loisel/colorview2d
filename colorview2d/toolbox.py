#!/bin/python

import scipy as sp
import numpy as np
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.filters import median_filter
from scipy import optimize


class modification():
    removeOnLoadFile = False
    
    def __repr__(self):
        return "{}{}".format(self.title(),self.__dict__)

    def title(self):
        return self.__class__.__name__

    
class smooth(modification):
    """ blurs the image by convolving with a 2D gaussian kernel of size sizex * sizey.
    """

    def __init__(self,widget,sizex,sizey):
        self.widget = widget
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

    def __init__(self,widget,blocksize,offset):

        self.widget = widget
        self.blocksize = blocksize
        self.offset = offset


    def apply_mod(self,datafile):

        from skimage.filter import threshold_adaptive
        from skimage import img_as_float

        datafile.set_Zdata(img_as_float(threshold_adaptive(datafile.Zdata,self.blocksize,method='mean',offset=self.offset)))

class median(modification):

    def __init__(self,widget,sizex,sizey):
        self.size = (sizex,sizey)

    def apply_mod(self,datafile):
        datafile.set_Zdata(median_filter(datafile.Zdata,size=self.size))
        
class scale(modification):

    def __init__(self,widget,zscale):

        self.widget = widget
        self.zscale = zscale

    def __repr__(self):
        return "{}(zscale={})".format(self.title(),self.zscale)

    def apply_mod(self,datafile):

        datafile.set_Zdata(datafile.Zdata*self.zscale)

class crop(modification):

    removeOnLoadFile = True

    def __init__(self,widget,xleft,xright,ybottom,ytop):

        self.widget = widget
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



def peakdetect2(y_axis, x_axis, region = 20, delta_rel = 5, delta_abs = 0, dynamic_threshold = False, delta_rel_step = 1.):
    """
    Peak finding algorhithm that supports relative and
    absolute peak heights above an average value that is taken
    over a given region of points.
    The maxima are found over the absolute values of the input array.
    In the relative peak height mode, it can operate recursively
    reducing the relative magnitude by delta_rel_step in each recursion.

    Args:
      y_axis (np.ndarray): A numpy array with the values on the y axis.
                           The absolute values of the contents are used for the analysis.
      x_axis (np.ndarray): A numpy array with the values on the x axis.
      region (int): Integer size of region over which the average is taken.
                    It will also determine the minimum distance between peaks.
      delta_rel (float): Relative height of a possible maximum over the average.
      delta_abs (float): Absolute height of a possible maximum over the average.
                         Overrides the choice of delta_rel
      dynamic_threshold (boolean): Switches the dynamic recursion on and off.
      delta_rel_step (float): If the dynamic recursion is switched on, this values
                              determines the step size that is substracted from delta_rel
                              during each recursion.

    Returns:
      max_peaks (np.array): A numpy array where each line contains the value on the x-axis,
                            the value on the y-axis and the index on the x-range:
                            ...
                            [x_max, y_max, max_index]
                            ...
    """
    max_peaks = []
    maxindex = None
    maxi = -np.Inf
    found_new_max = False

    y_axis = np.abs(y_axis)

    for index in range(x_axis.shape[0]):
        
        # let us look at the first points
        if index < region/2:
            avg = np.average(y_axis[:region/2])
        elif index > x_axis.shape[0]-region/2:
            avg = np.average(y_axis[-region/2:])
        else:
            avg = np.average(y_axis[index-region/2:index+region/2])

        if(y_axis[index] > maxi):
            if delta_abs > 0 and y_axis[index] > avg + delta_abs:
                maxi = y_axis[index]
                maxindex = index
                max_peaks.append([x_axis[index], maxi, maxindex])
                print "call"

            elif y_axis[index] > avg*delta_rel:
                #import pdb;pdb.set_trace()
                maxi = y_axis[index]
                maxindex = index
                found_new_max = True

        if maxindex:
            if maxindex + region/2 < index and found_new_max:
                max_peaks.append([x_axis[maxindex], maxi, maxindex])
                maxi = -np.Inf
                found_new_max = False

    if dynamic_threshold and len(max_peaks) == 0 and delta_rel > 0:
        # print "Going into recursion: delta_rel = {}".format(delta_rel-delta_rel_step)
        return peakdetect2(y_axis, x_axis, region = region, delta_rel = delta_rel - delta_rel_step, dynamic_threshold = True)
                
    return np.array(max_peaks)
        


def peakdetect(y_axis, x_axis = None, lookahead = 300, delta=0):
    """
    Converted from/based on a MATLAB script at:
    http://billauer.co.il/peakdet.html
    function for detecting local maximas and minmias in a signal.
    Discovers peaks by searching for values which are surrounded by lower
    or larger values for maximas and minimas respectively
    keyword arguments:
    y_axis -- A list containg the signal over which to find peaks
    x_axis -- (optional) A x-axis whose values correspond to the y_axis list
    and is used in the return to specify the postion of the peaks. If
    omitted an index of the y_axis is used. (default: None)
    lookahead -- (optional) distance to look ahead from a peak candidate to
    determine if it is the actual peak (default: 200)
    '(sample / period) / f' where '4 >= f >= 1.25' might be a good value
    delta -- (optional) this specifies a minimum difference between a peak and
    the following points, before a peak may be considered a peak. Useful
    to hinder the function from picking up false peaks towards to end of
    the signal. To work well delta should be set to delta >= RMSnoise * 5.
    (default: 0)
    delta function causes a 20% decrease in speed, when omitted
    Correctly used it can double the speed of the function
    return -- two lists [max_peaks, min_peaks] containing the positive and
    negative peaks respectively. Each cell of the lists contains a tupple
    of: (position, peak_value)
    to get the average peak value do: sp.mean(max_peaks, 0)[1] on the
    results to unpack one of the lists into x, y coordinates do:
    x, y = zip(*tab)
    """
    max_peaks = []
    min_peaks = []
    dump = [] #Used to pop the first hit which almost always is false
       
    # store data length for later use
    length = len(y_axis)
    
    
    #perform some checks
    if lookahead < 1:
        raise ValueError, "Lookahead must be '1' or above in value"
    if not (sp.isscalar(delta) and delta >= 0):
        raise ValueError, "delta must be a positive number"
    
    #maxima and minima candidates are temporarily stored in
    #mx and mn respectively
    mn, mx = sp.Inf, -sp.Inf
    
    #Only detect peak if there is 'lookahead' amount of points after it
    for index, (x, y) in enumerate(zip(x_axis[:-lookahead],
                                        y_axis[:-lookahead])):
        if y > mx:
            mx = y
            mxpos = x
        if y < mn:
            mn = y
            mnpos = x
        
        ####look for max####
        if y < mx-delta and mx != sp.Inf:
            #Maxima peak candidate found
            #look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index+lookahead].max() < mx:
                max_peaks.append([mxpos, mx,index])
                dump.append(True)
                #set algorithm to only find minima now
                mx = sp.Inf
                mn = sp.Inf
                if index+lookahead >= length:
                    #end is within lookahead no more peaks can be found
                    break
                continue
            #else: #slows shit down this does
            # mx = ahead
            # mxpos = x_axis[sp.where(y_axis[index:index+lookahead]==mx)]
        
        ####look for min####
        if y > mn+delta and mn != -sp.Inf:
            #Minima peak candidate found
            #look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index+lookahead].min() > mn:
                min_peaks.append([mnpos, mn,index])
                dump.append(False)
                #set algorithm to only find maxima now
                mn = -sp.Inf
                mx = -sp.Inf
                if index+lookahead >= length:
                    #end is within lookahead no more peaks can be found
                    break
            #else: #slows shit down this does
            # mn = ahead
            # mnpos = x_axis[sp.where(y_axis[index:index+lookahead]==mn)]
    
    
    #Remove the false hit on the first value of the y_axis
    try:
        if dump[0]:
            max_peaks.pop(0)
        else:
            min_peaks.pop(0)
        del dump
    except IndexError:
        #no peaks were found, should the function return empty lists?
        pass
        
    return [max_peaks, min_peaks]
