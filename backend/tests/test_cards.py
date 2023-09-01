from sorcerer.game.cards import Firebolt
from sorcerer.game.effects import Effect


def test_card_effect_definition():
    firebolt = Firebolt(card_id=0)
    assert len(firebolt.effects) > 0
