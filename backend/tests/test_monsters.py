from dataclasses import asdict, FrozenInstanceError

import pytest
from sorcerer.game.cards import Firebolt
from sorcerer.game.monsters import Demon


def test_monster_contract():
    demon_1 = Demon()
    data = asdict(demon_1)

    assert demon_1.monster_id == "monster_demon", "card_id data contract not working as expected"
    assert data["monster_id"] == "monster_demon", "card_id is not converted by asdict"

    with pytest.raises(FrozenInstanceError):
        demon_1.monster_id = "****"

    demon_1.cards.append(Firebolt())
    print("Demon: ", demon_1)


def test_shared_state():
    """Ensure that monster instances are not implicitly shared."""
    demon_1 = Demon()
    demon_2 = Demon()

    assert demon_1 is not demon_2

    demon_1.cards.append(Firebolt())
    assert len(demon_1.cards) == 1
    assert len(demon_2.cards) == 0
