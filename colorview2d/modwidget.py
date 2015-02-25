"""
ModWidget
---------

Module provides the base class for plugin widgets.

It contains a checkbox widget and can be used
directly in a mod plugin.

:copyright: 2014 by Alois Dirnaichner
:license: GPLv3, see LICENSE for more details
"""

import wx

class ModWidget(wx.BoxSizer):
    """
    Base class for the plugin widgets that can be provided
    to colorview2d.

    The widget is a descendant of wx.BoxSizer.
    Childs should call init and update upon overwrite.

    :ivar mod: The mod class this widget is assigned to
    :ivar panel: The panel this widget lives on
    :ivar title: The title of the mod.
    :ivar chk: A handle for the checkbox widget.

    """
    flags = wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL

    def __init__(self,mod,panel):
        wx.BoxSizer.__init__(self,wx.HORIZONTAL)
        self.mod = mod
        self.panel = panel
        self.title = self.mod.title
        self.chk = wx.CheckBox(self.panel, wx.ID_ANY, self.title)
        self.Add(self.chk,0,self.flags,border=10)
        self.panel.Bind(wx.EVT_CHECKBOX,self.on_chk,self.chk)

    def update(self):
        """
        Update the mod widget to comply with the state of the mod.
        Should update all widgets contained in the ModWidget descendant.
        """
        self.chk.SetValue(self.mod.active)

    def on_chk(self,event):
        """
        Handler for the event that is triggered by activating/deactivating
        the checkbox.

        It is not required to overwrite this function in a custom plugin implementation.
        """
        if self.chk.GetValue():
            self.mod.activate()
        else:
            self.mod.deactivate()

    
        