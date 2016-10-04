"""
File loader module.
Load and saves files of different format to and from a data object.

To create a data object, we have to specify the 2d array
and the axes. The calling signature is

df = colorview2d.data(Array, Ranges)

The specification of the ranges is optional.

A fileloader load_* method creates and returns a data object.
A fileloader save_* method creates a file from a data object.
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

    Important: We assume that the ranges on x and y-axes are increasing linearly.
               Only the first and last block is used for the x-axis range and
               the first and the last line of the first block is used for the y-axis.

    Args:
        path (string): Path to the gnuplot-style datafile.
        columns (tuple): A triple of integers specifying the three columns to use.
                         1. column: x-range, 2. column: y-range, 3. column: data
                         default: (0, 1, 2)
    """
    if columns is None:
        columns = (0, 1, 2)

    data = np.genfromtxt(path, usecols=columns, invalid_raise=False)

    # If the array only consists of a single line we reshape explicitly
    # to 2d array
    if len(data.shape) == 1:
        data.shape = (1, 3)

    nlines = data.shape[0]

    bsize = 1

    # Note that the first block is the primer.
    # If the data structure of the first block is not equal to
    # the other blocks, we can not continue.
    for i in range(1, data.shape[0]):
        if data[i,0] != data[i-1,0]:
            bsize = i
            break

    bnum = nlines // bsize
    lnum = bsize * bnum

    # Check integrity
    # first column, the same value has to appear within each block
    for blocknum in range(1, bnum):
        assert np.all(data[blocknum * bsize:(blocknum + 1) * bsize, 0] == data[blocknum * bsize, 0]), \
            "First column of file %s is corrupt in block %d." % (path, blocknum)

    # second column, the same range has to appear for each block
    for blocknum in range(bnum):
        assert np.all(data[blocknum * bsize:(blocknum + 1) * bsize, 1] == data[:bsize, 1]), \
            "Second column of file %s is corrupt in block %d." % (path, blocknum)

    # Store the data

    zdata = np.resize(data[:lnum, 2], (bnum, bsize)).T
    # xyrange = (data[bsize - 1::bsize, 0], data[:bsize, 1])

    # the first and the last block define the x-range
    xleft, xright = (data[0, 0], data[-1, 0])
    # the first and the last line of the first block in the second column define the y-range
    ybottom, ytop = (data[0, 1], data[bsize-1, 1])
    return colorview2d.Data(zdata, ((ybottom, ytop), (xleft, xright)))


def save_gpfile(fname, data, comment=""):
    """
    Saves a data to a file with filename in the gnuplot format.

    Args:
        fname (string): The filename of the ASCII file to contain the data.
        data (colorview2d.Data): The data.
        comment (string): A comment on the data.
    """

    fh = open(fname, 'wb')

    fh.write(comment + "\n")

    for i in range(data.xwidth):
        np.savetxt(
            fh, np.vstack(
                (data.x_range[i] * np.ones(data.ywidth),
                 data.y_range,
                 data.zdata[:, i])).T)
        fh.write("\n")

    fh.close()



