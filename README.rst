colorview2d Readme
==================

Use colorview2d to visualize and analize 2d data with (linear) axes.

Features:
---------

-  Wide range of adjustable filters (mods) using routines from numpy, scipy and scikit.images:
   
   -  interpolation,
   -  Gaussian and median filters,
   -  scale, rotate, flip, crop
   -  thresholding to extract features,
   -  absolute value, natural logarithm, derivation
   -  something missing? Add a mod easily.
   
-  Plot to pdf or just use the matplotlib figure.
-  Annoyed of matplotlib.pyplots 2d colorplot interface? Simple and
   convenient plot configuration.

   -  Adjust axis labels, their size and font as well as the plot size.
   -  Easily adapt the colorbar to your needs.
   
-  Mass extract linetraces (to depict feature evolution).
-  Save cv2d config files and restore any modifications easily.
-  Save and load data to and from plain text files (gnplot format).

Installation
------------

You can use the python package index via pip

::

    sudo pip2.7 install --upgrade colorview2d

*Note*: If you receive a 'Could not find a version that satisfies...' error, try to
upgrade pip, ``pip install --upgrade pip``

If you are considering writing your own mods then installation into the
userspace is preferable (access to colorview2d/mods to place the mod
file).

::

    pip2.7 install --user <username> --upgrade colorview2

Usage
-----

I stronlgy recommend to use ipython interactive shell for this tutorial.
We initialize some random data with x and y ranges:

::

    import numpy as np
    data = np.random.random((100, 100))
    xrange = (0., np.random.random())
    yrange = (0., np.random.random())

Obtain a :class:`colorview2d.Data` instance to initialize the :class:`colorview2d.View`
object:

::

    import colorview2d
    data = colorview2d.Data(data, (yrange, xrange))
    view = colorview2d.View(data)

Note that the order of the ranges (y range first) is not a typo. It is
reminiscent of the rows-first order of the 2d array.

What is the data about? We add some labels:

::

    view.config['Xlabel'] = 'foo (f)'
    view.config['Ylabel'] = 'bar (b)'
    view.config['Cblabel'] = 'nicyness (n)'

Let us have a look.

::

    view.show_plt_fig()

We do not like the font and the ticks labels are too small

::

    view.config.update({'Font': 'Ubuntu', 'Fontsize': 16})

Also, the colormap, being default matplotlib's jet, is not
greyscale-compatible, so we change to 'Blues' (have a look at the
matplotlib documentation to get a list of colormaps).

::

    view.config['Colormap'] = 'Blues'

Its time to plot a pdf and save the config

::

    view.plot_pdf('Nice_unmodified.pdf')
    view.save_config('Nice_unmodified.cv2d')

*Note*: Have a look at the plain text ``Nice_unmodified.cv2d``. The
config is just read as a dict. If you modify this file, changes get
applied accordingly upon calling ``load_config`` if you do not misspell
parameter names or options.

If you want to reuse the config next time, just use it upon
initialization of the ``view``:

::

    view = cv2d.View(original_data, cfgfile='Nice_unmodified.cv2d')

We realize that there is some (unphysical :) noise in the data. Nicyness
does not fluctuate so much along foo or bar and our cheap
nice-intstrument produced some additional fluctuations.

::

    view.add_mod('Smooth', (1, 1))

also we are interested more in the change of our nice landscape and not
in its absolute values so we derive along the bar axis

::

    view.add_mod('Derive')

Have a look at the ``mods/`` folder for other mods and documentation on
the arguments. It is also straightforward to create your own mod there.
Just have a look at the other mods in the folder.

We are interested especially in the nicyness between 0.0 and 0.1.

::

    view.config.update({'Cbmin':0.0, 'Cbmax':0.1})

To re-use this data later (without having to invoke colorview2d again),
we can store the data to a gnuplot-style plain text file.

::

    colorview2d.fileloaders.save_gpfile('Nice_smooth_and_derived.dat', view.data)

Extending colorview2d
---------------------

fileloaders
~~~~~~~~~~~

Have a look at the :class:`colorview2d.Data` definition in the :module:`colorview2d.data`
module. To create ``Data`` we have to provide the 2d array and the
bounds of the y and x ranges.

::

    data = colorview2d.Data(
        array,
        ((bottom_on_y_axis, top_on_y_axis),
        (left_on_x_axis, right_on_x_axis)))

To save data, just use the ``Data`` attributes, e.g.

::

    my_array = my_view.data.zdata # 2d numpy.array
    my_x_range = my_view.data.x_range # 1d numpy.array (left-to-right)
    my_y_range = my_view.data.y_range # 1d numpy.array (bottom-to-top)

mods
~~~~

If you want to apply your own modifications to the ``data``, just put a
module inside the ``colorview2d/mods`` directory (or package, if you
wish). The module should contain a class which inherits from
:class:`colorview2d.IMod` and implements the method
``do_apply(self, data, modargs)``.

You can modifiy the datafile freely, there is no error-checking done on
the consistency of the data (axes bounds, dimensions). Have a look at
the ``mods/Derive.py`` module for a *minimal* example.

To see if your mod is added successfully, have a look at
``my_view.modlist``.

4.10.2015, A. Dirnaichner
