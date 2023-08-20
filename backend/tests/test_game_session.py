import logging

import pytest

from sorcerer.game.game_session import GameSession

JOIN_KEY = "****"


def test_begin_game() -> None:
    game = GameSession(JOIN_KEY)

    game.create_new_player(is_leader=True)
    game.create_new_player(is_leader=False)

    game.begin_game()
    print("GameSession: ", game.to_dict())

    assert game.judge is not None, "No judge was chosen"
    assert len(game.monsters) > 0, "No monster were chosen"
