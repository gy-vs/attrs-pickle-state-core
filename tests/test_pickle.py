"""
Tests for the generation of ``__getstate__`` / ``__setstate__`` through the
``getstate_setstate`` option, and for pickling/copying behavior in general.
"""

from __future__ import absolute_import, division, print_function

import copy
import pickle
import weakref

import pytest

import attr

from attr._compat import PY2


ALL_PROTOCOLS = list(range(pickle.HIGHEST_PROTOCOL + 1))


def assert_pickle_roundtrip(instance, protocols=ALL_PROTOCOLS):
    """
    Pickle and unpickle *instance* with every of *protocols* and assert that
    the copy is equal but not identical.
    """
    for protocol in protocols:
        clone = pickle.loads(pickle.dumps(instance, protocol))
        assert clone == instance
        assert clone is not instance


# ---------------------------------------------------------------------------
# Module-level classes (classes local to a test can't be pickled by name).
# ---------------------------------------------------------------------------


@attr.s(slots=True)
class SlotsDefault(object):
    x = attr.ib()
    y = attr.ib()


@attr.s
class DictDefault(object):
    x = attr.ib()
    y = attr.ib()


@attr.s(getstate_setstate=True)
class DictForced(object):
    x = attr.ib()
    y = attr.ib()


@attr.s(slots=True, getstate_setstate=True)
class SlotsForced(object):
    x = attr.ib()
    y = attr.ib()


@attr.s(slots=True, getstate_setstate=False)
class SlotsOff(object):
    x = attr.ib()


@attr.s(getstate_setstate=False)
class DictOff(object):
    x = attr.ib()


@attr.s(slots=True, frozen=True)
class FrozenSlotsDefault(object):
    x = attr.ib()


@attr.s(frozen=True, getstate_setstate=True)
class FrozenDictForced(object):
    x = attr.ib()


@attr.s(slots=True, frozen=True, getstate_setstate=False)
class FrozenSlotsOff(object):
    x = attr.ib()


@attr.s(slots=True, frozen=True, cache_hash=True)
class CachedHashSlots(object):
    x = attr.ib()


@attr.s(frozen=True, cache_hash=True, getstate_setstate=True)
class CachedHashDict(object):
    x = attr.ib()


@attr.s(slots=True, weakref_slot=True)
class WeakrefSlots(object):
    x = attr.ib()


@attr.s(slots=True, weakref_slot=False)
class NoWeakrefSlots(object):
    x = attr.ib()


# Inheritance chains: each level adds one field, options vary.
@attr.s(slots=True)
class LevelA(object):
    a = attr.ib()


@attr.s(slots=True)
class LevelB(LevelA):
    b = attr.ib()


@attr.s(slots=True)
class LevelC(LevelB):
    c = attr.ib()


@attr.s(slots=True, getstate_setstate=False)
class ParentOff(object):
    a = attr.ib()


@attr.s(slots=True, getstate_setstate=True)
class ParentOffChildOn(ParentOff):
    b = attr.ib()


@attr.s(slots=True, getstate_setstate=True)
class ParentOn(object):
    a = attr.ib()


@attr.s(slots=True)
class ParentOnChildDefault(ParentOn):
    b = attr.ib()


@attr.s(getstate_setstate=False)
class DictParentOff(object):
    a = attr.ib()


@attr.s(slots=True, getstate_setstate=True)
class DictParentOffSlotsChild(DictParentOff):
    b = attr.ib()


@attr.s(slots=True)
class SlotsParentDefault(object):
    a = attr.ib()


@attr.s(getstate_setstate=True)
class SlotsParentDefaultDictChild(SlotsParentDefault):
    b = attr.ib()


@attr.s(slots=True, getstate_setstate=True)
class AltA(object):
    a = attr.ib()


@attr.s(slots=True, getstate_setstate=False)
class AltB(AltA):
    b = attr.ib()


@attr.s(slots=True, getstate_setstate=True)
class AltC(AltB):
    c = attr.ib()


@attr.s(slots=True)
class OverrideBase(object):
    a = attr.ib()
    n = attr.ib(default=0)


@attr.s(slots=True)
class OverrideChild(OverrideBase):
    n = attr.ib(default=1)


@attr.s(slots=True, getstate_setstate=False)
class InheritedOffChild(SlotsDefault):
    z = attr.ib()


class PlainStateBase(object):
    def __getstate__(self):
        return {"plain": True}

    def __setstate__(self, state):
        assert state == {"plain": True}
        object.__setattr__(self, "restored", True)


@attr.s(slots=True, getstate_setstate=False)
class PlainStateChild(PlainStateBase):
    x = attr.ib()


