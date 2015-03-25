
colorview2d is a 2D color plotting utility. 

It uses the power of numpy, scipy and matplotlib to visualize 3d datasets 
provided as ASCII text data files. 

---

Features of the beta: 

* Adjustable colorbar. 
* Rotate and crop datasets. 
* Adjust axis labels, their size and font as well as the plot size. 
* Plot line traces of arbitrary orientations by point and click in the 2d colorplot. 
* Mass extract linetraces (to depict feature evolution). 
* Extract linear slopes in units of the datafile axis by point and click. 
* Measure distances interactively in the plot.
* Convolute the dataset with a gaussian window ("smoothing").
* Apply a median filter to the data. 
* Scale and derive data.
* Save cv2d config files to recover the state of the data file
  including axis labels and plotting pipeline. 
* Extensible plot manipulation toolbox using yapsy plugin framework.
* Interactive Python shell can be used to access internal objects.
 
---

Installation and Usage: 

* Windows:
 Note that that only some (few) versions can be provided as a binary package
 for Windows.

 Please have a look at 
   https://sourceforge.net/projects/colorview2d/files/
 for the latest version.

 Download and extract the files from the archive into a single folder. 
 Execute colorview2d.exe, 
 whilst the default plotting file ("demo.dat") and the 
 configuration file ("default.cv2d") are present in the same directory. 

* Linux:
 You can download a tarball from
 
   https://pypi.python.org/pypi/colorview2d/
 
 and execute 

   sudo easy_install colorview2d-version.tar.gz 

 If everything works out nicely, you can start the program via

   colorview2d [-f | --file filename] [--columns columns] [-c | --cv2d config_file]

 where you can specify the filename of the datafile and which columns you want to read in, or, 
 alternatively, a cv2d config file.

3.3.2015 Alois Dirnaichner
