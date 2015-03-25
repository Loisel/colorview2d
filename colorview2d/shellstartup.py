import numpy as np
import view
import signal
from pydispatch import dispatcher

State = view.State

def update():
    dispatcher.send(signal.PLOT_UPDATE_DATAFILE)
    dispatcher.send(signal.PANEL_UPDATE_COLORCTRL)