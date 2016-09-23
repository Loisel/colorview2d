import os
import sys
import re
import wx
import logging

class ConfigDict(dict):
    def __init__(self, cvfig, *args, **kwargs):
        self.update(*args, **kwargs)
        self.cvfig = cvfig

    def __setitem__(self, key, value):
        if key not in self.cvfig._config.keys():
            raise KeyError('Not a valid configuration key %s.' % key)

        super(ConfigDict, self).__setitem__(key, value)
        # When there is no plot we do not care at the moment.
        if not self.cvfig.plotting:
            return
            
        if key == 'Colormap':
            self.cvfig._plot.set_cmap(self.cvfig._config['Colormap'])
        elif key == 'Cbmin':
            if value == 'auto':
                self.cvfig._plot.set_clim(vmin=self.cvfig._datafile.zmin)
            else:
                self.cvfig._plot.set_clim(vmin=self.cvfig._config['Cbmin'])
        elif key == 'Cbmax':
            if value == 'auto':
                self.cvfig._plot.set_clim(vmax=self.cvfig._datafile.zmax)
            else:
                self.cvfig._plot.set_clim(vmax=self.cvfig._config['Cbmax'])

        if key in ['Colormap', 'Cbmin', 'Cbmax']:
            self.cvfig._plot.changed()
            return

        # If config_dict only contains changes that do not need a redrawing
        # of the plot we apply them and return
        if key in ['Xlabel', 'Ylabel', 'Xtickformat', 'Ytickformat', 'Cblabel']:
            self.cvfig._apply_config_post_plot()
            return

        # If the font parameters, the ticksize or the format of the colorbar ticks
        # is changed, we have to redraw the plot
        self.cvfig.draw_plot()

        
    def update_raw(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, "
                                "got %d" % len(args))
            other = dict(args[0])
            for key in other:
                super(ConfigDict, self).__setitem__(key, other[key])

        for key in kwargs:
            super(ConfigDict, self).__setitem__(key, kwargs[key])


    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, "
                                "got %d" % len(args))
            other = dict(args[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value
        return self[key]

class Line():
    """
    Represents a line drawn in a matplotlib axes object.

    This is a utility class that provides mainly slope and shift of the line.
    Lines can also be labeled in the plot.

    Attributes:
      x1,x2,y1,y2 (float): Two points defining the line.
      comment (string): A string describing the line.
      axes (matplotlib axes): Axes object to create the line in.
      line (matplotlib line): The lineplot associated with the axes object.
      commenttext (matplotlib text): The commenttext plotted in the axes object.
    """
    def __init__(self,axes,x1, x2, y1, y2, comment = None, position = None, **args):
        self.x1 = x1
        self.y1 = y1
        self.y2 = y2
        self.x2 = x2
        
        self.comment = comment

        self.dx = self.x2-self.x1
        self.dy = self.y2-self.y1

        self.addline(axes, comment = comment, position = position)
        
    def __del__(self):
        try:
            self.removeline()
        except ValueError:
            logging.debug("Line already deleted.")
            
    def addline(self,axes, comment = None, position = None,**args):
        self.axes = axes
        if comment:
            if position is None:
                position = self.x1, self.y1+0.5
            self.commenttext = self.axes.text(position[0], position[1], comment)
        self.line, = self.axes.plot([self.x1,self.x2],[self.y1,self.y2], **args)

    def removeline(self):
        if hasattr(self,'commenttext'):
            try:
                self.commenttext.remove()
            except ValueError:
                logging.debug('Can not remove linetext properly.')
        self.line.remove()

    def set_data(self,x1,x2,y1,y2):
        self.x1 = x1
        self.y1 = y1
        self.y2 = y2
        self.x2 = x2

        self.dx = self.x2-self.x1
        self.dy = self.y2-self.y1

        self.line.set_data([x1,x2],[y1,y2])

    def set_comment(self,comment, position = None):
        if position is None:
            position = self.x1, self.y1-0.5
        self.comment = comment
        if hasattr(self,'commenttext'):
            self.commenttext.remove()
        self.commenttext = self.axes.text(position[0],position[1],self.comment)


    def get_slope(self):        
        try:
            return self.dy/self.dx
        except ZeroDivisionError:
            print "Slope not defined for a perpendicular line."
        
    def get_shift(self):
        return self.y1-self.get_slope()*self.x1
            
    def get_y(self,x):
        return x*self.get_slope()+self.get_shift()

    def get_x(self,y):
        return (y-self.get_shift())/self.get_slope()

    def get_comment(self):
        return self.comment


class DistanceLine(Line):
    def __init__(self, axes, x1, x2, y1, y2, horizontal):

        self.axes = axes
        self.horizontal = horizontal
        
        self.x1 = x1
        self.y1 = y1
        self.y2 = y2
        self.x2 = x2
        
        self.dx = self.x2-self.x1
        self.dy = self.y2-self.y1

        if self.horizontal:
            self.marker = '|'
        else:
            self.marker = '_'
            
        self.addline(axes)

    def get_distance(self):
        if self.horizontal:
            return "{:1.3e}".format(self.dx)
        else:
            return "{:1.3e}".format(self.dy)

    def set_distancelabel(self):
        self.set_comment(self.get_distance(), position = self.get_position()) 
            
    def get_position(self):
        if self.horizontal:
            pixel_coord = self.axes.transData.transform(((self.x1+self.x2)/2.,self.y1))+[0,5.]
        else:
            pixel_coord = self.axes.transData.transform((self.x1, (self.y1+self.y2)/2.))+[5.,0]
        inv = self.axes.transData.inverted()
        return inv.transform(pixel_coord)

    def addline(self,axes):
        Line.addline(self, axes, comment = self.get_distance(), position = self.get_position(), marker = self.marker, markersize = 10)
        


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
    
