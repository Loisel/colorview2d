
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
* Convolute the dataset with a gaussian window ("smoothing"). 
* Scale and derive data. 

---

Installation and Usage: 

* Windows:
 Download and extract the files from the archive into a single folder. 
 Execute colorview2d.exe, 
 whilst the default plotting file ("demo.dat") and the 
 configuration file ("default.config") are present in the same directory. 

* Linux:
 You can download a tarball from
 
   https://pypi.python.org/pypi/colorview2d/
 
 and execute 

   sudo easy_install colorview2d-version.tar.gz 

 If everything works out nicely, you can start the program via

   colorview2d [-f | --file filename] [-c | --columns columns]

 where you can specify the filename of the datafile and which columns you want to read in.

20.1.2015 Alois Dirnaichner
