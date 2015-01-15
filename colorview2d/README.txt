
colorview2d is a 2D color plotting utility. 

It uses the power of numpy, scipy and matplotlib to visualize 3d datasets provided in ASCII text data files. 

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
 Download and execute the colorview2d binary or script file, 
 whilst the default plotting file ("demo.dat") and the 
 configuration file ("default.config") is present in the same directory. 

* Linux:
 You can download a binary package, compressed as a 7z archive. 
 Uncompress and execute 

 ./colorview2d

 If you have numpy, scipy, the wxPython toolkit and matplotlib installed, 
 just download the source code via

 git clone git://git.code.sf.net/p/colorview2d/code colorview2d-code

 and execute

 python colorview2d.py

15.1.2015 Alois Dirnaichner