@attr.s(slots=True)
class CoopBase(object):
    a = attr.ib()


@attr.s(slots=True, getstate_setstate=False)
class CoopChild(CoopBase):
    b = attr.ib()

    def __getstate__(self):
        state = super(CoopChild, self).__getstate__()
        state["b"] = self.b
        return state

    def __setstate__(self, state):
        super(CoopChild, self).__setstate__(
            {name: state[name] for name in ("a",)}
        )
        object.__setattr__(self, "b", state["b"])


class TestGenerationSwitch(object):
    """
    Whether the dunders end up in the class dictionary is determined solely
    by the (resolved) option value -- not by pickling accidentally working.
    """

    def test_slots_default_generates(self):
        assert "__getstate__" in SlotsDefault.__dict__
        assert "__setstate__" in SlotsDefault.__dict__

    def test_dict_default_does_not_generate(self):
        assert "__getstate__" not in DictDefault.__dict__
        assert "__setstate__" not in DictDefault.__dict__

    def test_explicit_true_forces_for_dict_classes(self):
        assert "__getstate__" in DictForced.__dict__
        assert "__setstate__" in DictForced.__dict__

    def test_explicit_true_forces_for_slots(self):
        assert "__getstate__" in SlotsForced.__dict__
        assert "__setstate__" in SlotsForced.__dict__

    def test_explicit_false_skips_slots(self):
        assert "__getstate__" not in SlotsOff.__dict__
        assert "__setstate__" not in SlotsOff.__dict__

    def test_explicit_false_skips_dict(self):
        assert "__getstate__" not in DictOff.__dict__
        assert "__setstate__" not in DictOff.__dict__

    def test_explicit_true_overwrites_user_methods(self):
        """
        True means "generate", period -- even if the user defined methods.
        """

        @attr.s(slots=True, getstate_setstate=True)
        class C(object):
            x = attr.ib()

            def __getstate__(self):
                return "nope"

            def __setstate__(self, state):
                pass

        assert C(1).__getstate__() == {"x": 1}
        # The generated function keeps its "Automatically created" marker.
        assert "Automatically created by attrs." in C.__dict__[
            "__getstate__"
        ].__doc__

    def test_generated_methods_are_distinct_per_class(self):
        """
        Methods are freshly generated and attached, never shared.
        """
        assert SlotsDefault.__dict__["__getstate__"] is not (
            SlotsForced.__dict__["__getstate__"]
        )


class TestFalseDefers(object):
    """
    When generation is disabled, user-defined and inherited protocols take
    over completely.
    """

    def test_inherited_methods_take_over(self):
        # The child did not add its own methods and keeps exactly the
        # parent's.
        assert "__getstate__" not in InheritedOffChild.__dict__
        assert "__setstate__" not in InheritedOffChild.__dict__
        assert InheritedOffChild.__getstate__ is SlotsDefault.__dict__[
            "__getstate__"
        ]
        assert InheritedOffChild.__setstate__ is SlotsDefault.__dict__[
            "__setstate__"
        ]

    def test_plain_base_class_protocol_takes_over(self):
        instance = PlainStateChild(1)
        clone = pickle.loads(
            pickle.dumps(instance, pickle.HIGHEST_PROTOCOL)
        )
        assert clone.restored is True

    def test_user_methods_are_kept(self):
        """
        Methods defined directly on the class survive untouched.
        """

        @attr.s(slots=True, getstate_setstate=False)
        class C(object):
            x = attr.ib()

            def __getstate__(self):
                return ("user-state", self.x)

            def __setstate__(self, state):
                tag, x = state
                assert tag == "user-state"
                object.__setattr__(self, "x", x)

        assert C.__dict__["__getstate__"](C(42)) == ("user-state", 42)


class TestAutoDetect(object):
    def test_user_getstate_disables_generation(self):
        @attr.s(slots=True, auto_detect=True)
        class C(object):
            x = attr.ib()

            def __getstate__(self):
                return ("x", self.x)

            def __setstate__(self, state):
                object.__setattr__(self, "x", state[1])

        assert C(1).__getstate__() == ("x", 1)

    def test_user_setstate_disables_generation(self):
        @attr.s(slots=True, auto_detect=True)
        class C(object):
            x = attr.ib()

            def __setstate__(self, state):
                object.__setattr__(self, "x", state[1] + 1)

        assert "__setstate__" in C.__dict__
        assert "__getstate__" not in C.__dict__

    def test_inherited_methods_are_not_own(self):
        """
        Methods inherited from a base class must not count as "own".
        """

        @attr.s(slots=True, auto_detect=True)
        class Base(object):
            a = attr.ib()

        @attr.s(slots=True, auto_detect=True)
        class Child(Base):
            b = attr.ib()

        assert "__getstate__" in Child.__dict__


