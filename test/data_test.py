"""
data_test
---------

Module to test functionalities of the data and the fileloaders module.
"""
import unittest
import os
import random
import numpy as np

import colorview2d
import colorview2d.fileloaders as fl

class DataTest(unittest.TestCase):
    """Data test class."""
    def setUp(self):
        """Create a Data for the test."""

        width = np.random.randint(10, 100)
        height = np.random.randint(10, 100)
        print("arraysize ({0}, {1})".format(width, height))

        self.data = colorview2d.Data(np.random.random((width, height)))

    def test_crop_one(self):
        """Test to crop to array size one."""

        self.data.crop((0., 0., 0., 0.))
        self.assertEqual(self.data.zdata, np.array([self.data.zdata[0, 0]]))
        self.assertEqual(self.data.x_range, np.array([0.]))
        self.assertEqual(self.data.y_range, np.array([0.]))

    def test_crop_all(self):
        """Test where cropping leaves the whole file intact."""

        old_dfile = self.data.deep_copy()
        self.data.crop((0., self.data.zdata.shape[0] - 1,
                            0., self.data.zdata.shape[1] - 1))

        self.assertEqual(self.data.zdata.all(), old_dfile.zdata.all())

    def test_crop_random(self):
        """Use a sequence of random sizes to crop the data."""

        old_width = self.data.zdata.shape[1]
        old_height = self.data.zdata.shape[0]
        
        diff_width = np.random.randint(0, self.data.xmax - 1)
        diff_height = np.random.randint(0, self.data.ymax - 1)

        left_edge = np.random.randint(0, diff_width)
        right_edge = self.data.xmax - (diff_width - left_edge)

        bottom_edge = np.random.randint(0, diff_height)
        top_edge = self.data.ymax - (diff_height - bottom_edge)

        self.data.crop((bottom_edge, top_edge, left_edge, right_edge))

        self.assertEqual(
            self.data.zdata.shape,
            (old_height - diff_height, old_width - diff_width))
        self.assertEqual(self.data.xwidth, old_width - diff_width)
        self.assertEqual(self.data.ywidth, old_height - diff_height)

    def test_ylinetrace(self):
        """Extract a linecut along the y-axis."""

        # Extract a single linecut
        x_index = np.random.randint(self.data.xwidth)
        x_val = self.data.x_range[x_index]

        y_startindex = np.random.randint(self.data.ywidth)
        y_stopindex =  np.random.randint(self.data.ywidth)

        y_startval = self.data.y_range[y_startindex]
        y_stopval = self.data.y_range[y_stopindex]

        data = self.data.extract_ylinetrace(x_val, y_startval, y_stopval)[0]
        y_range = self.data.extract_ylinetrace(x_val, y_startval, y_stopval)[1]

        if y_startindex <= y_stopindex:
            self.assertEqual(data.tolist(), self.data.zdata[y_startindex:y_stopindex + 1, x_index].tolist())
            self.assertEqual(y_range.tolist(), self.data.y_range[y_startindex:y_stopindex + 1].tolist())
        else:
            self.assertEqual(data[::-1].tolist(), self.data.zdata[y_stopindex:y_startindex + 1, x_index].tolist())
            self.assertEqual(y_range[::-1].tolist(), self.data.y_range[y_stopindex:y_startindex + 1].tolist())

    def test_xlinetrace(self):
        """Extract a linecut along the x-axis."""

        # Extract a single linecut
        y_index = np.random.randint(self.data.ywidth)
        y_val = self.data.y_range[y_index]

        x_startindex = np.random.randint(self.data.xwidth)
        x_stopindex =  np.random.randint(self.data.xwidth)

        x_startval = self.data.x_range[x_startindex]
        x_stopval = self.data.x_range[x_stopindex]

        data = self.data.extract_xlinetrace(y_val, x_startval, x_stopval)[0]
        x_range = self.data.extract_xlinetrace(y_val, x_startval, x_stopval)[1]

        if x_startindex <= x_stopindex:
            self.assertEqual(data.tolist(), self.data.zdata[y_index, x_startindex:x_stopindex + 1].tolist())
            self.assertEqual(x_range.tolist(), self.data.x_range[x_startindex:x_stopindex + 1].tolist())
        else:
            self.assertEqual(data[::-1].tolist(), self.data.zdata[y_index, x_stopindex:x_startindex + 1].tolist())
            self.assertEqual(x_range[::-1].tolist(), self.data.x_range[x_stopindex:x_startindex + 1].tolist())

    def test_linetrace_series_all(self):
        """Test the extraction of a series of linecuts for the whole data."""

        # We extract the whole data as linecuts in x-direction
        result_array_x = self.data.extract_xlinetrace_series(
            self.data.ybottom,
            self.data.ytop,
            1,
            self.data.xleft,
            self.data.xright)

        # and in y-direction
        result_array_y = self.data.extract_ylinetrace_series(
            self.data.xleft,
            self.data.xright,
            1,
            self.data.ybottom,
            self.data.ytop)

        # the result array should be equal to the zdata array
        self.assertEqual(self.data.zdata.tolist(), result_array_x[:-1].tolist())
        self.assertEqual(self.data.zdata.tolist(), result_array_y[:-1].T.tolist())

        # ... with the ranges at the end
        self.assertEqual(self.data.x_range.tolist(), result_array_x[-1].tolist())
        self.assertEqual(self.data.y_range.tolist(), result_array_y[-1].tolist())
        
    def test_linetrace_arbitrary(self):
        """Extract a linetrace between two arbitrary points in the data."""

        xone = np.random.random() * self.data.xmax
        xtwo = np.random.random() * self.data.xmax

        yone = np.random.random() * self.data.ymax
        ytwo = np.random.random() * self.data.ymax

        print("Extracting arbitrary linetrace from ({0}, {1}) to ({2}, {3})."\
            .format(yone, xone, ytwo, xtwo))

        #import ipdb;ipdb.set_trace()
        linetrace = self.data.extract_arbitrary_linetrace((yone, xone), (ytwo, xtwo))

        # we check if the length of the extracted array is valid
        idx_one = self.data.idx_by_val_coordinate((yone, xone))
        idx_two = self.data.idx_by_val_coordinate((ytwo, xtwo))
        # the longer of the two diffs is the primary axis that determines
        # the length of the linetrace
        if abs(idx_one[0] - idx_two[0]) > abs(idx_one[1] - idx_two[1]):
            linetrace_length = abs(idx_one[0] - idx_two[0]) + 1
        else:
            linetrace_length = abs(idx_one[1] - idx_two[1]) + 1
        self.assertEqual(linetrace.size, linetrace_length)

        # see if start and endpoints are included correctly
        self.assertEqual(self.data.zdata[idx_one], linetrace[0])
        self.assertEqual(self.data.zdata[idx_two], linetrace[-1])

    def test_resize(self):
        """Interpolate the array to a new size of up to double the old size."""
        new_xwidth = self.data.xwidth + np.random.randint(self.data.xwidth)
        new_ywidth = self.data.ywidth + np.random.randint(self.data.ywidth)

        # save old range boundaries
        old_xleft, old_xright = (self.data.xleft, self.data.xright)
        old_ybottom, old_ytop = (self.data.ybottom, self.data.ytop)
        # save old corner values
        old_zbottom = (self.data.zdata[0, 0], self.data.zdata[0, -1])
        old_ztop = (self.data.zdata[-1, 0], self.data.zdata[-1, -1])

        self.data.resize(new_ywidth, new_xwidth)

        # Check new shape
        self.assertEqual(self.data.zdata.shape, (new_ywidth, new_xwidth))
        # Check x and y ranges
        self.assertEqual(self.data.ywidth, new_ywidth)
        self.assertEqual(self.data.xwidth, new_xwidth)
        self.assertEqual((self.data.y_range[0], self.data.y_range[-1]),\
                         (old_ybottom, old_ytop))
        self.assertEqual((self.data.x_range[0], self.data.x_range[-1]),\
                         (old_xleft, old_xright))
        # Check corner values
        self.assertEqual(old_zbottom, (self.data.zdata[0, 0], self.data.zdata[0, -1]))
        self.assertEqual(old_ztop, (self.data.zdata[-1, 0], self.data.zdata[-1, -1]))

