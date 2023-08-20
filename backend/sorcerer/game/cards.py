from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Card(ABC):
    card_id: str = field(init=False)
    owner: int | None = None


class Firebolt(Card):
    card_id: str = "card_firebolt"
