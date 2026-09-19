from typing import (
    Any,
    Callable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from attr import Factory as Factory
from attr import Attribute as Attribute

_T = TypeVar("_T")
_C = TypeVar("_C", bound=type)

_ValidatorType = Callable[[Any, Attribute[_T], _T], Any]
_ConverterType = Callable[[Any], _T]
_ReprType = Callable[[Any], str]
_ReprArgType = Union[bool, _ReprType]
_ValidatorArgType = Union[_ValidatorType[_T], Sequence[_ValidatorType[_T]]]


@overload
def field(
    *,
    default: None = ...,
    validator: None = ...,
    repr: _ReprArgType = ...,
    hash: Optional[bool] = ...,
    init: bool = ...,
    metadata: Optional[Mapping[Any, Any]] = ...,
    converter: None = ...,
    factory: None = ...,
    kw_only: bool = ...,
    eq: bool = ...,
    order: Optional[bool] = ...,
) -> Any: ...
@overload
def field(
    *,
    default: None = ...,
    validator: Optional[_ValidatorArgType[_T]] = ...,
    repr: _ReprArgType = ...,
    hash: Optional[bool] = ...,
    init: bool = ...,
    metadata: Optional[Mapping[Any, Any]] = ...,
    converter: Optional[_ConverterType[_T]] = ...,
    factory: Optional[Callable[[], _T]] = ...,
    kw_only: bool = ...,
    eq: bool = ...,
    order: Optional[bool] = ...,
) -> _T: ...
@overload
def field(
    *,
    default: _T,
    validator: Optional[_ValidatorArgType[_T]] = ...,
    repr: _ReprArgType = ...,
    hash: Optional[bool] = ...,
    init: bool = ...,
    metadata: Optional[Mapping[Any, Any]] = ...,
    converter: Optional[_ConverterType[_T]] = ...,
    factory: Optional[Callable[[], _T]] = ...,
    kw_only: bool = ...,
    eq: bool = ...,
    order: Optional[bool] = ...,
) -> _T: ...
@overload
def field(
    *,
    default: Optional[_T] = ...,
    validator: Optional[_ValidatorArgType[_T]] = ...,
    repr: _ReprArgType = ...,
    hash: Optional[bool] = ...,
    init: bool = ...,
    metadata: Optional[Mapping[Any, Any]] = ...,
    converter: Optional[_ConverterType[_T]] = ...,
    type: object = ...,
    factory: Optional[Callable[[], _T]] = ...,
    kw_only: bool = ...,
    eq: bool = ...,
    order: Optional[bool] = ...,
) -> Any: ...


# The Modern API mirrors attr.s but always collects PEP 526 annotations,
# detects manually implemented dunders and collects base attrs by MRO.
@overload
def define(
    maybe_cls: _C,
    these: Optional[Mapping[str, Any]] = ...,
    repr_ns: Optional[str] = ...,
    repr: _ReprArgType = ...,
    hash: Optional[bool] = ...,
    init: bool = ...,
    slots: bool = ...,
    frozen: bool = ...,
    weakref_slot: bool = ...,
    str: bool = ...,
    kw_only: bool = ...,
    cache_hash: bool = ...,
    auto_exc: bool = ...,
    eq: Optional[bool] = ...,
    order: Optional[bool] = ...,
    getstate_setstate: Optional[bool] = ...,
) -> _C: ...
@overload
def define(
    maybe_cls: None = ...,
    these: Optional[Mapping[str, Any]] = ...,
    repr_ns: Optional[str] = ...,
    repr: _ReprArgType = ...,
    hash: Optional[bool] = ...,
    init: bool = ...,
    slots: bool = ...,
    frozen: bool = ...,
    weakref_slot: bool = ...,
    str: bool = ...,
    kw_only: bool = ...,
    cache_hash: bool = ...,
    auto_exc: bool = ...,
    eq: Optional[bool] = ...,
    order: Optional[bool] = ...,
    getstate_setstate: Optional[bool] = ...,
) -> Callable[[_C], _C]: ...


# frozen and mutable are define with a couple of defaults flipped.
@overload
def frozen(
    maybe_cls: _C,
    these: Optional[Mapping[str, Any]] = ...,
    repr_ns: Optional[str] = ...,
    repr: _ReprArgType = ...,
    hash: Optional[bool] = ...,
    init: bool = ...,
    weakref_slot: bool = ...,
    str: bool = ...,
    kw_only: bool = ...,
    cache_hash: bool = ...,
    auto_exc: bool = ...,
    eq: Optional[bool] = ...,
    order: Optional[bool] = ...,
    getstate_setstate: Optional[bool] = ...,
) -> _C: ...
@overload
def frozen(
    maybe_cls: None = ...,
    these: Optional[Mapping[str, Any]] = ...,
    repr_ns: Optional[str] = ...,
    repr: _ReprArgType = ...,
    hash: Optional[bool] = ...,
    init: bool = ...,
    weakref_slot: bool = ...,
    str: bool = ...,
    kw_only: bool = ...,
    cache_hash: bool = ...,
    auto_exc: bool = ...,
    eq: Optional[bool] = ...,
    order: Optional[bool] = ...,
    getstate_setstate: Optional[bool] = ...,
) -> Callable[[_C], _C]: ...


mutable = define


def make_class(
    name: str,
    attrs: Union[List[str], Tuple[str, ...], Mapping[str, Any]],
    bases: Tuple[type, ...] = ...,
    **attributes_arguments: Any,
) -> type: ...
