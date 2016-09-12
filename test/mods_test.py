import unittest
import numpy as np
import random

import colorview2d

import logging
#logging.basicConfig(level="INFO")

class ModTest(unittest.TestCase):
    no_setUp = False
    
    def setUp(self):
        if not self.no_setUp:
            self.width = np.random.randint(10, 1000)
            self.height = np.random.randint(10, 1000)
            print "figsize ({}, {})".format(self.width, self.height)

            self.fig = colorview2d.CvFig(np.random.random((self.width, self.height)))

    def test_derive(self):
        self.fig.add_mod_to_pipeline(('Derive', ()))

    def test_crop(self):
        diff_width = np.random.randint(0, self.fig.datafile.Xmax - 1)
        diff_height = np.random.randint(0, self.fig.datafile.Ymax - 1)

        left_edge = np.random.randint(0, diff_width)
        right_edge = self.fig.datafile.Xmax - (diff_width - left_edge)

        bottom_edge = np.random.randint(0, diff_height)
        top_edge = self.fig.datafile.Ymax - (diff_height - bottom_edge)

        self.fig.add_mod_to_pipeline(('Crop', (left_edge, right_edge, bottom_edge, top_edge)))

    def test_smooth(self):
        xwidth = np.random.randint(1, self.width)
        ywidth = np.random.randint(1, self.height)

        self.fig.add_mod_to_pipeline(('Smooth', (xwidth, ywidth)))

    def test_rotate(self):
        self.fig.add_mod_to_pipeline(('Rotate', (bool(random.getrandbits(1)))))

    def test_flip(self):
        self.fig.add_mod_to_pipeline(('Flip', (bool(random.getrandbits(1)))))

    def test_absolute(self):
        self.fig.add_mod_to_pipeline(('Absolute', ()))

    def test_median(self):
        width = np.random.randint(1, min(self.width, self.height))

        self.fig.add_mod_to_pipeline(('Median', (width)))

    def test_log(self):
        self.fig.add_mod_to_pipeline(('Log', ()))

    def test_adaptiveThreshold(self):
        blocksize = np.random.randint(1, min(self.width, self.height)) / 2
        max_threshold = self.fig.datafile.Zmax / np.mean(self.fig.datafile.Zdata)
        threshold = np.random.randint(0, max_threshold)

        self.fig.add_mod_to_pipeline(('Adaptive_Threshold', (blocksize, threshold)))

    def test_multiple(self):
        testarray = dir(self)
        testarray.remove('test_multiple')
        testarray = [testname for testname in testarray if 'test_' in testname]

        testsequence = np.random.randint(0, len(testarray) - 1, 5)
        print "Multimodtest sequence {}".format([testarray[num] for num in testsequence])
        import ipdb;ipdb.set_trace()

        eval("self." + testarray[testsequence[0]] + "()")
        self.no_setUp = True

        for num in testsequence:
            call = "self." + testarray[num] + "()"
            print call
            eval(call)

        self.no_setUp = False

