# -*- coding: utf-8 -*-
"""
    tests.utils
    ~~~~~~~~~~~

    A set of helpful utilities during unit testing.

    :copyright: (c) 2014 by Alex Philipp.
    :license: MIT, see LICENSE for more details.
"""

from collections import namedtuple
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import socket
import sys
import time
import threading

import eww

IO = namedtuple('IO', 'stdout stderr')

class CaptureOutput(object):
    """Grabs anything sent to stdout & stderr."""

    def __init__(self, proxy=False):

        self.proxy = proxy

        if proxy:
            pass
        else:
            self.original_stdout = sys.stdout
            self.original_stderr = sys.stderr

    def __enter__(self):
        new_stdout = StringIO()
        new_stderr = StringIO()


        if self.proxy:
            sys.stdout.register(new_stdout)
            sys.stderr.register(new_stderr)
        else:
            sys.stdout = new_stdout
            sys.stderr = new_stderr

        return IO(stdout = new_stdout, stderr = new_stderr)

    def __exit__(self, *args, **kwargs):
        if self.proxy:
            sys.stdout.unregister()
            sys.stderr.unregister()
        else:
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr

def sock_did_output(sock, expected, timeout=5):
    """Waits up to timeout for 'expected' to appear."""

    # Because we are using file objects, we may receive
    # multiple lines at once, but we should not receive
    # partial lines, so no worries about the expected param
    # being chopped up.

    iterations = 0
    while iterations < timeout:
        try:
            msg = sock.recv(1024)
            if expected in msg:
                # Yay
                return True
        except socket.error:
            # Empty response
            time.sleep(0.1)
            iterations += 0.1

    # If we got here, no joy.
    return False

def connect_to_eww(host='localhost', port=10000, retries=20, delay=0.1):
    """Attempts to connect to eww with a configurable delay/retry."""

    sock = None
    connection_attempts = 0

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('localhost', port)
            sock.connect(server_address)
            break
        except socket.error:
            connection_attempts += 1
            if connection_attempts == retries:
                raise
            else:
                time.sleep(delay)

    return sock

def run_command(cmd_obj, args=None, assert_returns=None):
    """Runs a command for us and returns the output."""

    with CaptureOutput() as output:
        assert cmd_obj.run(line=args) == assert_returns
    return IO(stdout = output.stdout.getvalue(),
              stderr = output.stderr.getvalue())

def running_thread_count():
    return len(threading.enumerate())

def expected_thread_count(expected=0, timeout=2):
    total = 0
    while total < timeout:
        if running_thread_count() == expected:
            return True
        time.sleep(0.01)
        total += 0.01

def expected_dict_size(check_dict, expected=0, timeout=2):
    total = 0
    while total < timeout:
        if len(check_dict) == expected:
            return True
        time.sleep(0.01)
        total += 0.01

def expected_counter_value(name, value, timeout=2):
    total = 0
    while total < timeout:
        if eww.shared.COUNTER_STORE[name] == value:
            return True
        time.sleep(0.01)
        total += 0.01

def expected_stat_exists(name, stat_type, timeout=2):
    stat_dict = None
    if stat_type == 'counter':
        stat_dict = eww.shared.COUNTER_STORE
    elif stat_type == 'graph':
        stat_dict = eww.shared.GRAPH_STORE
    else:
        raise

    total = 0
    while total < timeout:
        if name in stat_dict:
            return True
        time.sleep(0.01)
        total += 0.01
