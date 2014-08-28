# -*- coding: utf-8 -*-
"""
    eww.ioproxy
    ~~~~~~~~~~~

    We move IOProxy instances into place of the IO files (sys.std[in, out,
    err]). IOProxy provides a thread-local proxy to whatever we want to use
    for IO.

    It is worth mentioning that this is *not* a perfect proxy.  Specifically,
    it doesn't proxy any magic methods.  There are lots of ways to fix that,
    but so far it hasn't been needed.

    If you want to make modification to the IO files, any changes you make
    prior to calling embed will be respected and handled correctly.  If you
    change the IO files after calling embed, everything will break.  Ooof.

    Fortunately, that's a rare use case.  In the event you want to though, you
    can use the register() and unregister() public APIs.  Please see the
    'Public API' section of the documentation for details on using them.

    :copyright: (c) 2014 by Alex Philipp.
    :license: MIT, see LICENSE for more details.
"""

import logging
import threading

LOGGER = logging.getLogger(__name__)

class IOProxy(object):
    """IOProxy provides a proxy object meant to replace sys.std[in, out, err].
    It does not proxy magic methods.  You can register your own file
    customization by calling register()/unregister().  More detail is
    available in the public API documentation.
    """

    def __init__(self, original_file):
        """Creates the thread local and registers the original file."""
        self.io_routes = threading.local()
        self.original_file = original_file
        self.register(original_file)

    def register(self, io_file):
        """Used to register a file for use in a particular thread."""
        self.io_routes.io_file = io_file

    def unregister(self):
        """Used to unregister a file for use in a particular thread."""
        try:
            del self.io_routes.io_file
        except AttributeError:
            LOGGER.debug('unregister() called, but no IO_file registered.')

    def write(self, data, *args, **kwargs):
        """Modify the write method to force a flush so our sockets work
        correctly.
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
        """All other methods and attributes lookups should go to the original
        file.
        """
        return getattr(self.io_routes.io_file, name)
