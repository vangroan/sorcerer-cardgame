"""
Integration tests for casting spells on entities.
"""
import random

import pytest

from sorcerer.game.game_session import GameSession
from sorcerer.game.interface import Target, TargetKind
from sorcerer.game.cards import Firebolt
from sorcerer.game.effects import EffectContext, on_cast, on_round_end


@pytest.fixture(scope="function")
def game_fight() -> GameSession:
    random.seed("game_fight")
    game = GameSession(join_key="****")

    player_1 = game.create_new_player(is_leader=True)
    player_2 = game.create_new_player()

    game.begin_game()

    game.place_player_bets(player_1.player_id, ["monster_succubus"])
    game.place_player_bets(player_2.player_id, ["monster_dragon"])

    game.begin_round(0)

    return game


def test_direct_spell(game_fight: GameSession):
    player_1 = game_fight.find_player(0)
    assert player_1 is not None

    demon = game_fight.find_monster("monster_demon")
    assert demon is not None

    target = Target(kind=TargetKind.MONSTER, target_id=demon.monster_id)
    target_entity = game_fight.resolve_target(target)

    firebolt = Firebolt(0, owner=player_1.player_id)
    context = EffectContext(game_fight, firebolt, target, target_entity, caster=player_1)
    on_cast(context)

    assert demon.cards[0] is firebolt

    # TODO: There will be no spell played on round end
    on_round_end(context)

    assert demon.health == 4
