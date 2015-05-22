#!/bin/python

"""
.. module:: gpfile

A module to handle 3D gnuplot datafiles.

It can be used to get information on the file,
access the contents via numpy arrays and extract
the ranges along the three axes.

The files are represented by the gp_file object.
The class provides methods to rotate, flipp, copy and save
the datafile.


Example
-------
::

    file = gp_file.gp_file('data.dat',(0,1,2))
    file.rotate_cw()
    file.report()
    file.save('newdata.dat')


"""

import scipy as sp
import copy


class Gpfile:
    """
    A gnuplot data file object.

    Usage:

        The datafile object can be initiated by the use of a filename and a column tuple.
        Alternatively, one can provide a 2d array of data. The axes are then just given by
        the index ranges.

        :filename: A gnuplot datafile to be read in.
        :columns: A tuple of three integers to specify the three columns.

        or:

        :data: Alternatively, a 2d :class:`numpy.ndarray` can be provided.
    

    Attributes:
    
    :ivar Zdata:  The two dimensional numpy arrray containing the actual data.
    :ivar Xrange: A one dimensional array representing the x axis range.
    :ivar Yrange: A one dimensional array representing the y axis range.
    :ivar Xleft: The value on the left of the x axis.
    :ivar Xright: The value on the right of the x axis.
    :ivar Ytop: The values on the top of the y axis.
    :ivar Ybottom: The values on the bottom of the y axis.
    :ivar Zmin: The min values of the 2d array.
    :ivar Zmax: The max values of the 2d array.
    :ivar Xmin: The min values of the x axis range.
    :ivar Xmax: The max values of the x axis range.
    :ivar Ymin: The min values of the y axis range.
    :ivar Ymax: The max values of the y axis range.
    :ivar filename: The filename of the ASCII file containing the data.      
      
    """

    def __init__(self,*args):
        # We decide if we are called using a filename string
        if isinstance(args[0],basestring):

            self.filename = args[0]
            data = sp.loadtxt(self.filename,usecols = args[1])
            nlines = data.shape[0]

            self.Bnum = 0

            for i in range(1,data.shape[0]):
                if data[i,0] != data[i-1,0]:
                    self.Bsize = i
                    break
            
            self.Bnum = nlines/self.Bsize
            self.Lnum = self.Bsize*self.Bnum
            # Store the data

            self.Zdata = (sp.resize(data[:self.Lnum,2],(self.Bnum,self.Bsize)).T)
            self.set_xyrange(data[self.Bsize-1::self.Bsize,0],data[:self.Bsize,1])

        # ... or by providing a numpy array.
        elif isinstance(args[0],sp.ndarray):
            self.Zdata = args[0]
            self.filename = "defaultfilename.dat"
            self.Bsize = self.Zdata.shape[0]
            self.Bnum = self.Zdata.shape[1]
            self.Lnum = self.Bnum*self.Bsize
            self.set_xyrange(sp.arange(self.Bnum),sp.arange(self.Bsize))
        else:
            raise ValueError("Received {}. Gpfile has to be initiated by filename or array.".format(args))
            

        self.Zmax = sp.amax(self.Zdata)
        self.Zmin = sp.amin(self.Zdata)


    def set_xyrange(self,Xrange,Yrange):
        """
        Specify the x and y ranges of the datafile.

        :param Xrange: One dimensional numpy array
                       with the same length as the width of the data.
        :type Xrange: :class:`numpy.ndarray`
        :param Yrange: One dimensional numpy array
                       with the same length as the height of the data.
        :type Yrange: :class:`numpy.ndarray`
        """
        if Xrange.shape[0] != self.Zdata.shape[1] or Yrange.shape[0] != self.Zdata.shape[0]:
            raise ValueError("Provided ranges are not compatible with the datafile.")
        
        self.Xrange = Xrange
        self.Yrange = Yrange


        self.Xleft = self.Xrange[0]
        self.Xright = self.Xrange[-1]

        self.Xmin = sp.amin(self.Xrange)
        self.Xmax = sp.amax(self.Xrange)

        self.Ytop = self.Yrange[-1]
        self.Ybottom = self.Yrange[0]

        self.Ymin = sp.amin(self.Yrange)
        self.Ymax = sp.amax(self.Yrange)

        self.dX = (self.Xrange[-1] - self.Xrange[0])/(self.Xrange.size-1)
        self.dY = (self.Yrange[-1] - self.Yrange[0])/(self.Yrange.size-1)


    def set_Zdata(self,Zdata):
        """
        Replace the 2d array containing the data.
        The Zmin and Zmax values are updated.

        :param Zdata: Two dimensional array to plot.
        :type Zdata: :class:`numpy.ndarray`
        """
        self.Zdata = Zdata

        self.Zmax = sp.amax(self.Zdata)
        self.Zmin = sp.amin(self.Zdata)


    def report(self):
        """
        Print a datafile report to the standart output.
        """

        print "Report for file {}:\n".format(self.filename)
        print "There are {} lines containing {} blocks with {} lines each.\n".format(self.Lnum,self.Bnum,self.Bsize)
        print "X-axis range from {} to {}\n\
Y-axis range from {} to {}".format(self.Xleft,self.Xright,self.Ybottom,self.Ytop)

    def deep_copy(self):
        """
        Deep copy the datafile object.

        :returns: A copy of the datafile object.
        """

        tmp = copy.deepcopy(self)
        tmp.Zdata = sp.copy(self.Zdata)
        tmp.Xrange = sp.copy(self.Xrange)
        tmp.Yrange = sp.copy(self.Yrange)

        return tmp

    def save(self,fname,comment=""):
        """
        Saves a datafile to a file with filename in the gnuplot format.

        :param fname: The filename of the ASCII file to contain the data.
        :type fname: str
        :param comment: A comment that is added to the top of the file.
        :type comment: str
        """

        f = open(fname,'w')

        f.write(comment+"\n")

        for i in range(self.Bnum):

            sp.savetxt(f,sp.vstack((self.Xrange[i]*sp.ones(self.Yrange.shape[0]),self.Yrange,self.Zdata[:,i])).T)
            f.write("\n")

        f.close()


    def rotate_cw(self):
        """
        Rotate the datafile clockwise. The axes are updated as well.
        """
        self.set_Zdata(sp.rot90(self.Zdata,k=1))
        self.set_xyrange(self.Yrange,self.Xrange[::-1])

    def rotate_ccw(self):
        """
        Rotate the datafile counter-clockwise. The axes are updated as well.
        """
        self.set_Zdata(sp.rot90(self.Zdata,k=3))
        self.set_xyrange(self.Yrange[::-1],self.Xrange)

    def flip_lr(self):
        """
        Flip the left and the right side of the datafile. The axes are updated as well.
        """
        self.set_Zdata(sp.fliplr(self.Zdata))
        self.set_xyrange(self.Xrange[::-1],self.Yrange)

    def flip_ud(self):
        """
        Flip the up and the down side of the datafile. The axes are updated as well.
        """
        self.set_Zdata(sp.flipud(self.Zdata))
        self.set_xyrange(self.Xrange,self.Yrange[::-1])


    def crop(self,xleft,xright,ybottom,ytop):
        """
        Crop the datafile to a subset of the array specifiying the corners of the subset in
        units of the axes ranges.

        :param xleft:
        :param xright:
        :param ybottom:
        :param ytop:
        
        """
        xleft_idx = self.get_xrange_idx(xleft)
        xright_idx = self.get_xrange_idx(xright)
        ybottom_idx = self.get_yrange_idx(ybottom)
        ytop_idx = self.get_yrange_idx(ytop)
        
        try:
            self.set_Zdata(self.Zdata[ybottom_idx:ytop_idx+1,xleft_idx:xright_idx+1])
            self.set_xyrange(self.Xrange[xleft_idx:xright_idx+1],self.Yrange[ybottom_idx:ytop_idx+1])
        except IndexError as e:
            print "Value not in data range: ",e


    def get_xrange_idx(self,value):
        """
        Return the nearest index of a value within the x axis range.

        :param value: A value in the range of the x axis
        :type value: float

        :returns: The closest index on the x axis range.
        """
        idx = int(sp.rint(abs(value-self.Xleft)/abs(self.dX)))

        try:
            self.Xrange[idx]
        except IndexError:
            print "Index {} deduced from value {} not within range.".format(idx,value)
        return idx
            

    def get_yrange_idx(self,value):
        """
        Return the nearest index of a value within the y axis range.

        :param value: A value in the range of the y axis
        :type value: float

        :returns: The closest index on the y axis range.
        """
        idx = int(sp.rint(abs(value-self.Ybottom)/abs(self.dY)))
        try:
            self.Yrange[idx]
        except IndexError:
            print "Index {} deduced from value {} not within range.".format(idx,value)
        return idx

    def set_filename(self,filename):
        self.filename = filename


    def get_Zmax(self):
        return self.Zdata.max()

    def get_Zmin(self):
        return self.Zdata.min()
