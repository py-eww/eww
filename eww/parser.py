# -*- coding: utf-8 -*-
"""
    eww.parser
    ~~~~~~~~~~

    We need to make some modifications to :py:mod:`optparse` for our
    environment.  This module creates a subclass of :py:mod:`optparse` with
    the necessary changes.

"""
# Pylint warns about too many public methods.  That's optparse's fault.
# pylint: disable=too-many-public-methods

import optparse

class ParserError(Exception):
    """We create a custom exception here to be raised on error.  That way
    we can safely handle parser errors and do something useful with them.
    """
    pass

class Parser(optparse.OptionParser):
    """Our lightly modified version of optparse."""

    def __init__(self, *args, **kwargs):
        """Init.  The only change here is forcing the help option off.  We
        could do this at instantiation, but it's cleaner to do it here.
        """
        kwargs['add_help_option'] = False
        optparse.OptionParser.__init__(self, *args, **kwargs)

    def error(self, msg):
        """We override error here to prevent us from exiting.  Optparse does
        not expect this to return, but that's not really a problem for us
        since each command can be abstractly considered a different, new
        script.

        Args:
            msg (str): The error message that will be passed to the ParserError
                       exception.

        Raises:
            ParserError: Raised when a command cannot be parsed.
        """
        raise ParserError(msg)

class Opt(optparse.Option):
    """We don't need to change anything here; we're subclassing this for
    consistency.
    """
    pass
