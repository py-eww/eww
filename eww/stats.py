# -*- coding: utf-8 -*-
"""
    eww.stats
    ~~~~~~~~~

    Eww's stats thread & interface.  Receives and processes stats requests.
    This module also provides some helper functions for stats, as well as
    defining our public API for stats.

"""

from collections import deque, namedtuple
import logging
from Queue import Full, Empty
try:
    import resource
except ImportError:
    # We're on Windows
    pass
import sys

LOGGER = logging.getLogger(__name__)

from .shared import COUNTER_STORE, GRAPH_STORE, STATS_QUEUE
from .stoppable_thread import StoppableThread

Stat = namedtuple('Stat', 'name type action value')

class InvalidGraphDatapoint(Exception):
    """Raised when stats.graph is called with invalid data"""
    pass

class InvalidCounterOption(Exception):
    """Raised when counter methods are called with invalid data"""
    pass

class StatsThread(StoppableThread):
    """StatsThread listens to STATS_QUEUE and processes incoming stats. As a
    StoppableThread subclass, this thread *must* check for the .stop_requested
    flag.
    """

    def __init__(self, max_datapoints=500, timeout=1):
        """Init."""
        super(StatsThread, self).__init__()
        self.timeout = timeout
        self.max_datapoints = max_datapoints

    def process_stat(self, msg):
        """Accepts and processes stats messages."""

        if msg.type == 'counter':

            if msg.name in GRAPH_STORE:
                error = 'Ignoring attempt to write counter stat to a name '
                error += 'used previously for graphs.  Stat name: ' + msg.name
                LOGGER.warning(error)
                return

            if msg.action == 'incr':
                try:
                    COUNTER_STORE[msg.name] += msg.value
                except KeyError:
                    COUNTER_STORE[msg.name] = msg.value

            elif msg.action == 'put':
                COUNTER_STORE[msg.name] = msg.value

            elif msg.action == 'decr':
                try:
                    COUNTER_STORE[msg.name] -= msg.value
                except KeyError:
                    COUNTER_STORE[msg.name] = -msg.value

        elif msg.type == 'graph':

            if msg.name in COUNTER_STORE:
                error = 'Ignoring attempt to write graph stat to a name used '
                error += 'previously for counters.  Stat name: ' + msg.name
                LOGGER.warning(error)
                return

            if msg.action == 'add':
                try:
                    GRAPH_STORE[msg.name].append(msg.value)
                except KeyError:
                    GRAPH_STORE[msg.name] = deque(maxlen=self.max_datapoints)
                    GRAPH_STORE[msg.name].append(msg.value)

    def run(self):
        """Main thread loop."""

        LOGGER.info('Stats thread running')

        while True:
            msg = None
            try:
                msg = STATS_QUEUE.get(timeout=self.timeout)
            except Empty:
                pass

            if self.stop_requested:
                return

            if msg:
                self.process_stat(msg)
                STATS_QUEUE.task_done()

def counter_manipulation(stat):
    """Backend to all counter change."""

    if not isinstance(stat.name, str):
        raise InvalidCounterOption('Name must be a string.')

    if not isinstance(stat.value, int):
        raise InvalidCounterOption('Amount must be an integer.')

    try:
        STATS_QUEUE.put_nowait(stat)
    except Full:
        LOGGER.warning('Stats queue is full.  Stat being silently dropped.')

def incr(name, amount=1):
    """Increments a counter."""

    counter_manipulation(Stat(name=name,
                              type='counter',
                              action='incr',
                              value=amount))

def put(name, amount=1):
    """Puts a counter to a specific value."""

    counter_manipulation(Stat(name=name,
                              type='counter',
                              action='put',
                              value=amount))

def decr(name, amount=1):
    """Reduces a counter."""

    counter_manipulation(Stat(name=name,
                              type='counter',
                              action='decr',
                              value=amount))

def graph(name, datapoint):
    """Adds an X.Y datapoint."""

    if not isinstance(name, str):
        raise InvalidGraphDatapoint('Name must be a string.')

    if not isinstance(datapoint, tuple):
        raise InvalidGraphDatapoint('Passed datapoint is not a tuple')

    if len(datapoint) != 2:
        raise InvalidGraphDatapoint('Passed datapoint is not a 2-member tuple')

    try:
        assert isinstance(datapoint[0], int)
        assert isinstance(datapoint[1], int)
    except AssertionError:
        raise InvalidGraphDatapoint('Datapoint values must be integers')

    try:
        STATS_QUEUE.put_nowait(Stat(name=name,
                                    type='graph',
                                    action='add',
                                    value=datapoint))
    except Full:
        LOGGER.warning('Stats queue is full.  Stat being silently dropped.')

def memory_consumption():
    """Returns memory consumption (specifically, max rss). Currently this
       uses the resource module, and is only available on Unix.  We silently
       return 0 on Windows.
       """

    if 'resource' not in sys.modules:
        return 0

    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
