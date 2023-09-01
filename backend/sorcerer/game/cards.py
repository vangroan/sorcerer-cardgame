from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Literal
import itertools

from sorcerer.game.effects import Effect
from sorcerer.game import effects

SpellKind = Literal["direct", "enchant", "support"]


@dataclass(frozen=True)
class Card(ABC):
    card_id: int  # Uniquely identifies the card in a game session.
    spell_id: str = field(init=False)
    spell_kind: SpellKind = field(init=False)
    forbidden: bool = field(init=False)
    effects: tuple[Effect, ...] = field(init=False)
    owner: int | None = None


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
    effects: tuple[Effect, ...] = (effects.Power(power=5),)


class Frostbolt(Card):
    spell_id: str = "card_frostbolt"
    spell_kind: SpellKind = "direct"
    forbidden: bool = False
    effects: tuple[Effect, ...] = ()


class MagicMissile(Card):
    spell_id: str = "card_magicmissile"
    spell_kind: SpellKind = "direct"
    forbidden: bool = False
    effects: tuple[Effect, ...] = ()
