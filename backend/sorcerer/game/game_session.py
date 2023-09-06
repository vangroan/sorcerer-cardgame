from __future__ import annotations

import logging
import random
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Any

from sorcerer.game.errors import GameError
from sorcerer.game.judges import Judge, get_judge_types
from sorcerer.game.monsters import Monster, get_monster_types
from sorcerer.game.cards import Card, get_standard_deck
from sorcerer.game.interface import Target, TargetKind
from sorcerer.game.moves import Move
from sorcerer.util import asdict_factory

logger = logging.getLogger(__name__)


MONSTER_BET_COUNT = {1, 2, 3}
"""Players can only bet on 1, 2 or 3 monsters during a round."""

MAX_ROUNDS = 3
"""Maximum number of fight rounds."""


class Phase(Enum):
    """
    Discribes the state machine of the game's phases.
    """

    LOBBY = "lobby"  # Players joining
    SETUP = "setup"  # Server selecting judge and monsters
    BETTING = "betting"  # Players choosing monster to bet on
    FIGHT = "fight"  # Players can play spells

    def __str__(self) -> str:
        return self.value


@dataclass
class PlayerView:
    player_id: int
    card_count: int
    bet_count: int


@dataclass
class GameView:
    """
    A player's view of the game's state.

    This omits sensitive information.
    """

    player_id: int
    player_count: int
    game_phase: Phase
    game_round: int
    game_turn: int
    deck_count: int
    discard_count: int
    created_at: datetime
    judge: Judge | None = None
    others: list[PlayerView] = field(default_factory=list)
    monsters: list[Monster] = field(default_factory=list)
    cards: list[Card] = field(default_factory=list)  # This player's cards
    monster_bets: list[str] = field(default_factory=list)
    join_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self, dict_factory=asdict_factory)


