.. _debugging_a_memory_leak:

Debugging a Memory Leak
=======================

To see the kind of power Eww gives you, we're going to use it to diagnose a memory leak.

This script here leaks memory quite badly::

    #! /usr/bin/env python

    class Parent(object):

        def __init__(self):
            self.child = None

        def __del__(self):
            pass

    class Child(object):

        def __init__(self):
            self.parent = None

        def __del__(self):
            pass

    if __name__ == '__main__':

        for _ in range(100):
            parent = Parent()
            child = Child()

            parent.child = child
            child.parent = parent

If only all reference cycles were this simple.

.. note::
    **Why does this leak?**

    Python uses a `reference counting <http://en.wikipedia.org/wiki/Reference_counting>`_ scheme for reaping old objects.  Python keeps track of the number of names attached to objects, and if that number drops to 0, Python will reap that object.

    Python can also handle *most* reference cycles.  The :py:mod:`gc` (garbage collection) module will take care of that for us.

    What the gc can't do is fix reference cycles where **both** objects have a ``__del__`` method.  The gc cannot automatically determine a safe order to run them in, so it refuses to reap either object.

    *This assumes you are using the CPython implementation.  The Python specification does not mention anything about object management, and individual implementations (PyPy, Jython, IronPython) may use different garbage collection techniques.*

Let's, for the exercise, say you've been running this in production for a while and notice that memory usage is constantly growing.