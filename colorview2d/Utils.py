import os
import sys
import re
import wx
import logging



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
    """Return the absolute path to a resource"""
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        logging.info("I'm packed to an exe, application path: {}".format(application_path))
    else:
        application_path = os.path.dirname(__file__)
        logging.info("Resource path: {}".format(application_path))
		
    return os.path.join(application_path, relative_path)

def mod_path(relative_path):

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        logging.info("The mods are supposed to be in {}.".format(base_path))
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)	

class SettingsDialog(wx.Dialog):
    def __init__(self,parent,*args,**kwargs):
        wx.Dialog.__init__(self,parent)

        self.mainbox = wx.BoxSizer(wx.VERTICAL)

        self.flags = wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL
        

        self.settingbox = wx.BoxSizer(wx.HORIZONTAL)
        self.column_label = wx.StaticText(self,wx.ID_ANY,'Columns (0 = first col.)')
        self.column_widget = wx.TextCtrl(self,wx.ID_ANY,'0,1,2')

        self.reset_chk = wx.CheckBox(self,wx.ID_ANY,'Reset Config')

        self.settingbox.Add(self.column_label,0,flag=self.flags,border=5)
        self.settingbox.Add(self.column_widget,0,flag=self.flags,border=5)
        self.settingbox.Add(self.reset_chk,0,flag=self.flags,border=5)

        self.mainbox.Add(self.settingbox)
        

        self.loadcancelbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.load_button = wx.Button(self, wx.ID_OK, 'Load')

        self.cancel_button = wx.Button(self, wx.ID_CANCEL)

        self.loadcancelbox.Add(self.load_button,0,flag=self.flags,border=5)
        self.loadcancelbox.Add(self.cancel_button,0,flag=self.flags,border=5)

        self.mainbox.Add(self.loadcancelbox)

        self.SetSizerAndFit(self.mainbox)

    def GetColumns(self):
        return read_columns(self.column_widget.GetValue())

    def GetSettingChk(self):
        return self.reset_chk.GetValue()
    