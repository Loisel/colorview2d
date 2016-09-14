"""
datafile_test
---------

Module to test functionalities of the datafile and the fileloaders module.
"""
import unittest
import os
import random
import numpy as np

import colorview2d
import colorview2d.fileloaders as fl

class DatafileTest(unittest.TestCase):
    """Datafile test class."""
    def setUp(self):
        """Create a Datafile for the test."""

        width = np.random.randint(10, 1000)
        height = np.random.randint(10, 1000)
        print "arraysize ({}, {})".format(width, height)

        self.datafile = colorview2d.Datafile(np.random.random((width, height)))

    def test_crop_one(self):
        """Test to crop to array size one."""

        self.datafile.crop(0., 0., 0., 0.)
        self.assertEqual(self.datafile.zdata, np.array([self.datafile.zdata[0, 0]]))
        self.assertEqual(self.datafile.xrange, np.array([0.]))
        self.assertEqual(self.datafile.yrange, np.array([0.]))

    def test_crop_all(self):
        """Test where cropping leaves the whole file intact."""

        old_dfile = self.datafile.deep_copy()
        self.datafile.crop(0., self.datafile.zdata.shape[1] - 1, 0., self.datafile.zdata.shape[0] - 1)

        self.assertEqual(self.datafile.zdata.all(), old_dfile.zdata.all())

    def test_crop_random(self):
        """Use a sequence of random sizes to crop the datafile."""

        old_width = self.datafile.zdata.shape[1]
        old_height = self.datafile.zdata.shape[0]
        
        diff_width = np.random.randint(0, self.datafile.xmax - 1)
        diff_height = np.random.randint(0, self.datafile.ymax - 1)

        left_edge = np.random.randint(0, diff_width)
        right_edge = self.datafile.xmax - (diff_width - left_edge)

        bottom_edge = np.random.randint(0, diff_height)
        top_edge = self.datafile.ymax - (diff_height - bottom_edge)

        self.datafile.crop(left_edge, right_edge, bottom_edge, top_edge)

        self.assertEqual(
            self.datafile.zdata.shape,
            (old_height - diff_height, old_width - diff_width))
        self.assertEqual(self.datafile.xrange.size, old_width - diff_width)
        self.assertEqual(self.datafile.yrange.size, old_height - diff_height)


class FileloaderTest(unittest.TestCase):
    """Test methods of the fileloader module."""
    fname = 'testdata.dat'
    def tearDown(self):
        """Delete the datafile if created."""
        os.remove(self.fname)
        
    def test_gpfile_oneline(self):
        """Create a minimal gnuplot-style file and load
        it with the load_gpfile method.
        """

        testdata = np.random.random((1, 3))
        np.savetxt(self.fname, testdata)

        datafile = fl.load_gpfile(self.fname)

        self.assertEqual(datafile.zdata[0, 0], testdata[0, 2])
        self.assertEqual(datafile.xrange[0], testdata[0, 0])
        self.assertEqual(datafile.yrange[0], testdata[0, 1])
            
    def test_gpfile_twoline(self):
        """Create a twoline gnuplot-style file and load
        it with the load_gpfile method.
        """

        testdata = np.random.random((2, 3))

        # The same value in each block for the y-axis
        testdata[:, 1] = np.random.random()

        with open(self.fname, 'w') as testfile:
            np.savetxt(testfile, testdata[0].reshape(1, 3))
        with open(self.fname, 'a') as testfile:
            testfile.write('\n')
            np.savetxt(testfile, testdata[1].reshape(1, 3))
            #add a third broken line            
            testfile.write('\n')
            np.savetxt(testfile, np.random.random((1, 2)))
            

        datafile = fl.load_gpfile(self.fname)

        self.assertEqual(datafile.zdata.shape, (1, 2))

        self.assertTrue(np.all(datafile.zdata == testdata[:, 2]))
        self.assertTrue(np.all(datafile.xrange == testdata[:, 0]))
        self.assertEqual(datafile.yrange[0], testdata[0, 1])

    def test_gpfile_twoline_broken(self):
        """Create a twoline gnuplot-style file and load
        it with the load_gpfile method. 
        We place y-value on the second column that are not equal
        to see if the load method notices.
        We expect a failure.
        """

        # NOT The same value in each block for the y-axis
        testdata = np.random.random((2, 3))

        np.savetxt(self.fname, testdata)

        with self.assertRaises(AssertionError):
            datafile = fl.load_gpfile(self.fname)


