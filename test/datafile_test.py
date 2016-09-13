"""
datafile_test
---------

Module to test functionalities of the datafile and the fileloaders module.
"""
import unittest
import numpy as np
import random

import colorview2d

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


