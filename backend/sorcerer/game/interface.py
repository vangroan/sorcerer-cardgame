from __future__ import annotations

import logging
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


def effect(name: str, *args, **kwargs) -> EffectDef:
    return EffectDef(name, args, kwargs)


class TargetKind(Enum):
    """
    The kind of game entity that can be the target of spells.
    """

    MONSTER = "monster"
    """Player targeted a monster in the fight"""
    SPELL = "spell"
    """Player targeted a spell on a monster"""
    PLAYER = "player"
    """Player targeted another player, or themselves"""
    JUDGE = "judge"
    """Player targeted the judge"""


@dataclass(frozen=True)
class Target:
    """
    A target of a spell card can be a monster, a direct spell
    or enchantment on a monster, the judge, the palyer
    themselves, or other players.
    """

    kind: TargetKind
    target_id: int | str | None


@dataclass(frozen=True)
class EffectDef:
    name: str
    args: tuple
    kwargs: dict

    @property
    def args_kwargs(self) -> tuple[tuple, dict]:
        return self.args, self.kwargs
