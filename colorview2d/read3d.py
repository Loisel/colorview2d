#!/bin/python

import scipy as sp
import copy

class gp_file:
	"""A gnuplot data file object"""

	def __init__(self,filename,columns):

		self.filename = filename
		
		data = sp.loadtxt(filename,usecols = columns)
		
		nlines = data.shape[0]

		self.Bnum = 0

		for i in range(1,data.shape[0]):	
			if data[i,0] != data[i-1,0]:
				self.Bsize = i		
				break

		self.Bnum = nlines/self.Bsize
		self.Lnum = self.Bsize*self.Bnum

		self.Xmin = data[0,0]
		self.Xmax = data[self.Lnum-1,0]

		self.Ymin = data[0,1]
		self.Ymax = data[self.Bsize-1,1]

		self.Xrange = sp.linspace(self.Xmin,self.Xmax,self.Bnum)
		self.Yrange = sp.linspace(self.Ymin,self.Ymax,self.Bsize)

                self.dX = self.Xrange[1] - self.Xrange[0]
                self.dY = self.Yrange[1] - self.Yrange[0]

		# Store the data

		self.Zdata = sp.flipud(sp.resize(data[:self.Lnum,2],(self.Bnum,self.Bsize)).T)
                #self.Zdata_Original = sp.copy(self.Zdata)


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

        def sv3d(self,fname,comment=""):
            """
            Saves a datafile to a file with filename in the gnuplot format.
            """

            f = open(fname,'w')

            f.write(comment+"\n")

            for i in range(self.Bnum):

                sp.savetxt(f,sp.vstack((self.Xrange[i]*sp.ones(self.Bsize),self.Yrange,self.Zdata[::-1,i])).T)
                f.write("\n")

            f.close()
