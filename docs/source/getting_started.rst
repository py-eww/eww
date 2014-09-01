.. _getting_started:

Getting Started
===============

Supported Platforms
-------------------

Every Eww release is tested on OSX and Linux.

On each platform, Eww is tested on CPython 2.6, 2.7, and PyPy.

Eww *probably* works on Windows, but we do not make any guarantees, or test anything on Windows.

Installation
------------

Eww is installable via Pip.  Something like this will get you going::

    pip install eww

Installing Eww also provides the Eww client, so you'll want to make sure you install Eww locally if you're connecting to a remote host.

To add Eww to your app, import it and call the embed() function like so::

    import eww
    eww.embed()

You can then connect to the running Eww console using the Eww client::

    basecamp ~: eww
    Welcome to the Eww console. Type 'help' at any point for a list of available commands.
    Running in PID: 93294 Name: ./demo.py
    (eww)

That's about all there is to a basic implementation.  You're ready to see what you can do with Eww on the :ref:`debugging_a_memory_leak` page.