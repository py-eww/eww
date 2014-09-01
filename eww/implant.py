# -*- coding: utf-8 -*-
"""
    eww.implant
    ~~~~~~~~~~~

    Provides functions for inserting and removing Eww.

"""

import sys
import logging
import threading
import __builtin__

from .dispatch import DispatchThread
from .ioproxy import IOProxy
from .quitterproxy import QuitterProxy
from .shared import (DISPATCH_THREAD_NAME, EMBEDDED, IMPLANT_LOCK, REMOVAL,
                     STATS_THREAD_NAME)
from .stats import StatsThread

LOGGER = logging.getLogger(__name__)

class WildlyInsecureFlagNotSet(Exception):
    """Raised when someone tries to make Eww listen on an external interface
       without setting the ``wildly_insecure`` flag in their
       :py:mod:`~eww.implant.embed` call.
       """

def embed(host='localhost', port=10000, timeout=1, max_datapoints=500,
          wildly_insecure=False):
    """The main entry point for eww.  It creates the threads we need.

    Args:
        host (str): The interface to listen for connections on.
        port (int): The port to listen for connections on.
        timeout (float): Frequency, in seconds, to check for a stop or
                         remove request.
        max_datapoints (int): The maximum number of graph datapoints to
                              record.  If this limit is hit, datapoints
                              will be discarded based on age, oldest-first.
        wildly_insecure (bool): This must be set to True in order to set
                                the ``host`` argument to anything besides
                                ``localhost`` or ``127.0.0.1``.

    Returns:
        None

    Raises:
        WildlyInsecureFlagNotSet:  Will be raised if you attempt to change
                                   the ``host`` parameter to something
                                   besides ``localhost`` or ``127.0.0.1``
                                   without setting ``wildly_insecure`` to
                                   True.
    """

    if not wildly_insecure:
        try:  # pragma: no cover -- We hit this branch, but coverage disagrees
            allowed = ['localhost', '127.0.0.1', '::1']
            assert host in allowed
        except AssertionError:
            msg = 'You cannot listen on an external interface without setting '
            msg += 'wildly_insecure to True.'
            raise WildlyInsecureFlagNotSet(msg)

    with IMPLANT_LOCK:
        if EMBEDDED.isSet():
            LOGGER.debug('attempted to embed eww more than once')
            return
        EMBEDDED.set()

    LOGGER.debug('eww beginning embed')

    sys.stdin = IOProxy(sys.stdin)
    sys.stdout = IOProxy(sys.stdout)
    sys.stderr = IOProxy(sys.stderr)

    __builtin__.quit = QuitterProxy(__builtin__.quit)
    __builtin__.exit = QuitterProxy(__builtin__.exit)

    dispatch_thread = DispatchThread(str(host), int(port), timeout=timeout)
    dispatch_thread.name = DISPATCH_THREAD_NAME
    dispatch_thread.daemon = True
    dispatch_thread.start()

    stats_thread = StatsThread(max_datapoints=max_datapoints,
                               timeout=timeout)
    stats_thread.name = STATS_THREAD_NAME
    stats_thread.daemon = True
    stats_thread.start()

    LOGGER.debug('eww completed embed')

    return

def remove():
    """Stops and removes all of eww.

    Returns:
        None
    """

    with IMPLANT_LOCK:
        if EMBEDDED.isSet() == False:
            LOGGER.debug('remove called without an embed')
            return
        if REMOVAL.isSet():
            LOGGER.debug('attempted to remove more than once simultaneously')
            return
        REMOVAL.set()

    LOGGER.debug('attempting to remove eww')

    all_threads = threading.enumerate()
    eww_threads = []

    for thread in all_threads:
        if 'eww' in thread.name:
            eww_threads.append(thread)

    for thread in eww_threads:
        thread.stop()
        thread.join(5)

    for thread in eww_threads:
        if thread.isAlive():
            # Our threads haven't stopped.
            LOGGER.debug('failed to remove eww, some threads may be alive')

    __builtin__.quit = __builtin__.quit.original_quit
    __builtin__.exit = __builtin__.exit.original_quit

    sys.stdin = sys.stdin.original_file
    sys.stdout = sys.stdout.original_file
    sys.stderr = sys.stderr.original_file

    with IMPLANT_LOCK:
        EMBEDDED.clear()
        REMOVAL.clear()
        LOGGER.debug('eww removal complete')

    return
