.. _a_note_on_security:

A Note on Security
==================

It is critical to understand three things about Eww and security:

* Eww traffic is unencrypted
* Eww does not have any authentication
* Anyone that can connect to Eww will have read and write access to everything your app (and the user running it) has

By default, Eww listens on :code:`localhost:10000`.  This means that to connect to Eww, you must be on the same box as the application running Eww.

This can cause issues for developers that use several virtual machines on their local boxes and want to use Eww from the host operating system.  To support that, you can configure Eww to listen on any IP and port you'd like::

    eww.embed(host='8.8.8.8', port=31337, wildly_insecure=True)

If you do not specify the wildly_insecure flag, Eww will immediately raise an exception if you try to listen on a non-internal address.

SSH support is planned to address these issues.