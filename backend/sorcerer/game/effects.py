from abc import ABC
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Effect(ABC):
    effect_id: str = field(init=False)


# =============================================================================
# Monster Effects


@dataclass(frozen=True)
class Undead(Effect):
    """
    Monster effect that inverts the power of all spells played on it.
    """

    effect_id: str = "effect_undead"


# =============================================================================
# Judge Effects


@dataclass(frozen=True)
class Dispel(Effect):
    effect_id: str = "effect_dispel"


@dataclass(frozen=True)
class Eject(Effect):
    effect_id: str = "effect_eject"
