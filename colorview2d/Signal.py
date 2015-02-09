"""
This module contains all signals that are used by colorview2d.
The signals contain a string specifying the purpose in more detail.

We always put the (main) recipient as the first part of the signal name.
"""


# Signals for the PlotPanel
PLOT_UPDATE_COLOR = 'Update the colors in the plot'
PLOT_DRAW_ANEW = 'Redraw the plot from the start'
PLOT_UPDATE_DATAFILE = 'Replace the datafile in the plot'
PLOT_CHANGE_COLORMAP = 'Change the colormap in the plot'
PLOT_UPDATE_CANVAS = 'Redraw all objects in the plot canvas'
PLOT_CHANGE_CONFIG =  'Update the labels, ticks and plot size from the config.'


# Signals for the MainPanel
PANEL_UPDATE_COLORCTRL = 'Update the color controls in the MainPanel'
PANEL_ADD_MODWIDGETS = 'Add mod widgets to the MainPanel'


# Signals for the Mod object
MOD_WIDGET_UPDATE = 'Update the mod widgets from the information in the mod'


# Signals for the View object
VIEW_ADD_MOD_TO_PIPELINE = 'Add a mod to the view mod pipeline'
VIEW_REMOVE_MOD_FROM_PIPELINE = 'Remove a mod from the view mod pipeline'