import numpy as np
import colorview2d.signal as signal
import colorview2d.view as view
from pydispatch import dispatcher

State = view.State

def update():
    dispatcher.send(signal.PLOT_UPDATE_DATAFILE)
    dispatcher.send(signal.PANEL_UPDATE_COLORCTRL)