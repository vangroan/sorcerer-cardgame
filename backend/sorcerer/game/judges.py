from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field

from sorcerer.game.effects import Dispel, Eject, Effect
from sorcerer.game.cards import SpellKind


@dataclass(frozen=True)
class DisallowSpell:
    spell_kind: SpellKind | None  # Optionally the kind of spells to disallow.
    forbidden: bool = field(kw_only=True, default=False)  # True when Forbidden spells are disallowed.


@dataclass(frozen=True)
class Judge(ABC):
    judge_id: str = field(init=False)
    name: str = field(init=False)
    title: str = field(init=False)
    mana_limit: int = field(init=False)
    judgement: Effect | None = field(init=False, default=None)
    disallows: list[SpellKind] = field(init=False)
    disallow_forbidden: bool = False


def get_judge_types() -> list[type[Judge]]:
    return [
        Moira,
    ]


class Moira(Judge):
    judge_id: str = "judge_moira"
    name: str = "Moira"
    title: str = "The Devious"
    mana_limit: int = 12
    judgement: Effect = Dispel()
    disallows: list[SpellKind] = ["direct"]
