Welcome to Eww's documentation
==============================

.. image:: https://travis-ci.org/py-eww/eww.svg?branch=master
    :target: https://travis-ci.org/py-eww/eww
.. image:: https://img.shields.io/coveralls/py-eww/eww.svg
    :target: https://coveralls.io/r/py-eww/eww
.. image:: https://readthedocs.org/projects/eww/badge/?version=latest
    :target: https://readthedocs.org/projects/eww/?badge=latest
|
.. image:: https://pypip.in/py_versions/eww/badge.svg
    :target: https://pypi.python.org/pypi/eww
.. image:: https://pypip.in/implementation/eww/badge.svg
    :target: https://pypi.python.org/pypi/eww
.. image:: https://pypip.in/license/eww/badge.svg
    :target: https://pypi.python.org/pypi/eww
|

Eww is a pretty nifty tool for debugging and introspecting running Python programs.

Eww gives you access to a Python REPL *inside* of your running application, plus easy to use statistics and graphing tools.

Using Eww involves adding two lines to your app::

    import eww
    eww.embed()

And then connecting from your terminal::

    basecamp ~: eww
    Welcome to the Eww console. Type 'help' at any point for a list of available commands.
    Running in PID: 93294 Name: ./demo.py
    (eww)

That's it.

If you're brand new to Eww, you'll want to head on over to :ref:`getting_started`.

Looking to contribute to Eww?  Check out our :ref:`contributing` guide.

.. toctree::
   :maxdepth: 2
   :hidden:

   Introduction <self>
   getting_started
   debugging_leak
   security
   statistics
   versioning_compatibility
   troubleshooting
   contributing
   api/index
