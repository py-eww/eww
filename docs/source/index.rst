Welcome to Eww's documentation
==============================

.. image:: https://travis-ci.org/py-eww/eww.svg?branch=master
    :target: https://travis-ci.org/py-eww/eww
.. image:: https://coveralls.io/repos/py-eww/eww/badge.png
    :target: https://coveralls.io/r/py-eww/eww
.. image:: https://readthedocs.org/projects/eww/badge/?version=latest
    :target: https://readthedocs.org/projects/eww/?badge=latest

|

Eww is a pretty nifty tool for debugging and introspecting running Python programs.

Eww gives you access to a Python REPL *inside* of your running application.  Also, pretty awesome statistics and graphing tools.

Using Eww is as simple as adding this to your Python app::

    import eww
    eww.embed()

And then connecting from your terminal::

    basecamp ~: eww
    Welcome to the Eww console. Type 'help' at any point for a list of available commands.
    (eww)

That's it.

If you're brand new to Eww, you'll want to head on over to :ref:`getting_started`.

Looking to contribute to Eww?  Check out our :ref:`contributing` guide.

.. toctree::
   :maxdepth: 2
   :hidden:

   getting_started
   debugging_leak
   security
   statistics
   versioning_compatibility
   troubleshooting
   internals
   contributing
   api
