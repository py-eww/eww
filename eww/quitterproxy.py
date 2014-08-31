# -*- coding: utf-8 -*-
"""
    eww.quitterproxy
    ~~~~~~~~~~~~~~~~

    QuitterProxy is a :py:class:`threading.local`-based proxy used to override
    the normal quit behavior on demand.  It is very similar to IOProxy, but
    rather than proxying files, it proxies Quitter objects.  We need to do this
    so calling exit() or quit() in the REPL won't kill the console connection.

    This is because calling quit()/exit() will raise the SystemExit exception,
    *and* close stdin.  We can catch the SystemExit exception, but if stdin is
    closed, it kills our socket.

    Normally that's exactly the behavior you want, but because we embed a REPL
    in the Eww console, exiting the REPL can cause the entire session to exit,
    not just the REPL.

    If you want to make modifications to the quit or exit builtins, you can use
    the public register/unregister APIs on QuitterProxy for it.  It works the
    same way as on :py:mod:`~eww.ioproxy.IOProxy` objects.

"""

import threading
import logging

LOGGER = logging.getLogger(__name__)

class QuitterProxy(object):
    """QuitterProxy provides a proxy object meant to replace __builtin__.[quit,
    exit].  You can register your own quit customization by calling
    register()/unregister().
    """

    def __init__(self, original_quit):
        """Creates the thread local and registers the original quit.

        Args:
            original_quit (Quitter): The original quit method.  We keep a
                                     reference to it since we're replacing it.
        """
        self.quit_routes = threading.local()
        self.original_quit = original_quit
        self.register(original_quit)

    def __repr__(self):
        """We just call self here, that way people can use e.g. 'exit' instead
        of 'exit()'.
        """
        self()

    def register(self, quit_method):
        """Used to register a quit method in a particular thread.

        Args:
            quit_method (callable): A callable that will be called instead of
                                    ``original_quit``.

        Returns:
            None
        """
        self.quit_routes.quit = quit_method

    def unregister(self):
        """Used to unregister a quit method in a particular thread.

        Returns:
            None
        """
        try:
            del self.quit_routes.quit
        except AttributeError:
            LOGGER.debug('unregister() called, but no quit method registered.')

    def __call__(self, code=None):
        """Calls the registered quit method.

        Args:
            code (str): A quit message.
        """
        try:
            self.quit_routes.quit(code)
        except AttributeError:
            self.original_quit(code)

def safe_quit(code=None):
    """This version of the builtin quit method raises a SystemExit, but does
    *not* close stdin.

    Args:
        code (str): A quit message.
    """
    raise SystemExit(code)
