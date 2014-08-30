Versioning and Compatibility
============================

Eww follows the `semantic versioning <http://semver.org/>`_ specification.

That means:

* Eww's versions are denoted by three integers: MAJOR.MINOR.PATCH
* The PATCH number is incremented on bugfixes and documentation changes
* The MINOR number is incremented when backwards-compatible functionality is added
* The MAJOR number is incremented when the public API is changed

The Public API
--------------

The public API is defined as anything exported in :code:`eww/__init__.py`.  That includes:

* :code:`eww.embed`
* :code:`eww.remove`
* :code:`eww.incr`
* :code:`eww.put`
* :code:`eww.decr`
* :code:`eww.graph`
* :code:`eww.memory_consumption`

New functionality may be added to these functions but, on the same major version number, all changes are guaranteed to be backwards-compatible.

Specifying a Version
--------------------

Rather than specifying a specific version in your requirements.txt file, you should specify anything in the same MAJOR series.

E.g., if you are currently using 2.1.1, you should specify Eww in your requirements.txt as::

    eww>=2.0.0,<3