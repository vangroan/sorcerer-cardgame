from sorcerer.game.judges import Judge, Moira


def test_judge_disallows():
    moira = Moira()

    assert len(moira.disallows) > 0
    assert moira.disallows[0] == "direct"
    assert moira.disallow_forbidden == False
