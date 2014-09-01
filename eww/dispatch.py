# -*- coding: utf-8 -*-
"""
    eww.dispatch
    ~~~~~~~~~~~~

    Eww's dispatch thread.  Listens for incoming connections and creates
    consoles for them.

"""
# Pylint will warn on the select statement.  It's there for future expansion.
# pylint: disable=unused-variable

import logging
import select
import socket

from .console import ConsoleThread
from .stoppable_thread import StoppableThread

LOGGER = logging.getLogger(__name__)

class DispatchThread(StoppableThread):
    """``DispatchThread`` runs the connection listener thread. As a
    StoppableThread subclass, this thread *must* check for the .stop_requested
    flag.
    """

    def __init__(self, host, port, timeout=1):
        """Init.

           Args:
               host (str): The interface to listen for connections on.
               port (int): The port to listen for connections on.
               timeout (float): Frequency, in seconds, to check for a stop or
                                remove request.
        """
        super(DispatchThread, self).__init__()
        self.server_address = (host, port)
        self.timeout = timeout

    def run(self):
        """Main thread loop.

           Returns:
               None
        """

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_socket.bind(self.server_address)
        except socket.error as exception:
            LOGGER.error('Dispatch thread could not bind: ' + str(exception))
            return
        server_socket.listen(5)
        LOGGER.info('Dispatch thread bound and listening')

        inputs = [server_socket]

        while True:
            # We don't strictly need select here, but it makes timeout
            # checking easier.  It also makes it easier to add PTY/TTY
            # down the line.
            readable, writable, errored = select.select(inputs,
                                                        [],
                                                        inputs,
                                                        self.timeout)

            for sock in readable:
                if sock is server_socket:
                    user_socket, addr = sock.accept()  # pragma: no cover

                    user_thread = ConsoleThread(user_socket)
                    user_thread.daemon = True
                    user_thread.name = 'eww_console_' + str(addr)
                    user_thread.start()

            if self.stop_requested:
                try:
                    server_socket.shutdown(socket.SHUT_RDWR)
                except socket.error:  # pragma: no cover
                    # If we don't have an active connection this will raise,
                    # just pass.
                    pass
                server_socket.close()
                return
