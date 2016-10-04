"""Test functionalities of the colorview2d.View class.

In particular:
- interactive plotting functionality and its interplay with the View class.
- the handling of the config dict.
"""

import unittest
import random

import os

import numpy as np

import colorview2d

class PltFigTest(unittest.TestCase):
    """Use all kind of View functionality while interactive
    :class:`matplotlib.pyplot.Figure` is shown.
    """

    def setUp(self):
        """We create a View object and show it."""
        self.fig = colorview2d.View(np.random.random((100, 100)))
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
        self.assertFalse(self.fig._plt_fig_is_active())

        # open it again
        self.fig.show_plt_fig()

        # is it there?
        self.assertTrue(self.fig._plt_fig_is_active())

        # close it twice
        self.fig.hide_plt_fig()
        self.fig.hide_plt_fig()
        

    def test_mods(self):
        """Select some random mod tests and run them."""

        # Derive
        self.fig.add_mod('Derive')
        # Crop
        self.fig.add_mod('Crop', (np.random.randint(self.fig.data.ywidth),
                                  self.fig.data.ywidth,
                                  np.random.randint(self.fig.data.xwidth),
                                  self.fig.data.xwidth))
        # Smooth
        self.fig.add_mod('Smooth', (1., 1.))
        
        # is the window there?
        self.fig._fig.show()
        raw_input("A cropped data, with smooth and derive...")
 
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

    def test_replace_dat(self):
        """Replace the data while retaining all other changes."""

        # let us apply thresholding and decrease the fontsize

        self.fig.add_mod('Smooth', (3, 3))
        self.fig.add_mod('Adaptive_Threshold', (20, 0.1))
        self.fig.config['Xlabel'] = 'latitude (deg)'
        self.fig.config['Ylabel'] = 'longitude (deg)'
        self.fig.config['Fontsize'] = 8

        self.fig._fig.show()
        raw_input("Test: Smooth mod, Adaptive Threshold mod, xlabel latitude, ylabel longitude, "
                  "fontsize 8 (Ubuntu).")

        # now we replace the datafile
        array = np.random.random((200, 200))
        bounds = ((-1, -0.5), (11, 13))
        data = colorview2d.Data(array, bounds)
        self.fig.replace_data(data)

        # and let us check again
        self.fig._fig.show()
        raw_input("Test: Smooth mod, Adaptive Threshold mod, xlabel latitude, ylabel longitude, "
                  "fontsize 8 (Ubuntu).")


