"""
File loader module.
Load and saves files of different format to and from a datafile object.

To create a datafile object, we have to specify the 2d array
and the axes. The calling signature is

df = colorview2d.datafile(Array, Ranges)

The specification of the ranges is optional.

A fileloader load_* method creates and returns a datafile object.
A fileloader save_* method creates a file from a datafile object.
"""

import numpy as np
import colorview2d

def load_gpfile(path, columns=None):
    """
    Load a gnuplot file.
    A gnuplot file consists of plain text data. It is organised in blocks separated by
    newlines. Each block has multiple columns specifying the data.
    You can specify the three columns using the columns argument, default is (0, 1, 2).

    Normally, the first column is constant for the whole block. It specifies the values
    on the x-axis, i.e., one block contains the data for one vertical row in the 2d array.
    The second column specifies the values on the y-axis.

    The last, third, column specifies the actual data for the x and y coordinate given.

    Args:
        path (string): Path to the gnuplot-style datafile.
        columns (tuple): A triple of integers specifying the three columns to use.
                         1. column: x-range, 2. column: y-range, 3. column: data
                         default: (0, 1, 2)
    """
    if columns is None:
        columns = (0, 1, 2)

    data = np.loadtxt(path, usecols=columns)
    nlines = data.shape[0]

    bnum = 0

    for i in range(1, data.shape[0]):
        if data[i,0] != data[i-1,0]:
            bsize = i
            break

    bnum = nlines / bsize
    lnum = bsize * bnum
    # Store the data

    zdata = (np.resize(data[:lnum, 2], (bnum, bsize)).T)
    xyrange = (data[bsize - 1::bsize, 0], data[:bsize, 1])

    return colorview2d.Datafile(zdata, xyrange)


def save_gpfile(fname, datafile, comment=""):
    """
    Saves a datafile to a file with filename in the gnuplot format.

    Args:
        fname (string): The filename of the ASCII file to contain the data.
        datafile (colorview2d.Datafile): The datafile containing the data.
        comment (string): A comment on the data.
    """

    fh = open(fname, 'w')

    fh.write(comment + "\n")

    for i in range(datafile.xrange.size):
        np.savetxt(
            fh, np.vstack(
                (datafile.xrange[i] * np.ones(datafile.yrange.shape[0]),
                 datafile.yrange,
                 datafile.zdata[:, i])).T)
        fh.write("\n")

    fh.close()



