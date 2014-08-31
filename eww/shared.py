# -*- coding: utf-8 -*-
"""
    eww.shared
    ~~~~~~~~~~

    Contains all of our global mutable state.  Everything here is dangerous.

    Because we are a library rather than an app, we're forced to use icky
    things like locks as a defensive mechanism.

    Unless you are very confident in your multithreading skillz (and realize
    you should still have a healthy fear), I strongly recommend not interacting
    with anything here directly.

"""

from Queue import Queue
import threading

DISPATCH_THREAD_NAME = 'eww_dispatch_thread'
STATS_THREAD_NAME = 'eww_stats_thread'

IMPLANT_LOCK = threading.Lock()

EMBEDDED = threading.Event()
REMOVAL = threading.Event()

STATS_QUEUE = Queue(maxsize=500)
COUNTER_STORE = {}
GRAPH_STORE = {}
