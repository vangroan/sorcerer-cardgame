from __future__ import annotations

from enum import Enum
from abc import ABC
from dataclasses import dataclass, field
from typing import Literal


SpellKind = Literal["direct", "enchant", "support"]


@dataclass(frozen=True)
class Card(ABC):
    card_id: str = field(init=False)
    spell_kind: SpellKind = field(init=False)
    forbidden: bool = field(init=False)
    owner: int | None = None


class Firebolt(Card):
    card_id: str = "card_firebolt"
    spell_kind: SpellKind = "direct"
    forbidden: bool = False
