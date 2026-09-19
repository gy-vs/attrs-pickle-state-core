Glossary
========

.. glossary::

   dict classes
      A regular class whose attributes are stored in the ``__dict__`` attribute of every single instance.
      This is quite wasteful especially for objects with very few data attributes and the space consumption can become significant when creating large numbers of instances.

      This is the type of class you get by default both with and without ``attrs``.

   slotted classes
      A class that has no ``__dict__`` attribute and `defines <https://docs.python.org/3/reference/datamodel.html#slots>`_ its attributes in a ``__slots__`` attribute instead.
      In ``attrs``, they are created by passing ``slots=True`` to ``@attr.s``.

      Their main advantage is that they use less memory on CPython [#pypy]_.

      However they also come with a bunch of possibly surprising gotchas:

      - Slotted classes don't allow for any other attribute to be set except for those defined in one of the class' hierarchies ``__slots__``:

        .. doctest::

          >>> import attr
          >>> @attr.s(slots=True)
          ... class Coordinates(object):
          ...     x = attr.ib()
          ...     y = attr.ib()
          ...
          >>> c = Coordinates(x=1, y=2)
          >>> c.z = 3
          Traceback (most recent call last):
              ...
          AttributeError: 'Coordinates' object has no attribute 'z'

      - Slotted classes can inherit from other classes just like non-slotted classes, but some of the benefits of slotted classes are lost if you do that.
        If you must inherit from other classes, try to inherit only from other slotted classes.

      - Slotted classes must implement :meth:`__getstate__ <object.__getstate__>` and :meth:`__setstate__ <object.__setstate__>` to be serializable with `pickle` protocol 0 and 1.
        Therefore, ``attrs`` creates these methods automatically for ``slots=True`` classes (Python 2 uses protocol 0 by default).

        .. note::

            You can control this behavior with the ``getstate_setstate`` argument:

            - leaving it unset preserves the historical default (generated for slotted classes, not for regular classes),
            - ``getstate_setstate=False`` prevents generation entirely, so your own or an inherited pair of methods is used instead, and
            - ``getstate_setstate=True`` forces generation (the generated methods will *override* any methods you defined on the class).

            The generated methods serialize all ``attrs`` fields (never ``__weakref__`` or a cached hash), work for frozen classes, and reset cached hashes on deserialization.

        Also, `think twice <https://www.youtube.com/watch?v=7KnfGDajDQw>`_ before using `pickle`.

      - Slotted classes are weak-referenceable by default.
        This can be disabled in CPython by passing ``weakref_slot=False`` to ``@attr.s`` [#pypyweakref]_.

      - Since it's currently impossible to make a class slotted after it's created, ``attrs`` has to replace your class with a new one.
        While it tries to do that as graciously as possible, certain metaclass features like ``__init_subclass__`` do not work with slotted classes.


.. [#pypy] On PyPy, there is no memory advantage in using slotted classes.
.. [#pypyweakref] On PyPy, slotted classes are naturally weak-referenceable so ``weakref_slot=False`` has no effect.
