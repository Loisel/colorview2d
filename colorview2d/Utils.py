import os
import sys
import re
import wx
import logging
import wx.lib.customtreectrl as customtreectrl

def set_default_font():
    # We select the default matplotlib font
    # To that end we catch the warning -- not particularly elegant
    if View.State.config['Font'] == 'default':
        for font in plt.rcParams['font.sans-serif']:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                findfont(FontProperties(family=font))
                if len(w):
                    continue
                else:
                    View.State.config['Font'] = font
                    break


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
    
class FileBrowser(customtreectrl.CustomTreeCtrl):
    FOLDER, \
    ERROR, \
    FILE = range(3)
    def __init__(self, parent, rootdir, *args, **kwargs):
        super(FileBrowser, self).__init__(parent,
                                          *args,
                                          **kwargs)
        assert os.path.exists(rootdir), \
               "Invalid Root Directory!"
        assert os.path.isdir(rootdir), \
               "rootdir must be a Directory!"

        # Attributes
        self._il = wx.ImageList(16, 16)
        self._root = rootdir
        self._rnode = None

        # Setup
        for art in (wx.ART_FOLDER, wx.ART_ERROR,
                    wx.ART_NORMAL_FILE):
            bmp = wx.ArtProvider.GetBitmap(art, size=(16,16))
            self._il.Add(bmp)
        self.SetImageList(self._il)
        self._rnode = self.AddRoot(os.path.basename(rootdir),
                                   image=FileBrowser.FOLDER,
                                   data=self._root)
        self.SetItemHasChildren(self._rnode, True)
        # use Windows-Vista-style selections
        self.EnableSelectionVista(True)

        # Event Handlers
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING,
                  self.OnExpanding)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED,
                  self.OnCollapsed)

    def _GetFiles(self, path):
        try:
            files = [fname for fname in os.listdir(path)
                     if fname not in ('.', '..')]
        except OSError:
            files = None
        return files


    def OnCollapsed(self, event):
        item = event.GetItem()
        self.DeleteChildren(item)

    def OnExpanding(self, event):
        item = event.GetItem()
        path = self.GetPyData(item)
        files = self._GetFiles(path)

        # Handle Access Errors
        if files is None:
            self.SetItemImage(item, FileBrowser.ERROR)
            self.SetItemHasChildren(item, False)
            return

        for fname in files:
            fullpath = os.path.join(path, fname)
            if os.path.isdir(fullpath):
                self.AppendDir(item, fullpath)
            else:
                self.AppendFile(item, fullpath)


    def AppendDir(self, item, path):
        """Add a directory node"""
        assert os.path.isdir(path), "Not a valid directory!"
        name = os.path.basename(path)
        nitem = self.AppendItem(item, name,
                                image=FileBrowser.FOLDER,
                                data=path)
        self.SetItemHasChildren(nitem, True)

    def AppendFile(self, item, path):
        """Add a file to a node"""
        assert os.path.isfile(path), "Not a valid file!"
        name = os.path.basename(path)
        self.AppendItem(item, name,
                        image=FileBrowser.FILE,
                        data=path)

    def GetSelectedPath(self):
        """Get the selected path"""
        sel = self.GetSelection()
        path = self.GetItemPyData(sel)
        return path

    def GetSelectedPaths(self):
        """Get a list of selected paths"""
        sels = self.GetSelections()
        paths = [self.GetItemPyData(sel)
                 for sel in sels ]
        return paths
