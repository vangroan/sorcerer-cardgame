from collections import namedtuple
from copy import copy
from enum import Enum
from datetime import datetime
from typing import Any, Callable, TypeVar, Generic


def asdict_factory(data: list[tuple[str, Any]]):
    """
    A custom ``dataclasses.asdict`` factory that can handle enums.
    """

    def convert_value(obj):
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    return dict((k, convert_value(v)) for k, v in data)


TClass = TypeVar("TClass", bound=type)
_FIELDS = "__datadef_fields__"
_IMMUTABLES = [bool, int, float, tuple]


def datadef() -> Callable[[TClass], TClass]:
    """
    Annotations without default values must be overwritten by derived classes.
    """

    def decorator(cls: TClass) -> TClass:
        annotations = cls.__annotations__
        var_lookup = set(vars(cls).keys())
        datadef_fields: dict[str, _DataDef_Field] = {}

        # We must determine the contract for derived classes.
        #
        # A type annotation on the base `datadef` that doesn't
        # have a default value must be defined in the derived class.
        for name, value in annotations.items():
            if name not in var_lookup:
                # No default attribute value supplied
                datadef_fields[name] = _DataDef_Field(name, ty=value)

        setattr(cls, _FIELDS, datadef_fields)

        # Setup magic methods
        setattr(cls, "__repr__", _make_repr(cls))

        _check_contract(cls)

        return cls

    return decorator


def _make_repr(cls: TClass) -> Callable[[TClass], str]:
    def _repr(self) -> str:
        args = ()
        kwargs = {}
        return f"{cls.__qualname__}({args}, {kwargs})"

    return _repr


_DataDef_Field = namedtuple("_DataDef_Field", ["name", "ty"])


def is_datadef(cls: type) -> bool:
    return hasattr(cls, _FIELDS)


def fields(cls: type) -> dict[str, _DataDef_Field]:
    if not is_datadef(cls):
        raise ValueError(f"Argument 'cls' must be a data definition")

    return copy(getattr(cls, _FIELDS)) or {}


def _check_contract(cls: type):
    assert is_datadef(cls)

    bases = [base for base in cls.__bases__ if is_datadef(base)]
    datadef_attrs = vars(cls)
    datadef_annotations = cls.__annotations__

    for base in bases:
        for name, datadef_field in fields(base).items():
            if name not in datadef_attrs:
                raise ValueError(f"Derived type '{cls.__qualname__}' must define an attribute '{name}'")

            # TODO: Check that types match (probably unfeasible because we would have to implement a whole typechecker)

            # if anno := datadef_annotations.get(name):
            #     print(f"{datadef_field.ty} is not {anno}")
            #     if datadef_field.ty is not anno:
            #         raise TypeError(f"Type annotation '{name}' on derived type '{cls.__qualname__}' must be type {repr(datadef_field.ty)}")


T = TypeVar("T")


class MyThing(Generic[T]):
    pass


@datadef()
class Base:
    thing_id: int
    effects: list[str]
    thing: MyThing[str] = MyThing()
    # owner: Any | None

    # def __init__(self, owner: Any | None = None):
    #     self.owner = owner


@datadef()
class Foobar(Base):
    thing_id: int = 1
    effects: list[str] = [
        "firebolt",
    ]

    def __str__(self) -> str:
        return "foobar"


print(str(Foobar()), ", ", repr(Foobar()))
print(f"{Foobar()} {Foobar()!r}")
