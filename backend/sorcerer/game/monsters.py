from abc import ABC
from dataclasses import dataclass, field

from sorcerer.game.cards import Card


@dataclass(frozen=True)
class Monster(ABC):
    monster_id: str = field(init=False)
    prize: int = field(init=False)
    power: int = field(init=False)
    cards: list[Card] = field(default_factory=list)


def get_monster_types() -> list[type[Monster]]:
    return [
        Demon,
        Dragon,
    ]


class Demon(Monster):
    monster_id: str = "monster_demon"
    prize: int = 5
    power: int = 7


class Dragon(Monster):
    monster_id: str = "monster_dragon"
    prize: int = 3
    power: int = 10
