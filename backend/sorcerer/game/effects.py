"""
Effects of monsters, judges and spells.

This is the bulk of the game logic, which touches all
types in the domain.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence
from sorcerer.game.errors import GameError

from sorcerer.game.interface import EffectDef, Target
from sorcerer.game.monsters import Monster
from sorcerer.game.game_session import GameSession, PlayerSession
from sorcerer.game.cards import Card

logger = logging.getLogger(__name__)


def on_cast(context: EffectContext):
    """
    Hook executed when a player casts a spell card.
    """
    pairs = resolve_effects(context.spell_card.effect_defs)
    _map_effects(pairs, lambda effect: effect.on_cast(context))


def on_round_end(context: EffectContext):
    """
    Hook executed when a fight round ends.
    """
    pairs = resolve_effects(context.spell_card.effect_defs)
    _map_effects(pairs, lambda effect: effect.on_round_end(context))


_EffectPairs = list[tuple[type["Effect"], EffectDef]]
"""Effect class types and the indirect data definitions that were used to look them up."""


def _map_effects(effects: _EffectPairs, func: Callable[[Effect], None]):
    """
    Map the given callable to the list of effect types given.
    """
    for effect_cls, effect_def in effects:
        args, kwargs = effect_def.args_kwargs
        logger.debug("Instantiating effect: %s(*%s, **%s)", effect_cls, args, kwargs)
        effect = effect_cls(*args, **kwargs)
        func(effect)


def resolve_effects(
    effect_defs: Sequence[EffectDef],
) -> _EffectPairs:
    pairs = [(resolve_effect(effect_def.name), effect_def) for effect_def in effect_defs]

    result: _EffectPairs = []
    errors: list[str] = []
    for effect, effect_def in pairs:
        if effect is None:
            errors.append(effect_def.name)
        else:
            result.append((effect, effect_def))

    if errors:
        raise GameError(f"Card effect(s) do not exist: {', '.join(errors)}")

    return result


def resolve_effect(class_name: str) -> type[Effect] | None:
    return _TYPES.get(class_name)


_TYPES: dict[str, type[Effect]] = {}


def _register(ty: type) -> type:
    _TYPES[ty.__name__] = ty
    # NOTE: Logged records will not print if this module is imported before logging is setup.
    logger.debug("Registering effect type: %s" % ty.__name__)
    return ty


@dataclass(frozen=True)
class EffectContext:
    """
    Contextual state passed to a played card, to mutate game state.
    """

    game_session: GameSession
    spell_card: Card  # Spell that casted this effect
    target: Target | None  # Targeting information
    target_entity: Any | None  # Instance of entity being targeted
    caster: PlayerSession  # The player that casted the spell card


@dataclass(frozen=True)
class Effect(ABC):
    effect_id: str = field(init=False)

    @abstractmethod
    def process(self, ctx: EffectContext) -> None:
        raise NotImplementedError()

    def on_cast(self, ctx: EffectContext):
        """
        Hook executed when a player casts a spell card.
        """
        ...

    def on_round_end(self, ctx: EffectContext) -> None:
        """
        Hook executed when a fight round ends.
        """
        ...


# =============================================================================
# Monster Effects


@dataclass(frozen=True)
@_register
class Undead(Effect):
    """
    Monster effect that inverts the power of all spells played on it.
    """

    effect_id: str = "effect_undead"

    def process(self, ctx: EffectContext) -> None:
        pass


# =============================================================================
# Judge Effects


@dataclass(frozen=True)
@_register
class Dispel(Effect):
    effect_id: str = "effect_dispel"

    def process(self, ctx: EffectContext) -> None:
        pass


@dataclass(frozen=True)
@_register
class Eject(Effect):
    effect_id: str = "effect_eject"

    def process(self, ctx: EffectContext) -> None:
        pass


# =============================================================================
# Spell Effects


@dataclass(frozen=True)
@_register
class Power(Effect):
    """
    Simple effect that increases or decreases a monster's power.
    """

    effect_id: str = "effect_power"
    power: int = field(init=True, default=0)

    def process(self, ctx: EffectContext) -> None:
        monster: Monster = ctx.target_entity  # type: ignore
        monster.cards.append(ctx.spell_card)

    def on_cast(self, ctx: EffectContext):
        monster: Monster = ctx.target_entity  # type: ignore
        monster.cards.append(ctx.spell_card)

    def on_round_end(self, ctx: EffectContext) -> None:
        monster: Monster = ctx.target_entity  # type: ignore
        monster.health += self.power
