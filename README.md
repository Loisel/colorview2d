colorview2d Readme
==================

Use colorview2d to visualize and analize 2d data with (linear) axes. 


Features:
~~~~~~~~~

* Wide range of adjustable filters (mods) that can be extended easily.
  - interpolation,
  - Gaussian and median filters, 
  - scale, rotate, flip, crop
  - thresholding to extract features,
  - absolute value, natural logarithm, derivation
  - something missing? Add a mod easily.
* Plot to pdf or just use the matplotlib figure.
* Annoyed of matplotlib.pyplots 2d colorplot interface? Simple and convenient plot configuration.
  - Adjust axis labels, their size and font as well as the plot size.
  - Easily adapt the colorbar to your needs.
* Mass extract linetraces (to depict feature evolution). 
* Save cv2d config files and restore any modifications easily
* Save and load data to and from ASCII files (gnplot format)
 

Installation
~~~~~~~~~~~~

You can use the python package index via pip

    sudo pip2.7 install --upgrade colorview2d

or easy_install

    sudo easy_install --upgrade colorview2d

 Note that numpy can not be installed via the
 python package index. Please install these packages via the package
 manager that is shipped with your linux distribution.

Usage
~~~~~

I stronlgy recommend to use ipython interactive shell for this tutorial.
We initialize some random data with x and y ranges:

    data = np.random.random((100, 100))
    xrange = (0., np.random.random())
    yrange = (0., np.random.random())

Obtain a colorview2d.CvFig object:

    cvfig = colorview2d.CvFig(data, (yrange, xrange))

Note that the order of the ranges (y range first) is not a typo.
It is reminiscent of the rows-first order of the 2d array.

What is the data about? We add some labels:

    cvfig.config['Xlabel'] = 'foo (f)'
    cvfig.config['Ylabel'] = 'bar (b)'
    cvfig.config['Zlabel'] = 'nicyness (n)'

Let us have a look.

    cvfig.show_plt_fig()

We do not like the font and the ticks labels are too small

    cvfig.config.update({'Font': 'Ubuntu', 'Fontsize': 16})

Also, the colormap, being default matplotlib's jet, is not greyscale-compatible, so we change to
'Blues' (have a look at the matplotlib documentation to get a list of colormaps).

    cvfig.config['Colormap'] = 'Blues'

Its time to plot a pdf and save the config

    cvfig.plot_pdf('Nice_unmodified.pdf')
    cvfig.save_config('Nice_unmodified.cv2d')

We realize that there is some (unphysical :) noise in the data. Nicyness does not fluctuate
so much along foo or bar and our cheap nice-intstrument produced some additional fluctuations.

    cvfig.add_mod('Smooth', (1, 1))

also we are interested more in the change of our nice landscape and not in its absolute
values so we derive along the bar axis

    cvfig.add_mod('Derive')

Have a look at the mods/ folder for other mods and documentation on the arguments.
It is also straightforward to create your own mod there. Just have a look at the other mods
in the folder.
To re-use this data later (without having to invoke colorview2d again), we can store
the data to a gnuplot-style plain text file.

    cvfig.fileloader.save_gpfile('Nice_smooth_and_derived.dat')

This tutorial only covers a part of the features.
More documentation on colorview2d will be added soon.

26.9.2015, Alois Dirnaichner
