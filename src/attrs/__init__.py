"""
The Modern API of ``attrs`` (:pep:`526` annotations only).

It is a small, opinionated layer on top of `attr.s`/`attr.ib`.

.. versionadded:: 20.1.0
"""

from __future__ import absolute_import, division, print_function

from attr import Factory
from attr import attrib as _attrib
from attr._make import NOTHING, attrs as _attrs, make_class as _make_class


__all__ = ["define", "frozen", "mutable", "field", "Factory", "make_class"]


# Shared defaults of the Modern API: PEP 526 annotations are collected
# automatically, the base classes' attribute collection is done correctly via
# the MRO, manually implemented dunder methods are detected, and classes are
# made weak-referenceable.
_MODERN_DEFAULTS = dict(
    auto_attribs=True,
    auto_detect=True,
    collect_by_mro=True,
    weakref_slot=True,
    getstate_setstate=None,
)


def field(
    default=NOTHING,
    validator=None,
    repr=True,
    hash=None,
    init=True,
    metadata=None,
    converter=None,
    factory=None,
    kw_only=False,
    eq=True,
    order=None,
):
    """
    Create a new attribute on a class that is handled by `attrs.define`,
    `attrs.frozen`, or `attrs.mutable`.

    Equivalent to `attr.ib` with modern defaults (``eq=True``); the
    containing class must use PEP 526 type annotations.
    """
    return _attrib(
        default=default,
        validator=validator,
        repr=repr,
        hash=hash,
        init=init,
        metadata=metadata,
        converter=converter,
        factory=factory,
        kw_only=kw_only,
        eq=eq,
        order=order,
    )


def define(
    maybe_cls=None,
    these=None,
    repr_ns=None,
    repr=None,
    hash=None,
    init=None,
    slots=False,
    frozen=False,
    weakref_slot=True,
    str=False,
    kw_only=False,
    cache_hash=False,
    auto_exc=False,
    eq=None,
    order=None,
    getstate_setstate=None,
):
    r"""
    Define an ``attrs`` class using the Modern API.

    Identical to `attr.s`, but with opinionated defaults:

    - PEP 526 annotations are collected automatically
      (``auto_attribs=True``), so no `attr.ib` calls are needed; use
      `attrs.field` to configure an attribute.
    - Dunder methods (``__init__``, ``__repr__``, ``__eq__`` ...) that you
      implement yourself are detected and not overwritten
      (``auto_detect=True``).
    - Attributes are collected from base classes in correct MRO order
      (``collect_by_mro=True``).
    - Slotted classes are weak-referenceable by default
      (``weakref_slot=True``).
    - *getstate_setstate* defaults to ``None``: slotted classes get
      ``__getstate__``/``__setstate__`` (your own versions win thanks to
      auto-detection), regular classes rely on the default pickle protocol.
      Pass ``True`` to generate them for every class or ``False`` to opt out
      completely.

    Can be used as a bare decorator (``@attrs.define``) or with arguments
    (``@attrs.define(...)``).
    """
    kwargs = dict(_MODERN_DEFAULTS)
    kwargs.update(
        dict(
            these=these,
            repr_ns=repr_ns,
            repr=repr,
            hash=hash,
            init=init,
            slots=slots,
            frozen=frozen,
            weakref_slot=weakref_slot,
            str=str,
            kw_only=kw_only,
            cache_hash=cache_hash,
            auto_exc=auto_exc,
            eq=eq,
            order=order,
            getstate_setstate=getstate_setstate,
        )
    )
    return _attrs(maybe_cls, **kwargs)


def frozen(
    maybe_cls=None,
    these=None,
    repr_ns=None,
    repr=None,
    hash=None,
    init=None,
    weakref_slot=True,
    str=False,
    kw_only=False,
    cache_hash=False,
    auto_exc=False,
    eq=None,
    order=None,
    getstate_setstate=None,
):
    """
    A convenience shortcut for `attrs.define` with ``frozen=True`` and
    ``slots=True``.

    The resulting classes are immutable (in the same sense as
    ``frozen=True`` for `attr.s`) and memory-efficient, and therefore also
    hashable by default.
    """
    return define(
        maybe_cls=maybe_cls,
        these=these,
        repr_ns=repr_ns,
        repr=repr,
        hash=hash,
        init=init,
        slots=True,
        frozen=True,
        weakref_slot=weakref_slot,
        str=str,
        kw_only=kw_only,
        cache_hash=cache_hash,
        auto_exc=auto_exc,
        eq=eq,
        order=order,
        getstate_setstate=getstate_setstate,
    )


mutable = define
"""
An alias for `define`, useful to make the contrast with `frozen` explicit.
"""


def make_class(name, attrs, bases=(object,), **attributes_arguments):
    """
    A quick way to create a new class with *attrs* using the Modern API.

    Behaves like `attr.make_class`, but with the opinionated defaults of
    `attrs.define`.
    """
    for key, value in _MODERN_DEFAULTS.items():
        attributes_arguments.setdefault(key, value)
    return _make_class(name, attrs, bases, **attributes_arguments)
