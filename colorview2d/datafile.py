#!/bin/python
"""
A module to handle 3D datafiles.

A datafile consists of a 2d array and x and y axes.
The class provides methods to rotate, flipp, copy and save
the datafile.


Example
-------
::

    file = Datafile(np.random.random(100, 100))
    file.rotate_cw()
    file.report()
    file.save('newdata.dat')


"""

import copy
import logging
import numpy as np


class Datafile(object):
    """
    A data file object.

    Provide a 2d array of data. The ranges on x and y axis can be specified.
    If they are not, the ranges are enumerating the number of rows and columns,
    respectively.


    Attributes:

        zdata (numpy.array):  The two dimensional numpy arrray containing the actual data.

        xrange (numpy.array): A one dimensional array representing the x axis range.
        yrange (numpy.array): A one dimensional array representing the y axis range.

    Properties:
    xleft: The value on the left of the x axis.
    xright: The value on the right of the x axis.
    ytop: The values on the top of the y axis.
    ybottom: The values on the bottom of the y axis.

    zmin: The min values of the 2d array.
    zmax: The max values of the 2d array.

    xmin: The min values of the x axis range.
    xmax: The max values of the x axis range.
    ymin: The min values of the y axis range.
    ymax: The max values of the y axis range.
      
    """

    def __init__(self, data, ranges=None):
        """Initialize a datafile object.
        
        Args:
            data (numpy.array): the two-dimensional array holding the data.
            ranges (tuple): x and y ranges, numpy.arrays
        
        """

        self._zdata = data
        self._xrange = None
        self._yrange = None

        try:
            self.xyrange = ranges
        except (IndexError, ValueError, TypeError):
            logging.warn('Ranges are not specified correctly. Using default ranges.')
            self.xyrange = (np.arange(self._zdata.shape[1]), np.arange(self._zdata.shape[0]))
            

    @property
    def xleft(self):
        return self._xrange[0]

    @property
    def xright(self):
        return self._xrange[-1]

    @property
    def ytop(self):
        return self._yrange[-1]

    @property
    def ybottom(self):
        return self._yrange[0]

    @property
    def xmin(self):
        return np.amin(self._xrange)

    @property
    def xmax(self):
        return np.amax(self._xrange)

    @property
    def dx(self):
        return (self._xrange[-1] - self._xrange[0])/(self._xrange.size-1)

    @property
    def dy(self):
        return (self._yrange[-1] - self._yrange[0])/(self._yrange.size-1)

    @property
    def ymin(self):
        return np.amin(self._yrange)

    @property
    def ymax(self):
        return np.amax(self._yrange)

    @property
    def zmin(self):
        return np.amin(self._zdata)

    @property
    def zmax(self):
        return np.amax(self._zdata)

    @property
    def zdata(self):
        return self._zdata

    @zdata.setter
    def zdata(self, zdata):
        self._zdata = zdata

    @property
    def yrange(self):
        return self._yrange

    @yrange.setter
    def yrange(self, yrange):
        if yrange.size != self._zdata.shape[0]:
            raise ValueError("Provided yrange is not compatible with the datafile.")
        self._yrange = yrange

    @property
    def xrange(self):
        return self._xrange
    
    @xrange.setter
    def xrange(self, xrange):
        if xrange.size != self._zdata.shape[1]:
            raise ValueError("Provided xrange is not compatible with the datafile.")
        self._xrange = xrange

    @property
    def xyrange(self):
        return (self._xrange, self._yrange)
    
    @xyrange.setter
    def xyrange(self, ranges):
        """
        Specify the x and y ranges of the datafile.

        :param xrange: One dimensional numpy array
                       with the same length as the width of the data.
        :type xrange: :class:`numpy.ndarray`
        :param yrange: One dimensional numpy array
                       with the same length as the height of the data.
        :type yrange: :class:`numpy.ndarray`
        """

        self.xrange = ranges[0]
        self.yrange = ranges[1]

    def report(self):
        """
        Print a datafile report to the standart output.
        """

        print(
            "There are {} lines and {} columns in the datafile.\n"
            .format(self._zdata.shape[0], self._zdata.shape[1]))
        print(
            "X-axis range from {} to {}".format(self.xleft, self.xright),
            "Y-axis range from {} to {}".format(self.ybottom, self.ytop))

    def deep_copy(self):
        """
        Deep copy the datafile object.

        :returns: A copy of the datafile object.
        """

        tmp = copy.deepcopy(self)
        tmp.zdata = np.copy(self._zdata)
        tmp.xrange = np.copy(self._xrange)
        tmp.yrange = np.copy(self._yrange)

        return tmp


    def rotate_cw(self):
        """
        Rotate the datafile clockwise. The axes are updated as well.
        """
        self.zdata = np.rot90(self._zdata,k=1)
        self.xyrange = (self._yrange, self._xrange[::-1])

    def rotate_ccw(self):
        """
        Rotate the datafile counter-clockwise. The axes are updated as well.
        """
        self.zdata = np.rot90(self._zdata,k=3)
        self.xyrange = (self._yrange[::-1], self._xrange)

    def flip_lr(self):
        """
        Flip the left and the right side of the datafile. The axes are updated as well.
        """
        self.zdata = np.fliplr(self._zdata)
        self.xyrange = (self._xrange[::-1], self._yrange)

    def flip_ud(self):
        """
        Flip the up and the down side of the datafile. The axes are updated as well.
        """
        self.zdata = np.flipud(self._zdata)
        self.xyrange = (self._xrange, self._yrange[::-1])


    def crop(self, xleft, xright, ybottom, ytop):
        """
        Crop the datafile to a subset of the array specifiying the corners of the subset in
        units of the axes ranges.

        :param xleft:
        :param xright:
        :param ybottom:
        :param ytop:
       
        """
        xleft_idx = self.get_xrange_idx(xleft)
        xright_idx = self.get_xrange_idx(xright)
        ybottom_idx = self.get_yrange_idx(ybottom)
        ytop_idx = self.get_yrange_idx(ytop)

        # import ipdb;ipdb.set_trace()
        try:
            self.zdata = self._zdata[ybottom_idx:ytop_idx + 1, xleft_idx:xright_idx + 1]
            self.xyrange = (
                self._xrange[xleft_idx:xright_idx + 1], self._yrange[ybottom_idx:ytop_idx + 1])
        except IndexError as ie:
            print "Value not in data range: ", ie

    def get_xrange_idx(self, value):
        """
        Return the nearest index of a value within the x axis range.

        Args:
            value: A value in the range of the x axis

        Returns: The closest index on the x axis range.
        """
        return (np.abs(self._xrange - value)).argmin()   

    def get_yrange_idx(self, value):
        """
        Return the nearest index of a value within the y axis range.

        Args:
            value: A value in the range of the y axis

        Returns: The closest index on the y axis range.
        """
        return (np.abs(self._yrange - value)).argmin()











