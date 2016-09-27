"""Test functionalities of the colorview2d.CvFig class.

In particular:
- interactive plotting functionality and its interplay with the CvFig class.
- the handling of the config dict.
"""

import unittest
import random
import string
import os
import matplotlib.pyplot as plt
import numpy as np
from test.mods_test import ModTest

import colorview2d

class PltFigTest(unittest.TestCase):
    """Use all kind of CvFig functionality while interactive
    :class:`matplotlib.pyplot.Figure` is shown.
    """

    def setUp(self):
        """We create a CvFig object and show it."""
        self.fig = colorview2d.CvFig(np.random.random((100, 100)))
        self.fig.show_plt_fig()

    def tearDown(self):
        """Hide the interactive plotting window."""
        self.fig.hide_plt_fig()

    def test_multiple_figs(self):
        """Open multiple interactive plotting windows."""
        # when we try to open it again, nothing should happen
        self.fig.show_plt_fig()
        # close it
        self.fig.hide_plt_fig()

        # is there an active plot?
        self.assertFalse(self.fig.plt_fig_is_active())

        # open it again
        self.fig.show_plt_fig()

        # is it there?
        self.assertTrue(self.fig.plt_fig_is_active())

        # close it twice
        self.fig.hide_plt_fig()
        self.fig.hide_plt_fig()
        

    def test_mods(self):
        """Select some random mod tests and run them."""

        # Derive
        self.fig.add_mod('Derive')
        # Crop
        self.fig.add_mod('Crop', (np.random.randint(self.fig.datafile.ywidth),
                                  self.fig.datafile.ywidth,
                                  np.random.randint(self.fig.datafile.xwidth),
                                  self.fig.datafile.xwidth))
        # Smooth
        self.fig.add_mod('Smooth', (1., 1.))
        
        # is the window there?
        self.fig._fig.show()
        raw_input("A cropped datafile, with smooth and derive...")
 
    def test_config(self):
        """Modify the config by different ways to test the ConfigDict class."""
        # Direct __setitem__
        my_Cbmin = 0.2
        my_Ylabel = 'foo'
        self.fig.config['Cbmin'] = my_Cbmin
        self.fig.config['Ylabel'] = my_Ylabel
        # Check directly in plot
        self.assertEqual(my_Cbmin, self.fig._plot.get_clim()[0])
        self.assertEqual(my_Ylabel, self.fig._fig.axes[0].get_ylabel())

        # Now something more advanced: Font style and size
        self.fig.config = {'Font': 'Ubuntu', 'Fontsize': 18}

        # Check again
        self.assertEqual(my_Cbmin, self.fig._plot.get_clim()[0])
        self.assertEqual(my_Ylabel, self.fig._fig.axes[0].get_ylabel())
        
        # This can only be checked graphically
        # Let us have a look:

        self.fig._fig.show()
        raw_input("We should notice a colorbar minimum of 0.2, ylabel foo and fontsize 18 in Ubuntu...")

        # add a mod to test the pipeline dump
        self.fig.add_mod('Smooth', (1, 1))

        # Save config to file and reload it
        filename = 'testconfig.cv2d'
        self.fig.save_config(filename)
        self.fig.load_config(filename)

        self.fig._fig.show()
        raw_input("Test: cbmin of 0.2, ylabel foo, fontsize 18 (Ubuntu) and smoothing applied...")
        os.remove(filename)


