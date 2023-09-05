import json
import logging
import asyncio
import secrets
from enum import Enum
from dataclasses import dataclass
from typing import Iterable, Generator

import websockets
from websockets.exceptions import ConnectionClosedOK
from websockets.server import serve, WebSocketServerProtocol

from sorcerer.game.errors import GameError
from sorcerer.game.game_session import GameSession, PlayerSession
from sorcerer.game.effects import EffectContext, on_cast

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass(eq=False, frozen=True)
class Client:
    player: PlayerSession
    websocket: WebSocketServerProtocol


StatePair = tuple[GameSession, set[Client]]

STATE: dict[str, StatePair] = {}

Message = str


class Kind(Enum):
    INIT = "init"  # First player initialises the game, or others join.
    JOINED = "joined"  # Notify all players that someone has joined.
    BEGIN = "begin"  # First player begins the game after other palyers have joined.
    NEXT_ROUND = "next_round"  # Betting is done and round starts.
    SETUP = "setup"  # Signal players that the server is setting up the game.
    STATE = "state"  # Player requested the latest state.
    BET = "bet"  # Player places a bet. Only valid during the "betting" phase.
    ACTION = "action"  # Player has played a card
    INCR = "incr"
    ERR = "error"

    def __str__(self) -> str:
        return str(self.value)


def error(message: str) -> Message:
    return json.dumps(
        {
            "kind": Kind.ERR.value,
            "message": message,
        }
    )


def broadcast(clients: Iterable[Client], kind: Kind, data: dict) -> None:
    data["kind"] = kind.value
    message = json.dumps(data)
    websockets.broadcast(get_websockets(clients), message)  # type: ignore


def get_websockets(
    clients: Iterable[Client],
) -> Generator[WebSocketServerProtocol, None, None]:
    for client in clients:
        yield client.websocket


async def play(
    websocket: WebSocketServerProtocol,
    player: PlayerSession,
    game: GameSession,
    clients: set[Client],
) -> None:
    """
    Game message pump.
    """
    async for message in websocket:
        try:
            data = json.loads(message)
            logger.debug("Player-%d recv: %s", player.player_id, data)

            try:
                message_kind = Kind(data.get("kind"))
            except ValueError:
                logger.warning("Unknown message kind: %s", data.get("kind"))
                await websocket.send(json.dumps({"kind": "error", "message": "Unknown message kind"}))
                continue

            if message_kind == Kind.INCR:
                new_count = game.incr()
                data = {"count": new_count, "player_id": player.player_id}
                broadcast(clients, Kind.INCR, data)
            elif message_kind == Kind.BEGIN:
                # All players are ready. Begin the game.
                if player.is_leader:
                    broadcast(
                        clients,
                        Kind.SETUP,
                        {"message": "Server is setting up the game"},
                    )
                    game.begin_game()
                else:
                    await websocket.send(error("Only the leader can begin the game"))
            elif message_kind == Kind.STATE:
                game_view = game.get_view(player.player_id, join_key=True)
                await websocket.send(json.dumps({"kind": str(Kind.STATE), "game": game_view.to_dict()}))
            elif message_kind == Kind.BET:
                if not game.is_betting_phase:
                    logger.warning(
                        "Player-%d placed bet outside of betting phase",
                        player.player_id,
                    )
                    await websocket.send(error("Bet must specify Monster IDs"))

                elif monster_ids := data.get("monster_ids"):
                    if isinstance(monster_ids, list):
                        monser_bets = [str(monster_id) for monster_id in monster_ids]
                        game.place_player_bets(player.player_id, monser_bets)

                        game_view = game.get_view(player.player_id, join_key=True)
                        await websocket.send(json.dumps({"kind": str(Kind.BET), "game": game_view.to_dict()}))
                    else:
                        await websocket.send(error("monster_ids must be an array"))

                else:
                    await websocket.send(error("Bet must specify Monster IDs"))

            elif message_kind == Kind.NEXT_ROUND:
                if not player.is_leader:
                    logger.warning(
                        "Player-%d attempted to begin fight phase, but isn't leader",
                        player.player_id,
                    )
                    await websocket.send(error("You are not the leader"))

                elif not game.is_betting_phase:
                    logger.warning(
                        "Player-%d began fight outside of betting phase",
                        player.player_id,
                    )
                    await websocket.send(error("Game must be in betting phase"))

                game.begin_round(0)
                broadcast(clients, Kind.NEXT_ROUND, {})

            elif message_kind == Kind.ACTION:
                card_id = data["card_id"]
                target = data.get["target"]

                # Lookup target instance
                target_entity = game.resolve_target(target)

                # Lookup card instance that player is playing
                spell_card = game.find_player_card(player.player_id, card_id)

                if spell_card is None:
                    raise GameError(f"Player-{player.player_id} does not have card {card_id}")

                context = EffectContext(game, spell_card, target, target_entity, caster=player)
                on_cast(context)

        except GameError as err:
            logger.debug("Player-%d violated a game rule: %s", player.player_id, err.message)
            data = err.to_dict()
            message = json.dumps(data)
            await websocket.send(message)

        except json.JSONDecodeError:
            # Not a JSON payload. Just Echo.
            await websocket.send(message)

        except ConnectionClosedOK:
            logger.info("Connection closed OK")
            break


async def start(websocket: WebSocketServerProtocol) -> None:
    join_key = secrets.token_urlsafe(12)
    game = GameSession(join_key)

    player = game.create_new_player(is_leader=True)
    clients = {Client(player, websocket)}

    STATE[join_key] = game, clients

    logger.info("Started game session: %s", id(game))

    try:
        event = {
            "kind": "init",
            "join": join_key,
        }
        await websocket.send(json.dumps(event))

        await play(websocket, player, game, clients)

    finally:
        logger.info("Cleaning up game: %s", join_key)
        del STATE[join_key]


async def join(websocket: WebSocketServerProtocol, join_key: str) -> None:
    logger.debug("Available games: %s", list(STATE.keys()))

    try:
        game, clients = STATE[join_key]
    except KeyError:
        logger.info("Game not found for key: %s", join_key)
        await websocket.send(error("Game not found"))
        await websocket.close()
        return

    # Players must join during the lobby phase
    if not game.is_lobby_phase:
        await websocket.send(error("Game has already started"))
        await websocket.close()

    player = game.create_new_player(is_leader=False)
    client = Client(player, websocket)

    # Register to receive broadcasted messages
    clients.add(client)

    broadcast(clients, Kind.JOINED, {"player_id": player.player_id})

    try:
        await play(websocket, player, game, clients)

    finally:
        clients.remove(client)


async def handle(websocket: WebSocketServerProtocol) -> None:
    message = await websocket.recv()
    cmd = json.loads(message)
    assert cmd["kind"] == "init"

    # Both start and join are handled on the same URI
    # because the join key is considered sensitive information.
    #
    # It is slightly more secure to send it in a message because
    # URIs are recorded in logs.
    if "join" in cmd:
        # Second player
        await join(websocket, cmd["join"])
    else:
        # First player starts the game
        await start(websocket)


async def main():
    async with serve(handle, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())
