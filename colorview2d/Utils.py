import os
import sys
import re
import wx
import wx.lib.customtreectrl as customtreectrl


def read_columns(string):
    """
    Utility function to read columns in the python format (a,b,c) out of a string.
    """
    p = re.compile('(\d+),(\d+),(\d+)')
    m = p.match(string)

    if m:
        column = (int(m.groups()[0]),int(m.groups()[1]),int(m.groups()[2]))
        return column
    else:
        raise InputError('Not a valid column string: {}'.format(string))


def write_columns(tup):
    return "{},{},{}".format(tup[0],tup[1],tup[2])

        
def resource_path(relative_path):
    """ Get absolute path to  """
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    return os.path.join(application_path, relative_path)


class LoadFileDialog(customtreectrl.CustomTreeCtrl):
    FOLDER,ERROR,FILE = range(3)

    def __init__(self, parent, *args, **kwargs):

        super(LoadFileDialog,self).__init__(parent, *args, **kwargs)
