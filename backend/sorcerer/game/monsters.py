from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field

from sorcerer.game.cards import Card
from sorcerer.game.effects import Effect, Undead


@dataclass(frozen=True)
class Monster(ABC):
    """
    Monsters must not be shared between game sessions, because they
    hold the spells casts on them during their session.
    """

    monster_id: str = field(init=False)
    name: str = field(init=False)
    prize: int = field(init=False)
    power: int = field(init=False)
    effect: Effect | None = field(init=False)
    cards: list[Card] = field(default_factory=list)


def get_monster_types() -> list[type[Monster]]:
    return [
        DarkElf,
        Demon,
        Dragon,
        Ghost,
        Goblin,
        Lizardman,
        Minotaur,
        Orc,
        Skeleton,
        Succubus,
    ]


class DarkElf(Monster):
    monster_id: str = "monster_darkelf"
    name: str = "Dark Elf"
    prize: int = 4
    power: int = 7
    effect: Effect | None = None


class Demon(Monster):
    monster_id: str = "monster_demon"
    name: str = "Demon"
    prize: int = 3
    power: int = 9
    effect: Effect | None = None


class Dragon(Monster):
    monster_id: str = "monster_dragon"
    name: str = "Dragon"
    prize: int = 3
    power: int = 10
    effect: Effect | None = None


class Ghost(Monster):
    monster_id: str = "monster_ghost"
    name: str = "Ghost"
    prize: int = 5
    power: int = 5
    effect: Effect = Undead()


class Goblin(Monster):
    monster_id: str = "monster_goblin"
    name: str = "Goblin"
    prize: int = 10
    power: int = 1
    effect: Effect | None = None


class Lizardman(Monster):
    monster_id: str = "monster_lizardman"
    name: str = "Lizardman"
    prize: int = 6
    power: int = 4
    effect: Effect | None = None


class Minotaur(Monster):
    monster_id: str = "monster_minotaur"
    name: str = "Minotaur"
    prize: int = 4
    power: int = 8
    effect: Effect | None = None


class Orc(Monster):
    monster_id: str = "monster_orc"
    name: str = "Orc"
    prize: int = 8
    power: int = 2
    effect: Effect | None = None


class Skeleton(Monster):
    monster_id: str = "monster_skeleton"
    name: str = "Skeleton"
    prize: int = 7
    power: int = 3
    effect: Effect = Undead()


class Succubus(Monster):
    monster_id: str = "monster_succubus"
    name: str = "Succubus"
    prize: int = 5
    power: int = 6
    effect: Effect | None = None