class TestGeneratedContent(object):
    @pytest.mark.parametrize("slots", [True, False])
    def test_state_covers_all_fields(self, slots):
        @attr.s(slots=slots, getstate_setstate=True)
        class C(object):
            x = attr.ib()
            y = attr.ib()

        assert C(1, 2).__getstate__() == {"x": 1, "y": 2}

    def test_state_is_field_mapping_not_instance_dict(self):
        """
        Non-field instance attributes are not part of the state.
        """
        instance = DictForced(1, 2)
        instance.other = 3
        assert instance.__getstate__() == {"x": 1, "y": 2}

    def test_weakref_never_part_of_state(self):
        instance = WeakrefSlots(1)
        weakref.ref(instance)  # would fail without the __weakref__ slot
        assert "__weakref__" not in instance.__getstate__()
        assert instance.__getstate__() == {"x": 1}

    def test_no_weakref_slot_state_unaffected(self):
        assert NoWeakrefSlots(3).__getstate__() == {"x": 3}

    def test_setstate_tolerates_missing_fields(self):
        """
        States from older versions or partial states must not crash restore;
        present fields are still restored, missing ones left unset.
        """
        instance = SlotsDefault.__new__(SlotsDefault)
        instance.__setstate__({"x": 7})
        assert instance.x == 7
        assert not hasattr(instance, "y")

    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS)
    def test_pickle_all_protocols_slots(self, protocol):
        assert_pickle_roundtrip(SlotsDefault(1, "two"), [protocol])

    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS)
    def test_pickle_all_protocols_dict_forced(self, protocol):
        assert_pickle_roundtrip(DictForced(1, "two"), [protocol])

    def test_copy_and_deepcopy_slots(self):
        instance = SlotsDefault([1, 2], 2)
        shallow = copy.copy(instance)
        deep = copy.deepcopy(instance)

        assert shallow == instance and shallow is not instance
        assert shallow.x is instance.x
        assert deep == instance and deep is not instance
        assert deep.x is not instance.x


class TestFrozen(object):
    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS)
    def test_frozen_slots_roundtrip(self, protocol):
        assert_pickle_roundtrip(FrozenSlotsDefault(42), [protocol])

    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS)
    def test_frozen_dict_forced_roundtrip(self, protocol):
        assert_pickle_roundtrip(FrozenDictForced(42), [protocol])

    def test_frozen_slots_without_methods_fail_to_unpickle(self):
        """
        Demonstrates why frozen slotted classes need the generated methods:
        without __setstate__, pickle restores through the frozen
        __setattr__ and fails.
        """
        if PY2:
            expected_errors = (TypeError,)
        else:
            expected_errors = (attr.exceptions.FrozenInstanceError, TypeError)
        with pytest.raises(expected_errors):
            pickle.loads(
                pickle.dumps(FrozenSlotsOff(1), pickle.HIGHEST_PROTOCOL)
            )

    def test_restore_does_not_use_normal_setattr(self):
        clone = pickle.loads(
            pickle.dumps(FrozenSlotsDefault(1), pickle.HIGHEST_PROTOCOL)
        )
        assert clone.x == 1
        with pytest.raises(attr.exceptions.FrozenInstanceError):
            clone.x = 2


class TestCacheHash(object):
    def test_slots_cache_is_reset(self):
        instance = CachedHashSlots(1)
        first_hash = hash(instance)
        assert instance._attrs_cached_hash == first_hash

        clone = pickle.loads(
            pickle.dumps(instance, pickle.HIGHEST_PROTOCOL)
        )
        # The old cache value is never serialized or restored.
        assert clone._attrs_cached_hash is None
        assert hash(clone) == first_hash
        assert clone._attrs_cached_hash == first_hash

    def test_dict_cache_is_reset(self):
        instance = CachedHashDict(1)
        first_hash = hash(instance)
        assert instance._attrs_cached_hash == first_hash

        clone = pickle.loads(
            pickle.dumps(instance, pickle.HIGHEST_PROTOCOL)
        )
        assert clone._attrs_cached_hash is None
        assert hash(clone) == first_hash

    def test_cache_absent_from_state(self):
        instance = CachedHashSlots(1)
        hash(instance)
        assert "_attrs_cached_hash" not in instance.__getstate__()

    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS)
    def test_cached_hash_roundtrip_all_protocols(self, protocol):
        instance = CachedHashSlots(8)
        before = hash(instance)
        clone = pickle.loads(pickle.dumps(instance, protocol))
        assert hash(clone) == before


