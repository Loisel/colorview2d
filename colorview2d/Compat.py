import os
import sys

def resource_path(relative_path):
    """ Get absolute path to  """
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    return os.path.join(application_path, relative_path)


    