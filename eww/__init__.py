# -*- coding: utf-8 -*-
"""
    eww
    ~~~

    Eww is a debugging framework that does some really cool stuff.

"""

__version__ = '0.0.1'

from .implant import embed, remove
from eww.stats import incr, put, decr, graph, memory_consumption
