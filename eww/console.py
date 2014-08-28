# -*- coding: utf-8 -*-
"""
    eww.console
    ~~~~~~~~~~~

    This implements eww's primary console thread.  It creates an instance of
    command.Command() for each new connection and handles all of the support
    for it (proxies and the like).

    :copyright: (c) 2014 by Alex Philipp.
    :license: MIT, see LICENSE for more details.
"""
# We *could* make register/unregister functions, but they aren't as meaningful
# outside of ConsoleThread.
# pylint: disable=no-self-use, no-member

import logging
import socket
import sys
import threading

from .command import Command

LOGGER = logging.getLogger(__name__)

class ConsoleThread(threading.Thread):
    """An instance of ConsoleThread is created for each attached user.  It
    implements all the features needed to make a nifty debugger.
    """

    def __init__(self, user_socket):
        """Sets up our socket and socket_file."""
        super(ConsoleThread, self).__init__()
        self.user_socket = user_socket
        self.user_socket_file = user_socket.makefile()

    def register_io(self):
        """Registers the correct IO streams for the thread."""
        sys.stdin.register(self.user_socket_file)
        sys.stdout.register(self.user_socket_file)
        sys.stderr.register(self.user_socket_file)

    def unregister_io(self):
        """Unregisters the custom IO streams for the thread."""
        sys.stdin.unregister()
        sys.stdout.unregister()
        sys.stderr.unregister()

    def stop(self):
        """Can be used to forcibly stop the thread."""
        self.user_socket.shutdown(socket.SHUT_RDWR)

    def cleanup(self):
        """Cleans up our thread."""
        print 'Disconnecting...'
        try:
            self.user_socket_file.close()
        except IOError:
            # If the underlying socket has been forcibly closed,
            # then we'll have a broken pipe on our hands.
            pass
        self.user_socket.close()
        self.unregister_io()

    def run(self):
        """Sets up our IO and starts a Console instance."""
        try:
            self.register_io()
            command = Command()
            command.intro = 'Welcome to the Eww console. Type \'help\' at any '
            command.intro += 'point for a list of available commands.'
            command.prompt = '(eww) '
            command.cmdloop()
        except Exception as catchall:  # pylint: disable=broad-except
            LOGGER.debug('Console thread died: ' + str(catchall))
        finally:
            self.cleanup()
