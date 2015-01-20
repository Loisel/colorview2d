import os
import sys
import re

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

def resource_path(relative_path):
    """ Get absolute path to  """
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    return os.path.join(application_path, relative_path)


    