"""
mods_test
---------

Module to test the mod framework.
Applies all mods seperately and in a mix.
"""

import unittest
import random
import string
import os
import numpy as np

import colorview2d

class ModTest(unittest.TestCase):
    """Class with mod tests."""
    no_setup = False

    def setUp(self):
        """Setup routine for all mod tests.
        This routine is normally called before the execution of each test.
        We suppress this behavior for the test of multiple mods using the no_setUp flag.
        """
        if not self.no_setup:
            self.width = np.random.randint(10, 300)
            self.height = np.random.randint(10, 300)
            x_range = (0., np.random.random())
            y_range = (0., np.random.random())
            print("figsize ({0}, {1})".format(self.width, self.height))

            self.data = colorview2d.Data(
                np.random.random((self.width, self.height)),
                (y_range, x_range))
            self.fig = colorview2d.View(self.data)

    def test_add_remove_mod(self):
        """Add mod by name, remove mod by postion and by name."""

        self.fig.add_mod('Derive')
        self.fig.add_mod('Smooth', (1, 1))
        self.fig.add_mod('Median', (1, 1))
        # remove by name
        self.fig.remove_mod('Derive')

        self.assertFalse('Derive' in [mod[0] for mod in self.fig.pipeline])

        # remove mod by position

        self.fig.remove_mod(pos=1)

        self.assertFalse('Smooth' in [mod[0] for mod in self.fig.pipeline])

    def test_call_signature(self):
        """Test the fancy call signature to add_mod(modname, modargs),
        add_modname(*modargs)."""

        # test a mod without arguments
        self.fig.add_Derive()

        # test two mods with one argument
        self.fig.add_Flip(True)
        self.fig.add_Scale(4.5)

        # test mod with two arguments
        self.fig.add_Smooth(3, 3)

        # test crop
        crop_bounds = (
            random.choice(self.fig.data.y_range),
            self.fig.data.ytop,
            random.choice(self.fig.data.x_range),
            self.fig.data.xright)
        self.fig.add_Crop(*crop_bounds)

        # check the pipeline
        self.assertEqual(self.fig.pipeline, [('Derive', ()),
                                             ('Flip', (True,)),
                                             ('Scale', (4.5,)),
                                             ('Smooth', (3, 3)),
                                             ('Crop', crop_bounds)])


    def test_derive(self):
        """Test of the derive mod."""
        self.fig.add_mod('Derive')

    def test_crop(self):
        """Test of the crop mod."""
        diff_width = np.random.random() * self.fig.data.xmax
        diff_height = np.random.random() * self.fig.data.ymax

        left_edge = np.random.random() * diff_width
        right_edge = self.fig.data.xmax - (diff_width - left_edge)

        bottom_edge = np.random.random() * diff_height
        top_edge = self.fig.data.ymax - (diff_height - bottom_edge)

        self.fig.add_mod('Crop', (bottom_edge, top_edge, left_edge, right_edge))

    def test_smooth(self):
        """Test of the smooth mod."""
        xwidth = np.random.randint(1, self.width)
        ywidth = np.random.randint(1, self.height)

        self.fig.add_mod('Smooth', (xwidth, ywidth))

    def test_rotate(self):
        """Test of the rotate mod."""
        self.fig.add_mod('Rotate', (bool(random.getrandbits(1))))

    def test_flip(self):
        """Test of the flip mod."""
        self.fig.add_mod('Flip', (bool(random.getrandbits(1))))

    def test_absolute(self):
        """Test of the absolute mod."""
        self.fig.add_mod('Absolute', ())

    def test_median(self):
        """Test of the median mod."""
        width = np.random.randint(1, min(self.width, self.height) // 2)

        self.fig.add_mod('Median', (width))

    def test_log(self):
        """Test of the log mod."""
        self.fig.add_mod('Log', ())

    def test_adaptiveThreshold(self):
        """Test of the adaptive_threshold mod."""
        blocksize = np.random.randint(1, min(self.width, self.height)) // 2
        max_threshold = self.fig.data.zmax / np.mean(self.fig.data.zdata)
        threshold = np.random.randint(0, max_threshold)

        self.fig.add_mod('Adaptive_Threshold', (blocksize, threshold))

    def test_multiple(self):
        """Tests a sequence of 5 randomly selected mods. The setUp routine is supressed so that
        all mods are applied to the same test case.
        """
        testarray = dir(self)
        testarray.remove('test_multiple')
        testarray.remove('test_add_remove_mod')
        testarray.remove('test_call_signature')
        testarray = [testname for testname in testarray if 'test_' in testname]

        testsequence = np.random.randint(0, len(testarray) - 1, 5)
        print("Multimodtest sequence {0}".format([testarray[num] for num in testsequence]))
        self.no_setup = True

        for num in testsequence:
            call = "self." + testarray[num] + "()"
            print(call)
            eval(call)

        self.no_setup = False


class ModFrameworkTest(unittest.TestCase):
    """Test the exploration of the mod modules."""
    def setUp(self):
        self.modname = ''.join(
            [random.choice(string.ascii_letters) for n in range(np.random.randint(1, 10))])
        filename = ''.join(
            [random.choice(string.ascii_letters) \
             for n in range(np.random.randint(10))]) + '.py'
        self.modpath = os.path.join('colorview2d/mods/', filename)
        with open(self.modpath, 'w+') as fh:
            fh.write('import colorview2d\n'
                     'class %s(colorview2d.IMod):\n'
                     '    def do_apply(self, data, modargs):\n'
                     '        print("do something to the modfile")\n' % self.modname)
    def tearDown(self):
        os.remove(self.modpath)
        try:
            os.remove(self.modpath + 'c')
        except FileNotFoundError:
            pass

    def test_add_find_mod(self):
        """Create a minimal mod file. Check if it is found by the
        mod framework.
        """

        fig = colorview2d.View(np.random.random((10, 10)))

        self.assertTrue(fig.modlist[self.modname])


