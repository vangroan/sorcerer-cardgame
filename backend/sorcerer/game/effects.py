from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Effect(ABC):
    effect_id: str = field(init=False)

    @abstractmethod
    def process(self) -> None:
        raise NotImplementedError()


# =============================================================================
# Monster Effects


class Undead(Effect):
    """
    Monster effect that inverts the power of all spells played on it.
    """

    effect_id: str = "effect_undead"

    def process(self) -> None:
        pass


# =============================================================================
# Judge Effects


class Dispel(Effect):
    effect_id: str = "effect_dispel"

    def process(self) -> None:
        pass


class Eject(Effect):
    effect_id: str = "effect_eject"

    def process(self) -> None:
        pass


# =============================================================================
# Spell Effects


@dataclass(frozen=True)
class Power(Effect):
    """
    Simple effect that increases or decreases a monster's power.
    """

    effect_id: str = "effect_power"
    power: int = field(init=True, default=0)

    def process(self) -> None:
        pass
