# -*- coding: utf-8 -*-
"""
    eww.ioproxy
    ~~~~~~~~~~~

    We replace ``sys.std[in, out, err]`` with instances of ``IOProxy``.
    ``IOProxy`` provides a thread-local proxy to whatever we want to use
    for IO.

    It is worth mentioning that this is *not* a perfect proxy.  Specifically,
    it doesn't proxy any magic methods.  There are lots of ways to fix that,
    but so far it hasn't been needed.

    If you want to make modification to sys.std[in, out, err], any changes you
    make prior to calling embed will be respected and handled correctly.  If
    you change the IO files after calling embed, everything will break.  Ooof.

    Fortunately, that's a rare use case.  In the event you want to though, you
    can use the register() and unregister() public APIs.  Check out the
    :ref:`troubleshooting` page for more information.

"""

import logging
import threading

LOGGER = logging.getLogger(__name__)

class IOProxy(object):
    """IOProxy provides a proxy object meant to replace sys.std[in, out, err].
    It does not proxy magic methods.  It is used by calling the object's
    register and unregister methods.
    """

    def __init__(self, original_file):
        """Creates the thread local and registers the original file.

        Args:
           original_file (file): Since IOProxy is used to replace an
                                 existing file, ``original_file`` should be
                                 the file you're replacing.
        """
        self.io_routes = threading.local()
        self.original_file = original_file
        self.register(original_file)

    def register(self, io_file):
        """Used to register a file for use in a particular thread.

        Args:
            io_file (file): ``io_file`` will override the existing file, but
                            only in the thread ``register`` is called in.

        Returns:
            None
        """
        self.io_routes.io_file = io_file

    def unregister(self):
        """Used to unregister a file for use in a particular thread.

        Returns:
            None
        """
        try:
            del self.io_routes.io_file
        except AttributeError:
            LOGGER.debug('unregister() called, but no IO_file registered.')

    def write(self, data, *args, **kwargs):
        """Modify the write method to force a flush after each write so our
        sockets work correctly.

        Args:
            data (str): A string to be written to the file being proxied.

        Returns:
            None
        """
        try:
            self.io_routes.io_file.write(data, *args, **kwargs)
            self.io_routes.io_file.flush()
        except AttributeError as exception:
            LOGGER.debug('Error calling IOProxy.write: ' + str(exception)
                         + ' Msg: ' + str(data))
        except IOError as exception:
            # This can happen when a console thread is forcibly stopped
            LOGGER.debug('Caught error while writing: ' + str(exception))

    def __getattr__(self, name):
        """All other methods and attributes lookups go to the original
        file.
        """
        return getattr(self.io_routes.io_file, name)