class TestInheritance(object):
    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS)
    def test_plain_slot_inheritance(self, protocol):
        instance = LevelC(1, 2, 3)
        clone = pickle.loads(pickle.dumps(instance, protocol))
        assert (clone.a, clone.b, clone.c) == (1, 2, 3)
        # Each level's state covers exactly its full field set -- inherited
        # fields are never duplicated.
        assert LevelA(1).__getstate__() == {"a": 1}
        assert LevelB(1, 2).__getstate__() == {"a": 1, "b": 2}
        assert instance.__getstate__() == {"a": 1, "b": 2, "c": 3}

    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS)
    def test_parent_false_child_true(self, protocol):
        clone = pickle.loads(
            pickle.dumps(ParentOffChildOn(1, 2), protocol)
        )
        assert (clone.a, clone.b) == (1, 2)
        assert ParentOffChildOn(1, 2).__getstate__() == {
            "a": 1,
            "b": 2,
        }

    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS)
    def test_parent_true_child_default_slots(self, protocol):
        clone = pickle.loads(
            pickle.dumps(ParentOnChildDefault(3, 4), protocol)
        )
        assert (clone.a, clone.b) == (3, 4)

    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS)
    def test_dict_parent_slots_child(self, protocol):
        clone = pickle.loads(
            pickle.dumps(DictParentOffSlotsChild(5, 6), protocol)
        )
        assert (clone.a, clone.b) == (5, 6)

    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS)
    def test_slots_parent_dict_child(self, protocol):
        clone = pickle.loads(
            pickle.dumps(SlotsParentDefaultDictChild(7, 8), protocol)
        )
        assert (clone.a, clone.b) == (7, 8)

    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS)
    def test_alternating_three_levels(self, protocol):
        instance = AltC(9, 10, 11)
        assert instance.__getstate__() == {"a": 9, "b": 10, "c": 11}
        clone = pickle.loads(pickle.dumps(instance, protocol))
        assert (clone.a, clone.b, clone.c) == (9, 10, 11)

    def test_overridden_field_not_duplicated(self):
        instance = OverrideChild(a=1, n=2)
        state = instance.__getstate__()
        assert list(state).count("n") == 1
        assert state == {"a": 1, "n": 2}

    @pytest.mark.parametrize("protocol", ALL_PROTOCOLS)
    def test_cooperative_user_state_methods(self, protocol):
        """
        Users can opt out and implement cooperative state methods
        themselves, including fields added by a slotted child.
        """
        clone = pickle.loads(pickle.dumps(CoopChild(1, 2), protocol))
        assert (clone.a, clone.b) == (1, 2)


class TestMakeClass(object):
    def test_make_class_passes_option_false(self):
        C = attr.make_class(
            "MakeClassOff", ["x"], slots=True, getstate_setstate=False
        )
        assert "__getstate__" not in C.__dict__

    def test_make_class_passes_option_true(self):
        C = attr.make_class(
            "MakeClassOn", ["x"], getstate_setstate=True
        )
        assert "__getstate__" in C.__dict__
        assert "__setstate__" in C.__dict__
        assert C(1).__getstate__() == {"x": 1}

        instance = C.__new__(C)
        instance.__setstate__({"x": 9})
        assert instance.x == 9


try:
    from attr import define, field, frozen, mutable
except ImportError:  # pragma: no cover
    define = None


@attr.define
class NextGenPoint(object):
    x = attr.field()
    y = attr.field(default=2)


@attr.frozen
class NextGenFrozen(object):
    x = attr.field()


@pytest.mark.skipif(PY2, reason="next-gen API is Python 3 only.")
class TestNextGen(object):
    def test_define_generates_by_default(self):
        assert "__getstate__" in NextGenPoint.__dict__
        assert "__setstate__" in NextGenPoint.__dict__
        assert "__slots__" in NextGenPoint.__dict__
        assert_pickle_roundtrip(NextGenPoint(1))

    def test_define_explicit_false(self):
        @define(getstate_setstate=False)
        class LocalOff(object):
            x: int = field()

        assert "__getstate__" not in LocalOff.__dict__

    def test_define_auto_attribs_guessing(self):
        @define
        class Guessing(object):
            x = field()

        assert Guessing(1).x == 1

    def test_frozen_define(self):
        assert "__getstate__" in NextGenFrozen.__dict__
        assert_pickle_roundtrip(NextGenFrozen(3))

    def test_mutable_define(self):
        @mutable(getstate_setstate=True)
        class Mut(object):
            x: int = field()

        assert "__getstate__" in Mut.__dict__
