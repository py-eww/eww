.. _versioning:

Versioning and Compatibility
============================

Eww follows the `semantic versioning <http://semver.org/>`_ specification.

That means:

* Eww's versions are denoted by three integers: MAJOR.MINOR.PATCH
* The PATCH number is incremented on bugfixes
* The MINOR number is incremented when backwards-compatible functionality is added
* The MAJOR number is incremented when the public API is changed

The Public API
--------------

The public API, for the purpose of ensuring compatibility, is enumerated here:

* :py:mod:`eww.embed <eww.implant.embed>`
* :py:mod:`eww.remove <eww.implant.remove>`
* :py:mod:`eww.incr <eww.stats.incr>`
* :py:mod:`eww.put <eww.stats.put>`
* :py:mod:`eww.decr <eww.stats.decr>`
* :py:mod:`eww.graph <eww.stats.graph>`
* :py:mod:`eww.memory_consumption <eww.stats.memory_consumption>`
* :py:mod:`sys.stdin.register <eww.ioproxy.IOProxy.register>`
* :py:mod:`sys.stdin.unregister <eww.ioproxy.IOProxy.unregister>`
* :py:mod:`sys.stdout.register <eww.ioproxy.IOProxy.register>`
* :py:mod:`sys.stdout.unregister <eww.ioproxy.IOProxy.unregister>`
* :py:mod:`sys.stderr.register <eww.ioproxy.IOProxy.register>`
* :py:mod:`sys.stderr.unregister <eww.ioproxy.IOProxy.unregister>`
* :py:mod:`__builtin__.quit.register <eww.quitterproxy.QuitterProxy.register>`
* :py:mod:`__builtin__.quit.unregister <eww.quitterproxy.QuitterProxy.unregister>`
* :py:mod:`__builtin__.exit.register <eww.quitterproxy.QuitterProxy.register>`
* :py:mod:`__builtin__.exit.unregister <eww.quitterproxy.QuitterProxy.unregister>`

New functionality may be added to these functions but, on the same major version number, all changes are guaranteed to be backwards-compatible.

Client Compatibility
--------------------

Any client in the same MAJOR version as the server can be used to connect to the server.

What constitutes backwards-compatible?
--------------------------------------

The interfaces listed above will always adhere to their documentation, and that documentation will not be changed (but may be extended) in the same major version.

The documentation is considered the sole source of truth and defines the details of the public API contract.

Practically, that means that if the code does something that the documentation does not agree with, the code is wrong and it will be fixed.

Here are a few examples of what Eww considers non-breaking changes:

* Adding a new configuration option to eww.embed with a default setting that preserves the existing contract
* Adding a new item to the public API
* Fixing a public API method that is documented to return ``True`` in certain circumstances, but mistakenly returns ``None``

And breaking changes:

* Requiring a new option in a public API call
* Changing the documentation of a public API call, rather than extending it
* Removing a public API call
* Renaming a public API call

My goal is to make this clear to understand.  The description above is the 'letter of the law', but the spirit is straightforward: we will not break your implementation.

Specifying a Version
--------------------

Rather than specifying a specific version in your requirements.txt file, you should specify anything in the same MAJOR series.

E.g., if you are currently using 2.1.1, you should specify Eww in your requirements.txt as::

    eww>=2.0.0,<3