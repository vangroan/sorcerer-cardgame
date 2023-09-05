from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass, field
from typing import Literal
import itertools

from sorcerer.game.interface import EffectDef, TargetKind, effect

logger = logging.getLogger(__name__)

SpellKind = Literal["direct", "enchant", "support"]


@dataclass(frozen=True)
class Card(ABC):
    card_id: int  # Uniquely identifies the card in a game session.
    spell_id: str = field(init=False)
    spell_kind: SpellKind = field(init=False)
    forbidden: bool = field(init=False)
    effect_defs: tuple[EffectDef, ...] = field(init=False)
    owner: int | None = None
    target: TargetKind = field(init=False)


@dataclass(frozen=False)
class CardHolder(ABC):
    """
    A card holder is any entity in the game that can be targeted
    by spell cards, and persist them.
    """

    cards: list[Card] = field(init=False)


def get_standard_deck() -> list[Card]:
    deck: list[Card] = []

    count = itertools.count(start=0)

    # -------------------------------------------------------------------------
    # Direct Spells
    deck.extend(Firebolt(next(count)) for _ in range(5))
    deck.extend(Frostbolt(next(count)) for _ in range(5))
    deck.extend(MagicMissile(next(count)) for _ in range(5))

    return deck


# -----------------------------------------------------------------------------
# Direct Spells


@dataclass(frozen=True)
class Firebolt(Card):
    spell_id: str = "card_firebolt"
    spell_kind: SpellKind = "direct"
    forbidden: bool = False
    effect_defs: tuple[EffectDef, ...] = (effect("Power", power=-5),)
    target: TargetKind = TargetKind.MONSTER


@dataclass(frozen=True)
class Frostbolt(Card):
    spell_id: str = "card_frostbolt"
    spell_kind: SpellKind = "direct"
    forbidden: bool = False
    effect_defs: tuple[EffectDef, ...] = (effect("Power", power=-4),)
    target: TargetKind = TargetKind.MONSTER


@dataclass(frozen=True)
class MagicMissile(Card):
    spell_id: str = "card_magicmissile"
    spell_kind: SpellKind = "direct"
    forbidden: bool = False
    effect_defs: tuple[EffectDef, ...] = (effect("Power", power=-4),)
    target: TargetKind = TargetKind.MONSTER
