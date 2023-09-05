from sorcerer.game.cards import Firebolt


def test_card_effect_definition():
    firebolt = Firebolt(card_id=0)
    assert len(firebolt.effect_defs) > 0
