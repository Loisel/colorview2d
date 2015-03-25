import numpy as np
import view
import signal
from pydispatch import dispatcher

State = view.State

def update():
    dispatcher.send(signal.PLOT_DRAW_ANEW)