class FileloaderTest(unittest.TestCase):
    """Test methods of the fileloader module."""
    fname = 'testdata.dat'
    def tearDown(self):
        """Delete the data if created."""
        os.remove(self.fname)
        
    def test_gpfile_oneline(self):
        """Create a minimal gnuplot-style file and load
        it with the load_gpfile method.
        """

        testdata = np.random.random((1, 3))
        with open(self.fname, 'wb') as fhand:
            np.savetxt(fhand, testdata)

        data = fl.load_gpfile(self.fname)

        self.assertEqual(data.zdata[0, 0], testdata[0, 2])
        self.assertEqual(data.x_range[0], testdata[0, 0])
        self.assertEqual(data.y_range[0], testdata[0, 1])
            
    def test_gpfile_twoline(self):
        """Create a twoline gnuplot-style file and load
        it with the load_gpfile method.
        """

        testdata = np.random.random((2, 3))

        # The same value in each block for the y-axis
        testdata[:, 1] = np.random.random()

        with open(self.fname, 'wb') as testfile:
            np.savetxt(testfile, testdata[0].reshape(1, 3))
        with open(self.fname, 'a') as testfile:
            testfile.write('\n')
        with open(self.fname, 'ab') as testfile:
            np.savetxt(testfile, testdata[1].reshape(1, 3))
            #add a third broken line            
        with open(self.fname, 'a') as testfile:
            testfile.write('\n')
        with open(self.fname, 'ab') as testfile:
            np.savetxt(testfile, np.random.random((1, 2)))
            

        data = fl.load_gpfile(self.fname)

        self.assertEqual(data.zdata.shape, (1, 2))

        self.assertTrue(np.all(data.zdata == testdata[:, 2]))
        self.assertTrue(np.all(data.x_range == testdata[:, 0]))
        self.assertEqual(data.y_range[0], testdata[0, 1])

    def test_gpfile_twoline_broken(self):
        """Create a twoline gnuplot-style file and load
        it with the load_gpfile method. 
        We place y-value on the second column that are not equal
        to see if the load method notices.
        We expect a failure.
        """

        # NOT The same value in each block for the y-axis
        testdata = np.random.random((2, 3))

        with open(self.fname, 'wb') as testfile:
            np.savetxt(testfile, testdata)

        with self.assertRaises(AssertionError):
            data = fl.load_gpfile(self.fname)


if __name__ == "__main__":
    unittest.main()
    
