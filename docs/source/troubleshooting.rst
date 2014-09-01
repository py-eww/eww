.. _troubleshooting:

Troubleshooting
===============

If you're having some trouble that isn't documented here, the best way to get support is by filing a `Github issue <https://github.com/py-eww/eww/issues>`_.

No input or output with Eww client
----------------------------------

Eww proxies :code:`sys.stdin`, :code:`sys.stdout`, and :code:`sys.stderr`.  If you override these as well, you'll break Eww.

If you want to replace the system IO files and use Eww at the same time, you can use the registration function.  Rather than assigning to the files like this::

    sys.stdin = your_custom_file  # Bad!

Use the registration function like so::

    sys.stdin.register(your_custom_file)  # Good!

And, when you want to switch back::

    sys.stdin.unregister()

I can't make Eww listen on a public interface
---------------------------------------------

Check out :ref:`a_note_on_security`.

eww.memory_consumption() always returns 0
-----------------------------------------

That function uses the :py:mod:`resource` module, which isn't available on Windows systems.  Rather than raising an exception and potentially taking your app offline, we return 0 instead.