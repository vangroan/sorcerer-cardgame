from dataclasses import asdict, dataclass
from typing import Any

from sorcerer.util import asdict_factory


@dataclass
class Move:
    move_id: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]

    def __init__(self, move_id: str, *args, **kwargs):
        self.move_id = move_id
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        args = ", ".join(map(str, self.args))
        kwargs = ", ".join(f"{name}={value}" for name, value in self.kwargs.items())
        sig = ", ".join(filter(bool, [args, kwargs]))
        return type(self).__qualname__ + f"({self.move_id}, {sig})"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self, dict_factory=asdict_factory)


print(Move("effect", effect_id="effect_power", monster_id="monster_demon", power=-4))