@dataclass(frozen=True)
class DiscardView:
    """
    State view containing all discarded spells, monsters and judges.
    """

    spells: list[Card] = field(default_factory=list)
    monsters: list[Monster] = field(default_factory=list)
    judges: list[Judge] = field(default_factory=list)


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
    monster_bets: list[str] = field(default_factory=list)

    @property
    def card_count(self) -> int:
        return len(self.cards)

    @property
    def bet_count(self) -> int:
        return len(self.monster_bets)


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
    round: int = -1
    turn: int = -1
    judge: Judge | None = None
    discarded_judges: list[Monster] = field(default_factory=list)
    players: list[PlayerSession] = field(default_factory=list)
    spells: list[Card] = field(default_factory=list)
    discarded_spells: list[Card] = field(default_factory=list)
    monsters: list[Monster] = field(default_factory=list)
    discarded_monsters: list[Monster] = field(default_factory=list)
    moves: list[Move] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_lobby_phase(self) -> bool:
        return self.phase == Phase.LOBBY

    @property
    def is_betting_phase(self) -> bool:
        return self.phase == Phase.BETTING

    @property
    def is_fight_phase(self) -> bool:
        return self.phase == Phase.FIGHT

    @property
    def player_count(self) -> int:
        """
        Number of players that joined the game.
        """
        return len(self.players)

    def find_player(self, player_id: int) -> PlayerSession | None:
        """
        Find a player in the game session with the given player ID.

        Returns ``None`` if the player cannot be found.
        """
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def first_player(self) -> PlayerSession | None:
        """
        Determine the player that goes first.
        """
        if self.players:
            return random.choice(self.players)
        return None

    def create_new_player(self, is_leader=False) -> PlayerSession:
        """
        Create a new player session inside this game session.

        The returned instance is shared state.
        """
        player_id = self.player_counter
        self.player_counter += 1

        player = PlayerSession(
            player_id=player_id,
            money=self.start_money,
            is_leader=is_leader,
        )

        self.players.append(player)

        return player

    def find_player_card(self, player_id: int, card_id: int) -> Card | None:
        """
        Find a card in a player's hand.
        """
        player = self.find_player(player_id)
        if player is None:
            raise GameError(f"Player does not exist: {player_id}")

        for card in player.cards:
            if card.card_id == card_id:
                return card

        return None

    def find_monster(self, monster_id: str) -> Monster | None:
        """
        Find a monster in the game session with the given monster ID.

        Returns ``None`` if the monster cannot be found.
        """
        for monster in self.monsters:
            if monster.monster_id == monster_id:
                return monster
        return None

    def choose_monsters(self, count: int = 5) -> list[Monster]:
        monsters = get_monster_types()
        chosen = []

        for _ in range(count):
            if not monsters:
                break

            monster_type = random.choice(monsters)

            # Ensure the same monster is not chosen multiple times
            monsters.remove(monster_type)

            chosen.append(monster_type())

        return chosen

    def shuffle_spells(self):
        """Shuffle the deck of card spells."""
        random.shuffle(self.spells)

    def try_draw_spell(self) -> Card | None:
        """
        Draw a spell from the top of the deck.

        Returns ``None`` when the spell deck is empty.
        """
        if self.spells:
            return self.spells.pop()
        return None

    def determine_hand_size(self) -> int:
        """
        Game rule for the number of cards dealt to each player.
        """
        if self.player_count <= 4:
            return 8
        elif self.player_count <= 5:
            return 6
        else:
            return 5

    def all_players_bet(self) -> bool:
        """
        Check whether all players have placed their bets.
        """
        return all(player.bet_count > 0 for player in self.players)

    def deal_cards(self, hand_size: int):
        """
        Fill each player's hand with spells from the deck, until their hand size
        reaches the given limit.

        If the spell deck is empty, dealing will stop.

        This algorithm mimics how dealing works at a table, drawing one card for each
        player in turn.
        """
        # Shallow copy the player container, because we
        # will be mutating it during iteration.
        players = self.players.copy()
        index = 0

        while players:
            if not self.spells:
                logger.debug("Game %s spell deck is empty", id(self))
                break

            player = players[index]

            if player.card_count < hand_size:
                spell_card = self.try_draw_spell()
                if spell_card:
                    player.cards.append(spell_card)
                index += 1
            else:
                # Don't increment the index.
                #
                # Because the current player was removed,
                # the next player moved up to the current index.
                players.remove(player)

            # List length will be zero when the last player is removed.
            if players:
                index = index % len(players)

    def begin_game(self):
        self.phase = Phase.SETUP
        logger.debug("Game %s beginning", id(self))

        # 1: Choose Judge
        judge_type = random.choice(get_judge_types())
        logger.debug("Game %s chose judge: %s", id(self), judge_type.__name__)
        self.judge = judge_type()

        # 2: Choose Monsters
        self.monsters = self.choose_monsters()

        # 3: Fill Spell Deck
        self.spells = get_standard_deck()
        self.shuffle_spells()

        # 4. Deal Cards
        hand_size = self.determine_hand_size()
        self.deal_cards(hand_size)

        self.phase = Phase.BETTING

    def begin_round(self, round: int):
        """
        Begin a fight round.
        """
        if self.phase not in (Phase.BETTING, Phase.FIGHT):
            raise GameError("Game must be in betting or fight phase to start a new round")

        # All players must have betted.
        if not self.all_players_bet():
            raise GameError("Not all players have placed their bets")

        if self.round >= MAX_ROUNDS:
            raise GameError("TODO: Game end not implemented yet")

        self.phase = Phase.FIGHT
        logger.debug("Round %d starting", round)

        self.round = round

        # Reset round turns by starting with first player
        first_player = self.first_player()
        assert first_player is not None, "Round started with no players"
        self.turn = first_player.player_id

    def next_round(self):
        """
        Advance the game to the next round.
        """
        self.begin_round(self.round + 1)

        # Refill player's cards
        self.deal_cards(self.determine_hand_size())

    def place_player_bets(self, player_id: int, monster_bets: list[str]) -> None:
        """
        Place the player's bet on their selected monsters,
        and check those bets against the game rules.
        """
        player = self.find_player(player_id)
        if not player:
            # TODO: This check for a player must live in a validation layer, and check an auth token.
            raise GameError("Player-%s doesn't exist")

        # Rule: Game must be in betting phase.
        if not self.is_betting_phase:
            raise GameError("Bets can only be placed during the betting phase")

        # Rule: Player can only bet on 1, 2 or 3 monsters during a round.
        if len(monster_bets) not in MONSTER_BET_COUNT:
            raise GameError("Bet cannot contain more than 3 monsters")

        # Rule: Player can only bet on monsters that are in the arena.
        game_monsters = set(monster.monster_id for monster in self.monsters)
        for monster_id in monster_bets:
            if monster_id not in game_monsters:
                raise GameError(f"Monster '{monster_id}' is not in the current game")

        # Rule: Players can change their bets in the betting phase.
        player.monster_bets = monster_bets

    def resolve_target(self, target: Target) -> None | Any:
        """
        Given a spell target, determine the precise instance.

        Returns:
            An instance of a monster, spell card, judge or player.
            ``None`` if no instance could be determined.
        """
        match target.kind:
            case TargetKind.MONSTER:
                if not isinstance(target.target_id, str):
                    raise TypeError("Monster target ID must be a string")

                monster = self.find_monster(target.target_id)
                if monster is None:
                    raise GameError(f"Monster target ID does not exist: {target.target_id}")

                return monster

            case TargetKind.SPELL:
                if not isinstance(target.target_id, int):
                    raise TypeError(f"Spell target ID must be a integer: {target.target_id}")

                # Spell cards are all over the place
                return self.resolve_spell_card(target.target_id)

            case TargetKind.PLAYER:
                # Player is targeting themselves
                if not isinstance(target.target_id, int):
                    raise TypeError("Player target ID must be a integer")

                player = self.find_player(target.target_id)
                if player is None:
                    raise GameError(f"Player target ID does not exist: {target.target_id}")

            case TargetKind.JUDGE:
                if not isinstance(target.target_id, int):
                    raise TypeError(f"Judge target ID must be a integer: {target.target_id}")

                return self.judge

            case _:
                raise GameError(f"Unknown target kind: {target.kind}")

        return None

    def resolve_spell_card(self, spell_id: int) -> Card | None:
        # The many places where spells can live
        # On monsters
        # On the judge
        # In a player's hand
        raise NotImplementedError("TODO")

    def move(self, move_id: str, *args, **kwargs):
        self.moves.append(Move(move_id, *args, **kwargs))

    def enqueue(self, move: Move):
        self.moves.append(move)

    def incr(self) -> int:
        self.counter += 1
        return self.counter

    def get_view(
        self,
        player_id: int,
        *,
        join_key: bool = False,
        watch_key: bool = False,
    ) -> GameView:
        """
        Create a redacted view of the game state, which is safe to
        show to a player.

        The view is specifically constructed for the requesting player.
        It must omit sensitive information about the game, server and
        other players.

        Arguments:
            player_id: The player that this state view is intended for.
            join_key: Indicates whether to include the join_key in the game view.
            watch_key: Indicates whether to include the watch_key in the game view.
        """
        others = []
        cards = []
        monster_bets = []

        for player in self.players:
            if player.player_id == player_id:
                # This is the requesting player
                cards = player.cards.copy()  # avoid shared state
                monster_bets = player.monster_bets.copy()
            else:
                # The requesting player's view of other players
                other_player = PlayerView(player.player_id, player.card_count, player.bet_count)
                others.append(other_player)

        return GameView(
            player_id,
            player_count=len(self.players),
            game_phase=self.phase,
            game_round=self.round,
            game_turn=self.turn,
            deck_count=len(self.spells),
            discard_count=len(self.discarded_spells),
            others=others,
            monsters=self.monsters.copy(),
            judge=self.judge,
            cards=cards,
            monster_bets=monster_bets,
            created_at=self.created_at,
            join_key=self.join_key if join_key else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self, dict_factory=asdict_factory)
