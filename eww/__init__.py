# -*- coding: utf-8 -*-
"""
    eww
    ~~~

    Eww is a debugging framework that does some really cool stuff.

"""

__version__ = '1.0.0'

from .implant import embed, remove
from eww.stats import incr, put, decr, graph, memory_consumption
