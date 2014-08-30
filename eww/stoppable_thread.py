# -*- coding: utf-8 -*-
"""
    eww.stoppable_thread
    ~~~~~~~~~~~~~~~~~~~~

    threading.Thread class that exposes a stop API.  Subclasses of this
    must check for .stop_requested regularly.

"""

import threading

class StoppableThread(threading.Thread):
    """Thread class that adds a stop() method.  Subclasses *must* check for the
    .stop_requested event regularly.
    """

    def __init__(self):
        """Init."""
        super(StoppableThread, self).__init__()
        self.stop_requested = False

    def stop(self):
        """Sets the stop_requested flag."""
        self.stop_requested = True
