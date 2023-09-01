import logging
import random

from sorcerer.game.game_session import GameSession

logger = logging.getLogger(__name__)
JOIN_KEY = "****"


def test_begin_game() -> None:
    game = GameSession(JOIN_KEY)

    game.create_new_player(is_leader=True)
    game.create_new_player(is_leader=False)

    game.begin_game()
    logger.debug("GameSession: %s", game.to_dict())

    assert game.judge is not None, "No judge was chosen"
    assert len(game.monsters) > 0, "No monster were chosen"
    assert game.players[0].card_count > 0, "Player was not dealth cards"


def test_betting_phase() -> None:
    random.seed("test_betting_phase")

    game = GameSession(JOIN_KEY)

    player_1 = game.create_new_player(is_leader=True)
    player_2 = game.create_new_player(is_leader=False)
    _ = game.create_new_player(is_leader=False)

    game.begin_game()
    logger.debug("GameSession: %s", game.to_dict())

    assert game.is_betting_phase

    game.place_player_bets(player_1.player_id, ["monster_succubus", "monster_darkelf"])
    game.place_player_bets(player_2.player_id, ["monster_demon"])
    assert game.players[1].monster_bets == ["monster_demon"]
    assert game.players[0].monster_bets == ["monster_succubus", "monster_darkelf"]


def test_begin_fight() -> None:
    random.seed("test_begin_fight")

    game = GameSession(JOIN_KEY)

    player_1 = game.create_new_player(is_leader=True)
    player_2 = game.create_new_player(is_leader=False)
    player_3 = game.create_new_player(is_leader=False)

    game.begin_game()
    logger.info("GameSession: %s", game)

    game.place_player_bets(player_1.player_id, ["monster_lizardman"])
    game.place_player_bets(player_2.player_id, ["monster_skeleton"])
    game.place_player_bets(player_3.player_id, ["monster_skeleton", "monster_darkelf"])

    assert game.round != 0
    game.begin_round(0)

    assert game.is_fight_phase
    assert game.round == 0
