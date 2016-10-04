#!/bin/python
"""
A module to handle 3D data with axes.

colorview2d.Data consists of a 2d array and x and y axes.
The class provides methods to rotate, flipp, copy and save
the datafile.


Example
-------
::

    file = Data(np.random.random(100, 100))
    file.rotate_cw()
    file.report()
    file.save('newdata.dat')


"""

import copy
import logging
import numpy as np

class Data(object):
    """
    ``Data`` hosts, well, the data and its axes.

    Data is stored in a 2d :class:`numpy-ndarray`.
    For the axes, only the bounds are stored. We assume linear scaling of the axes.
    If no bounds are specified, we use ``(0, n)`` as boundaries, ``n``
    being the number of rows and columns, respectively.

    """

    def __init__(self, data, range_bounds=None):
        """Initialize a data object.

        Args:
            data (numpy.array): the two-dimensional array holding the data.
            range_bounds (tuple of tuples): y-range boundaries as a tuple (bottom, top),
                                            x-range boundaries as a tuple (left, right)

        """

        self._zdata = data
        self._xrange_bounds = None
        self._yrange_bounds = None

        try:
            self.xrange_bounds = range_bounds[1]
            self.yrange_bounds = range_bounds[0]
        except (AssertionError, IndexError, TypeError):
            logging.warn('Ranges not specified correctly. '
                         'Should be ((y_bottom, y_top), (x_left, x_right)). '
                         'Using index dimensions as ranges.')
            self._xrange_bounds = (0., float(self._zdata.shape[1] - 1))
            self._yrange_bounds = (0., float(self._zdata.shape[0] - 1))


    @property
    def xleft(self):
        """Right boundary value of the x-axis."""
        return self._xrange_bounds[0]

    @property
    def xright(self):
        """Left boundary value of the x-axis."""
        return self._xrange_bounds[1]

    @property
    def xmin(self):
        """Minimum value of the x-axis range."""
        return min(self._xrange_bounds)

    @property
    def xmax(self):
        """Maximum value of the x-axis range."""
        return max(self._xrange_bounds)

    @property
    def dx(self):
        """Spacing of x-axis values."""
        return (self._xrange_bounds[1] - self._xrange_bounds[0]) /\
            (self._zdata.shape[1] - 1)

    @property
    def ytop(self):
        """Top boundary value of the y-axis."""
        return self._yrange_bounds[1]

    @property
    def ybottom(self):
        """Bottom boundary value of the y-axis."""
        return self._yrange_bounds[0]

    @property
    def ymin(self):
        """Minimum value of the y-axis range."""
        return min(self._yrange_bounds)

    @property
    def ymax(self):
        """Maximum value of the y-axis range."""
        return max(self._yrange_bounds)

    @property
    def dy(self):
        """Spacing of y-axis values."""
        return (self._yrange_bounds[1] - self._yrange_bounds[0]) /\
            (self._zdata.shape[0] - 1)

    @property
    def zdata(self):
        """2d :class:`numpy.ndarray`."""
        return self._zdata

    @property
    def zmin(self):
        """Minimum value of the 2d :class:`numpy.ndarray`."""
        return np.amin(self._zdata)

    @property
    def zmax(self):
        """Maximum value of the 2d :class:`numpy.ndarray`."""
        return np.amax(self._zdata)

    @property
    def xwidth(self):
        """Size of the array along the x-axis."""
        return self._zdata.shape[1]

    @property
    def ywidth(self):
        """Size of the array along the y-axis."""
        return self._zdata.shape[0]

    @zdata.setter
    def zdata(self, data):
        """Set a new 2d :class:`numpy.ndarray`."""
        assert isinstance(data, np.ndarray), \
            'Not a numpy array. Please provide a numpy array for Data creation.'
        assert len(data.shape) == 2, 'Provide a two-dimensional array for Data creation.'
        self._zdata = data

    @property
    def y_range(self):
        """A linear y-range array."""
        return np.linspace(
            self._yrange_bounds[0], self._yrange_bounds[1], self.zdata.shape[0])

    @property
    def x_range(self):
        """A linear x-range array."""
        return np.linspace(
            self._xrange_bounds[0], self._xrange_bounds[1], self.zdata.shape[1])


    @property
    def xrange_bounds(self):
        """Boundary values on the x-axis as a tuple (left, right)."""
        return self._xrange_bounds

    @xrange_bounds.setter
    def xrange_bounds(self, range_boundaries):
        assert len(range_boundaries) == 2, 'Boundaries of x-axis range not specified correctly.'

        self._xrange_bounds = (float(range_boundaries[0]), float(range_boundaries[1]))

    @property
    def yrange_bounds(self):
        """Boundary values on the y-axis as a tuple (bottom, top)."""
        return self._yrange_bounds

    @yrange_bounds.setter
    def yrange_bounds(self, range_boundaries):
        assert len(range_boundaries) == 2, 'Boundaries of y-axis range not specified correctly.'

        self._yrange_bounds = (float(range_boundaries[0]), float(range_boundaries[1]))


    def report(self):
        """
        Print a data report to the standart output.
        """

        print(
            "There are {0} lines and {1} columns in the datafile.\n"
            .format(self._zdata.shape[0], self._zdata.shape[1]))
        print(
            "X-axis range from {0} to {1}".format(self.xleft, self.xright),
            "Y-axis range from {0} to {1}".format(self.ybottom, self.ytop))

    def deep_copy(self):
        """
        Deep copy the :class:`colorview2d.Data` object and return the copy.

        Returns:
            A copy of the :class:`Colorview2d.Data` instance.
        """

        tmp = copy.deepcopy(self)
        tmp.zdata = np.copy(self._zdata)

        return tmp


    def rotate_cw(self):
        """
        Rotate the data clockwise. The axes are updated as well.
        """
        self.zdata = np.rot90(self._zdata, k=1)
        old_xrange_boundaries = self._xrange_bounds
        old_yrange_boundaries = self._yrange_bounds
        self._xrange_bounds = old_yrange_boundaries
        self._yrange_bounds = old_xrange_boundaries[::-1]


    def rotate_ccw(self):
        """
        Rotate the data counter-clockwise. The axes are updated as well.
        """
        self.zdata = np.rot90(self._zdata, k=3)
        old_xrange_boundaries = self._xrange_bounds
        old_yrange_boundaries = self._yrange_bounds
        self._xrange_bounds = old_yrange_boundaries[::-1]
        self._yrange_bounds = old_xrange_boundaries


    def flip_lr(self):
        """
        Flip the left and the right side of the data. The axes are updated as well.
        """
        self.zdata = np.fliplr(self._zdata)
        self._xrange_bounds = self._xrange_bounds[::-1]


    def flip_ud(self):
        """
        Flip the up and the down side of the data. The axes are updated as well.
        """
        self.zdata = np.flipud(self._zdata)
        self._yrange_bounds = self._yrange_bounds[::-1]

    def is_within_xbounds(self, val):
        """Check if the given value is within the xrange.

        Returns:
            a boolean.
        """
        return val >= self.xmin or val <= self.xmax

    def is_within_ybounds(self, val):
        """Check if the given value is within the yrange.

        Returns:
            a boolean.
        """
        return val >= self.ymin or val <= self.ymax

    def is_within_bounds(self, coordinate):
        """Check if the given coordinate (y, x) is within the ranges
        of the axes.

        Returns:
            a boolean.
        """
        return self.is_within_xbounds(coordinate[1]) or self.is_within_ybounds(coordinate[0])

    def crop(self, boundaries):
        """
        Crop the data to a subset of the array specifiying the corners of the subset in
        units of the axes ranges.

        Args:
            boundaries (tuple): (bottom boundary, top boundary,
                                           left boundary, right boundary)
        """
        bottom_boundary, top_boundary = (boundaries[0], boundaries[1])
        left_boundary, right_boundary = (boundaries[2], boundaries[3])
        assert self.is_within_bounds((bottom_boundary, left_boundary)),\
            'crop: Bottom left edge not within boundaries.'
        assert self.is_within_bounds((top_boundary, right_boundary)),\
            'crop: Top right edge not within boundaries.'


        xleft_idx = self.x_range_idx_by_val(left_boundary)
        xright_idx = self.x_range_idx_by_val(right_boundary)
        ybottom_idx = self.y_range_idx_by_val(bottom_boundary)
        ytop_idx = self.y_range_idx_by_val(top_boundary)
        self._xrange_bounds = (left_boundary, right_boundary)
        self._yrange_bounds = (bottom_boundary, top_boundary)

        self.zdata = self._zdata[ybottom_idx:ytop_idx + 1, xleft_idx:xright_idx + 1]

    def x_range_idx_by_val(self, value):
        """
        Return the nearest index of a value within the x axis range.

        Args:
            value: A value in the range of the x axis

        Returns:
            The closest index on the x axis range.
        """
        assert self.is_within_xbounds(value), 'Value %f out of xrange.' % value
        return int(round(abs(self.xleft - value) / self.dx))

    def y_range_idx_by_val(self, value):
        """
        Return the nearest index of a value within the y axis range.

        Args:
            value: A value in the range of the y axis

        Returns:
            The closest index on the y axis range.
        """
        assert self.is_within_ybounds(value), 'Value %f out of yrange.' % value
        return int(round(abs(self.ybottom - value) / self.dy))

    def idx_by_val_coordinate(self, coordinate):
        """Return the nearest index pair for a coordinate pair (y, x) along the
        two axes.

        Args:
            coordinate (tuple): y-axis value, x-axis value (inverse order!)
        Returns:
            (y-axis index, x-axis index) -- both integer
        """
        return (self.y_range_idx_by_val(coordinate[0]), self.x_range_idx_by_val(coordinate[1]))


    def extract_ylinetrace(self, xval, ystartval, ystopval):
        """Extract a linetrace along a given y-axis range vor a specific
        value on the x axis.

        Args:
            xval (float): Position of the linecut along the x-axis.
            ystartval (float): First and ...
            ystopval (float): last value of the range along the y-axis.

        Returns:
            numpy array with two rows
            [0] linecutdata
            [1] y-axis range
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
            xstartval (float): Start and ...
            xstopval (float): stop value of the range along the x-axis.

        Returns:
            numpy array with two rows
            [0] linecutdata
            [1] x-axis range
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
            x_first (float): value on the x-axis for the first line trace in the series.
            x_last (float): value on the x-axis for the last line trace in the series.
            x_interval (float): the (positive) interval between two linecuts on the x-axis.
            ystart (float): Start and ...
            ystop (float): stop value of the range along the y-axis.

        Returns:
            a numpy array with n + 1 rows with the length equal to the y-dimensions of zdata.
            n is the number of linecuts, i.e., abs(x_last - x_first) / x_interval.
            The last row contains the y-axis range.
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
            y_first (float): value on the y-axis for the first line trace in the series.
            y_last (float): value on the y-axis for the last line trace in the series.
            y_interval (float): the (positive) interval between two linecuts on the y-axis.
            xstart (float): Start and ...
            xstop (float): stop value of the range along the x-axis.

        Returns:
            a numpy array with n + 1 rows with the length equal to the x-dimensions of zdata.
            n is the number of linecuts, i.e., abs(y_last - y_first) / y_interval.
            The last row contains the x-axis range.
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

    def extract_arbitrary_linetrace(self, coordinate_one, coordinate_two):
        """Extract a linetrace between two arbitrary points.

        Args:
            coordinate_one (tuple): coordinate in the coordinate system of the axis.
                The order is (yval, xval)!
            coordinate_two (tuple): coordinates in the coordinate system of the
                x and y axes. The order is (yval, xval)!

        Returns:
            Array with the linetrace. No axis range is supplied since it does not make sense
            along any arbitrary direction.
        """

        # we transform to the grid
        idx_one = self.idx_by_val_coordinate(coordinate_one)
        idx_two = self.idx_by_val_coordinate(coordinate_two)

        assert idx_one != idx_two, (
            'Coordinate one and two are equal: (y=%d, x=%d).' % (idx_one[0], idx_one[1]),\
            'Can not extract linetrace of zero length.')

        # if one of the two coordinate axis has zero difference,
        # we call the orthogonal version
        # y axis difference is zero:
        if idx_one[0] == idx_two[0]:
            return self.extract_xlinetrace(
                coordinate_one[0], coordinate_one[1], coordinate_two[1])[0]
        # x axis difference is zero:
        elif idx_one[1] == idx_two[1]:
            return self.extract_ylinetrace(
                coordinate_one[1], coordinate_one[0], coordinate_two[0])[0]

        # which is the primary axis of the linetrace?
        if abs(idx_one[0] - idx_two[0]) > abs(idx_one[1] - idx_two[1]):
            primary_axis_index, secondary_axis_index = (0, 1)
        else:
            primary_axis_index, secondary_axis_index = (1, 0)

        linetrace_slope = float(idx_two[secondary_axis_index] - idx_one[secondary_axis_index]) /\
                          float(idx_two[primary_axis_index] - idx_one[primary_axis_index])
        # Note that the linetrace has one more points than its length
        linetrace_size = abs(idx_two[primary_axis_index] - idx_one[primary_axis_index]) + 1
        axis_sign = np.sign(idx_two[primary_axis_index] - idx_one[primary_axis_index])

        # go along primary axis and extract closest point
        # if the primary axis is y-axis
        if primary_axis_index == 0:
            # dy and dx are positive: increment on both axis postive (trivial case)
            # dy > 0, dx < 0: increment on first axis positive, slope negative -> increment
            # on second axis negative.
            # dy < 0, dx > 0: increment on y negative, slope negative -> dx positive
            # dy < 0, dx < 0: increment negative, slope positive -> dx negative
            linetrace = np.array(
                [self.zdata[yidx + idx_one[0], int(round(yidx * linetrace_slope + idx_one[1]))]
                 for yidx in np.arange(linetrace_size) * axis_sign])
        else:
            linetrace = np.array(
                [self.zdata[int(round(xidx * linetrace_slope + idx_one[0])), xidx + idx_one[1]]
                 for xidx in np.arange(linetrace_size) * axis_sign])

        return linetrace

    def resize(self, new_ywidth, new_xwidth, order=1):
        """Interpolate the array to a new, larger size.

        Uses scipy.misc.imresize.
        The ranges are interpolated accordingly.

        Args:
            new_ywidth (int): new dimensions along the y-axis.
            new_xwidth (int): new dimensions along the x-axis.
            order (int): order of the interpolation. See ``scipy.misc.imresize()``
        """
        # Check if scipy is available
        try:
            from scipy.ndimage import zoom
        except ImportError:
            logging.error(
                'Module scipy is not available. scipy.misc.imresize is used for interpolation.')
            return

        xfactor = float(new_xwidth) / self.xwidth
        yfactor = float(new_ywidth) / self.ywidth
        self._zdata = zoom(self._zdata, (yfactor, xfactor), order=order)
