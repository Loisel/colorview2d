#!/bin/python
"""
A module to handle 3D datafiles with axes.

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

        x_range (numpy.array): A one dimensional array representing the x axis range.
        y_range (numpy.array): A one dimensional array representing the y axis range.

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
    def y_range(self):
        return self._yrange

    @y_range.setter
    def y_range(self, y_range):
        if y_range.size != self._zdata.shape[0]:
            raise ValueError("Provided yrange is not compatible with the datafile.")
        self._yrange = y_range

    @property
    def x_range(self):
        return self._xrange

    @x_range.setter
    def x_range(self, x_range):
        if x_range.size != self._zdata.shape[1]:
            raise ValueError("Provided xrange is not compatible with the datafile.")
        self._xrange = x_range

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

        self.x_range = ranges[0]
        self.y_range = ranges[1]

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
        tmp.x_range = np.copy(self._xrange)
        tmp.y_range = np.copy(self._yrange)

        return tmp


    def rotate_cw(self):
        """
        Rotate the datafile clockwise. The axes are updated as well.
        """
        self.zdata = np.rot90(self._zdata, k=1)
        self.xyrange = (self._yrange, self._xrange[::-1])

    def rotate_ccw(self):
        """
        Rotate the datafile counter-clockwise. The axes are updated as well.
        """
        self.zdata = np.rot90(self._zdata, k=3)
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
        xleft_idx = self.x_range_idx_by_val(xleft)
        xright_idx = self.x_range_idx_by_val(xright)
        ybottom_idx = self.y_range_idx_by_val(ybottom)
        ytop_idx = self.y_range_idx_by_val(ytop)

        # import ipdb;ipdb.set_trace()
        try:
            self.zdata = self._zdata[ybottom_idx:ytop_idx + 1, xleft_idx:xright_idx + 1]
            self.xyrange = (
                self._xrange[xleft_idx:xright_idx + 1], self._yrange[ybottom_idx:ytop_idx + 1])
        except IndexError as error:
            print "Value not in data range: ", error

    def x_range_idx_by_val(self, value):
        """
        Return the nearest index of a value within the x axis range.

        Args:
            value: A value in the range of the x axis

        Returns: The closest index on the x axis range.
        """
        return (np.abs(self._xrange - value)).argmin()

    def y_range_idx_by_val(self, value):
        """
        Return the nearest index of a value within the y axis range.

        Args:
            value: A value in the range of the y axis

        Returns: The closest index on the y axis range.
        """
        return (np.abs(self._yrange - value)).argmin()

    def idx_by_val_coordinate(self, coordinate):
        """Return the nearest index pair for a coordinate pair along the
        two axes.
        
        Args:
            coordinate (tuple): y-axis value, x-axis value (inverse order!)
        Returns:
            (y-axis index, x-axis index)
        """
        return (self.y_range_idx_by_val(coordinate[0]), self.x_range_idx_by_val(coordinate[1]))

    def extract_ylinetrace(self, xval, ystartval, ystopval):
        """Extract a linetrace along a given y-axis range vor a specific
        value on the x axis.

        Args:
            xval (float): Position of the linecut along the x-axis.
            ystartval, ystopval (float): First and last value of the range along the y-axis.

        Returns:
            (linecutdata, y-axis range)
        """

        y_start_idx = self.y_range_idx_by_val(ystartval)
        y_stop_idx = self.y_range_idx_by_val(ystopval)

        assert y_start_idx != y_stop_idx,\
                              'Startindex and stopindex %d are equal for ylinetrace.' % y_start_idx

        sign = np.sign(y_stop_idx - y_start_idx)

        if sign == 1:
            return np.vstack(
                (self.zdata[y_start_idx:y_stop_idx + 1, self.x_range_idx_by_val(xval)],
                 self.y_range[y_start_idx:y_stop_idx + 1]))

        else:
            data = self.zdata[y_stop_idx:y_start_idx + 1, self.x_range_idx_by_val(xval)]
            y_range = self.y_range[y_stop_idx:y_start_idx + 1]
            return np.vstack((data[::-1], y_range[::-1]))

    def extract_xlinetrace(self, yval, xstartval, xstopval):
        """Extract a linetrace along a given y-axis range vor a specific
        value on the x axis.

        Args:
            yval (float): Position of the linecut along the y-axis.
            xstartval, xstopval (float): First and last value of the range along the x-axis.

        Returns:
            (linecutdata, x-axis range)
        """

        x_start_idx = self.x_range_idx_by_val(xstartval)
        x_stop_idx = self.x_range_idx_by_val(xstopval)

        assert x_start_idx != x_stop_idx,\
                              'Startindex and stopindex %d are equal for xlinetrace.' % x_start_idx

        sign = np.sign(x_stop_idx - x_start_idx)

        if sign == 1:
            return np.vstack(
                (self.zdata[self.y_range_idx_by_val(yval), x_start_idx:x_stop_idx + 1],
                 self.x_range[x_start_idx:x_stop_idx + 1]))
        else:
            data = self.zdata[self.y_range_idx_by_val(yval), x_stop_idx:x_start_idx + 1]
            x_range = self.x_range[x_stop_idx:x_start_idx + 1]
            return np.vstack((data[::-1], x_range[::-1]))

    def extract_ylinetrace_series(self, x_first, x_last, x_interval, ystart, ystop):
        """Extract linetraces along a given y-axis range for
        values on the x axis within a given range and separated by
        a given interval.

        Args:
            x_first, x_last (float): the values of the boundaries on the x-axis.
            x_interval (float): the (positive) interval between two linecuts on the x-axis.
            ystart, ystop (float): the y-axis range that is extracted.

        Returns:
            a list of tuples with the format (linecut_data, y_range)
        """


        result_array = self.extract_ylinetrace(x_first, ystart, ystop)
        if self.x_range_idx_by_val(x_first) == self.x_range_idx_by_val(x_last):
            return result_array

        result_range = result_array[1]
        result_array = result_array[0]

        x_sign = np.sign(x_last - x_first)
        x_pos = x_first + x_interval * x_sign

        while x_pos * x_sign <= x_last * x_sign:
            result_array = np.vstack((result_array, self.extract_ylinetrace(x_pos, ystart, ystop)[0]))

            x_pos += x_interval * x_sign

        return np.vstack((result_array, result_range))

    def extract_xlinetrace_series(self, y_first, y_last, y_interval, xstart, xstop):
        """Extract linetraces along a given x-axis range for
        values on the y axis within a given range and separated by
        a given interval.

        Args:
            y_first, y_last (float): the values of the boundaries on the y-axis.
            y_interval (float): the interval between two linecuts on the y-axis.
            xstart, xstop (float): the x-axis range that is extracted.

        Returns:
            Array of linetraces and the range array.
            Order: First to last. The range information is added as last row.
        """

        result_array = self.extract_xlinetrace(y_first, xstart, xstop)
        if self.y_range_idx_by_val(y_first) == self.y_range_idx_by_val(y_last):
            return result_array

        y_sign = np.sign(y_last - y_first)
        y_pos = y_first + y_interval * y_sign
        # For now we remove the range axis
        result_range = result_array[1]
        result_array = result_array[0]

        while y_pos * y_sign <= y_last * y_sign:
            # add the next linetrace to the other linetraces
            result_array = np.vstack((result_array, self.extract_xlinetrace(y_pos, xstart, xstop)[0]))

            y_pos += y_interval * y_sign

        return np.vstack((result_array, result_range))
