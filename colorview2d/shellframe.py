import wx
import wx.py.shell
import utils

class ShellFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent, title="Python shell",size=(800,600))
        self.parent = parent
        self.Shell = Shell(self)
        self.Layout()


class Shell(wx.py.shell.Shell):
    def __init__(self,parent):
        Text = """A colorview2d interactive python shell

The State object is made available as State.
Type update() to send a signal to draw the plot."""
        wx.py.shell.Shell.__init__(self, parent, introText = Text, startupScript = utils.resource_path("shellstartup.py"))


            