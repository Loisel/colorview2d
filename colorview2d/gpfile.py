#!/bin/python

"""
gpfile
~~~~~~~

A module to handle 3D gnuplot datafiles. It can be used to
get information on the file, access the contents via
numpy arrays and extract the ranges along the three axes.
Datafiles can also be rotated, copied and saved.

Example:
file = gp_file.gp_file('data.dat',(0,1,2))
file.rotate_cw()
file.report()
file.save('newdata.dat')

The files are represented by the gp_file object.

:copyright: 2014 by Alois Dirnaichner, see AUTHORS for more details
:license: GPLv3, see LICENSE for more details
"""

import scipy as sp
import copy


class gpfile():
    """A gnuplot data file object"""

    def __init__(self,*args):

        if isinstance(args[0],basestring):

            self.filename = args[0]
            data = sp.loadtxt(self.filename,usecols = args[1])

        elif isinstance(args[0],numpy.ndarray):
            data = args[0]
            self.filename = "defaultfilename.dat"
        else:
            raise ValueError("Received {}. gpfile has to be initiated by filename or array.".format(args))
            
        nlines = data.shape[0]

        self.Bnum = 0

        for i in range(1,data.shape[0]):
            if data[i,0] != data[i-1,0]:
                self.Bsize = i
                break

        self.set_xyrange(data[self.Bsize-1::self.Bsize,0],data[:self.Bsize,1])

        self.Bnum = nlines/self.Bsize
        self.Lnum = self.Bsize*self.Bnum


        # Store the data

        self.Zdata = (sp.resize(data[:self.Lnum,2],(self.Bnum,self.Bsize)).T)
        self.Zmax = sp.amax(self.Zdata)
        self.Zmin = sp.amin(self.Zdata)
        #self.Zdata_Original = sp.copy(self.Zdata)

    def set_filename(self,filename):
        self.filename = filename

    def set_xyrange(self,Xrange,Yrange):
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

        #self.Xrange = sp.linspace(self.Xmin,self.Xmax,self.Bnum)
        #self.Yrange = sp.linspace(self.Ymin,self.Ymax,self.Bsize)

        self.dX = (self.Xrange[-1] - self.Xrange[0])/(self.Xrange.size-1)
        self.dY = (self.Yrange[-1] - self.Yrange[0])/(self.Yrange.size-1)


    def set_Zdata(self,Zdata):
        self.Zdata = Zdata

        self.Zmax = sp.amax(self.Zdata)
        self.Zmin = sp.amin(self.Zdata)


    def report(self):

        print "Report for file {}:\n".format(self.filename)
        print "There are {} lines containing {} blocks with {} lines each.\n".format(self.Lnum,self.Bnum,self.Bsize)
        print "X-axis range from {} to {}\n\
Y-axis range from {} to {}".format(self.Xrange[0],self.Xrange[-1],self.Yrange[0],self.Yrange[-1])

    def deep_copy(self):

        tmp = copy.deepcopy(self)
        tmp.Zdata = sp.copy(self.Zdata)
        tmp.Xrange = sp.copy(self.Xrange)
        tmp.Yrange = sp.copy(self.Yrange)

        return tmp

    def save(self,fname,comment=""):
        """
        Saves a datafile to a file with filename in the gnuplot format.
        """

        f = open(fname,'w')

        f.write(comment+"\n")

        for i in range(self.Bnum):

            sp.savetxt(f,sp.vstack((self.Xrange[i]*sp.ones(self.Yrange.shape[0]),self.Yrange,self.Zdata[::,i])).T)
            f.write("\n")

        f.close()

    def get_xrange_idx(self,value):
        idx = int(sp.rint(abs(value-self.Xleft)/abs(self.dX)))

        try:
            self.Xrange[idx]
        except IndexError:
            print "Index {} deduced from value {} not within range.".format(idx,value)
        return idx
            

    def get_yrange_idx(self,value):
        idx = int(sp.rint(abs(value-self.Ybottom)/abs(self.dY)))
        try:
            self.Yrange[idx]
        except IndexError:
            print "Index {} deduced from value {} not within range.".format(idx,value)
        return idx

    def get_Zmax(self):
        return self.Zdata.max()

    def get_Zmin(self):
        return self.Zdata.min()

    def rotate_cw(self):
        self.set_xyrange(self.Yrange,self.Xrange[::-1])
        self.set_Zdata(sp.rot90(self.Zdata,k=3))

        return self

    def rotate_ccw(self):
        self.set_xyrange(self.Yrange[::-1],self.Xrange)
        self.set_Zdata(sp.rot90(self.Zdata,k=1))

        return self

    def get_region(self,xleft,xright,ybottom,ytop):
        try:
            return self.Zdata[-ytop:-ybottom,xleft:xright]
        except IndexError as e:
            print "Index not in data range:",e
