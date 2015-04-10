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
PLOT_AUTOSCALE_OFF = 'Deactivate the autoscaling of the axis on the plot canvas.'
PLOT_AUTOSCALE_ON = 'Activate the autoscaling of the axis on the plot canvas.'

# Signals for the MainPanel
PANEL_UPDATE_COLORCTRL = 'Update the color controls in the MainPanel'
PANEL_ADD_MODWIDGETS = 'Add mod widgets to the MainPanel'


# Signals for the Mod object
MOD_WIDGET_UPDATE = 'Update the mod widgets from the information in the mod'

# Signals for the config panel
CONFIG_UPDATE = 'Update the labeltickframe with the newly parsed config.'