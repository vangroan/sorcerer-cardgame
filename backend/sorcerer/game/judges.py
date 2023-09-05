from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field

from sorcerer.game.interface import EffectDef, effect
from sorcerer.game.cards import SpellKind


@dataclass(frozen=True)
class Judge(ABC):
    judge_id: str = field(init=False)
    name: str = field(init=False)
    title: str = field(init=False)
    mana_limit: int = field(init=False)
    judgement: EffectDef | None = field(init=False, default=None)
    disallows: tuple[SpellKind, ...] = field(init=False)
    disallow_forbidden: bool = False


def get_judge_types() -> list[type[Judge]]:
    return [
        Moira,
    ]


@dataclass(frozen=True)
class Moira(Judge):
    judge_id: str = "judge_moira"
    name: str = "Moira"
    title: str = "The Devious"
    mana_limit: int = 12
    judgement: EffectDef = effect("Dispel")
    disallows: tuple[SpellKind, ...] = ("direct",)
