from __future__ import annotations

from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict
from abc import ABC
from typing import Any

from sorcerer.util import asdict_factory


class Phase(Enum):
    """
    Discribes the state machine of the game's phases.
    """

    LOBBY = "lobby"  # Players joining
    SETUP = "setup"  # Server selecting judge and monsters
    BETTING = "betting"  # Players choosing monster to bet on

    def __str__(self) -> str:
        return self.value


class Card(ABC):
    card_id: str


@dataclass
class PlayerView:
    player_id: int
    card_count: int


@dataclass
class GameView:
    """
    A player's view of the game's state.

    This omits sensitive information.
    """

    player_id: int
    player_count: int
    game_phase: Phase
    created_at: datetime
    others: list[PlayerView] = field(default_factory=list)
    cards: list[Card] = field(default_factory=list)  # This player's cards
    join_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self, dict_factory=asdict_factory)


@dataclass
class PlayerSession:
    """
    Server side state for one player.

    This should be considered sensitive, and shouldn't be sent as-is to other palyers.
    """

    player_id: int
    money: int
    is_leader: bool = False
    cards: list[Card] = field(default_factory=list)

    @property
    def card_count(self) -> int:
        return len(self.cards)


@dataclass
class GameSession:
    """
    State object for a single game session.
    """

    join_key: str
    start_money: int = 2
    counter: int = 0
    player_counter: int = 0
    phase: Phase = Phase.LOBBY
    judge: Card | None = None
    players: list[PlayerSession] = field(default_factory=list)
    spells: list[Card] = field(default_factory=list)
    monsters: list[Card] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_lobby_phase(self) -> bool:
        return self.phase == Phase.LOBBY

    def create_new_player(self, is_leader=False) -> PlayerSession:
        player_id = self.player_counter
        self.player_counter += 1

        player = PlayerSession(
            player_id=player_id,
            money=self.start_money,
            is_leader=is_leader,
        )

        self.players.append(player)

        return player

    def begin_game(self):
        self.phase = Phase.SETUP

        # 1. Choose Judge

        # 2. Choose Monsters

        # 3. Deal Cards

        self.phase = Phase.BETTING

    def incr(self) -> int:
        self.counter += 1
        return self.counter

    def get_view(self, player_id: int) -> GameView:
        """
        Create a redacted view of the game state, which is safe to
        show to a player.

        The view is specifically constructed for the requesting player.
        It must omit sensitive information about the game, server and
        other players.

        Arguments:
            player_id: The player that this state view is intended for.
        """
        others = []
        cards = []

        for player in self.players:
            if player.player_id == player_id:
                # This is the requesting player
                cards = player.cards.copy()  # avoid shared state
            else:
                # Other player
                other_player = PlayerView(player.player_id, player.card_count)
                others.append(other_player)

        return GameView(
            player_id,
            player_count=len(self.players),
            game_phase=self.phase,
            others=others,
            cards=cards,
            created_at=self.created_at,
        )
