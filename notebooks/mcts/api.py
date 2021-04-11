from typing import Dict, Callable, Any, Optional, Union
import pathlib
import random
import string
import functools
import asyncio
import concurrent.futures
import json
from fastapi import FastAPI, WebSocket,  WebSocketDisconnect 

import time
from enum import Enum

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import tictactoe
from . import connect4
from .common import Player, Result
from .node import Node, mcts

app = FastAPI()


PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
STATIC_ROOT = PROJECT_ROOT / "static"


@app.get("/")
async def get() -> HTMLResponse:

    html = (PROJECT_ROOT / "static" / "index.html").read_text()
    return HTMLResponse(html)


app.mount("/static", StaticFiles(directory=str(STATIC_ROOT)), name="static")


# ractive helpers


def default_encoder(thing: Any) -> Any:
    if hasattr(thing, "__json__"):
        return thing.__json__()

    raise TypeError(repr(thing) + " is not JSON serializable")


dumps = functools.partial(
    json.dumps, indent=0, sort_keys=True, ensure_ascii=False, default=default_encoder
)


async def send_json(ws: WebSocket, data: Any) -> None:
    await ws.send_text(dumps(data))


async def ractive_set(ws: WebSocket, keypath: str, value: Any):
    await send_json(ws, ["set", keypath, value])


async def ractive_push(ws: WebSocket, keypath: str, value: Any):
    await send_json(ws, ["push", keypath, value])


async def notify(ws: WebSocket, text: str, level: str = "info") -> None:
    await ractive_push(ws, "notifications", {"text": text, "level": level})


message_handlers: Dict[str, Callable] = {}


def handle(name: str):
    def wrapper(func: Callable):
        message_handlers[name] = func
        return func

    return wrapper


class TicTacToeGame:
    def __init__(self) -> None:

        self.node = Node(tictactoe.State())

    def __json__(self):
        state = self.node.state
        return {
            "commands": [dict(i=cmd.i, j=cmd.j) for cmd in state.commands],
            "player": state.player,
            "result": state.result,
            "board": [
                [{0: "empty", -1: "X", +1: "O"}[cell] for cell in row]
                for row in state._m
            ],
            "name": "tictactoe",
            "size": tictactoe.SIZE,
        }


#
class Connect4Game:
    def __init__(self) -> None:
        self.node = Node(connect4.State())

    def __json__(self):
        return {
            "player": self.node.state.player,
            "result": self.node.state.result,
            "name": "connect4",
            "board": [
                [{0: "empty", -1: "X", +1: "O"}[cell] for cell in row]
                for row in self.node.state._m
            ],
        }


# Not even trying to sort out multiplayer, persistent state
# etc yet. That'll come later
current_game: Union[TicTacToeGame, Connect4Game, None] = None

# current_node:Optional[Node]=None


@handle("new_game")
async def handle_new_game(ws: WebSocket, what: str):
    global current_game
    assert what in ("tictactoe", "connect4")
    if what == "tictactoe":
        current_game = TicTacToeGame()
    else:
        current_game = Connect4Game()

    await ractive_set(ws, "current_game", current_game)


def apply_command(node: Node, command: Any) -> Node:
    if command in node.children:
        return node.children[command]
    else:
        return Node(node.state.apply(command))


@handle("connect4_move")
async def handle_connect4_move(ws: WebSocket, column: int) -> None:
    game = current_game
    if not isinstance(game, Connect4Game):
        return

    if game.node.state.result != Result.INPROGRESS:
        return

    if game.node.state.player != Player.ONE:
        return 
    command = connect4.Command(column=column)
    if command not in game.node.state.commands:
        return

    game.node = apply_command(game.node, command)

    await ractive_set(ws, "current_game", game)
    if game.node.state.result == Result.INPROGRESS:
        task = asyncio.create_task(pick_move(ws, game, 1.5))


@handle("tictactoe_move")
async def handle_tictactoe_move(ws: WebSocket, j: int, i: int) -> None:
    game = current_game

    if not isinstance(game, TicTacToeGame):
        return

    assert game.node.state.player == Player.ONE
    command = tictactoe.Command(j=j, i=i)
    if command not in game.node.state.commands:
        return

    game.node = apply_command(game.node, command)

    await ractive_set(ws, "current_game", game)

    if game.node.state.result == Result.INPROGRESS:
        task = asyncio.create_task(pick_move(ws, game, 1))


async def pick_move(
    ws: WebSocket, game: Union[TicTacToeGame, Connect4Game], seconds: int
) -> Any:

    if game is None:
        return
    if game != current_game:
        return None

    end = time.time() + seconds
    # very little thread safety here!
    #print(f"Before thinking: {game.node}")

    def think() -> None:
        while time.time() < end:
            mcts(game.node)

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, think)
    assert game.node.state.player == Player.TWO

    #print(f"{game.node.playouts} positions examined")
    print(game.node)
    # print(game.node.best_line())
    best = game.node.best()

    game.node = apply_command(game.node, best)

    # print(f"I think I have roughly a {round(100*game.node.ratio)} % chance of winning now")
    # 
    print("best line:", ",".join(repr(command) for command in game.node.best_line()))
    
    
    await ractive_set(ws, "current_game", game)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:

    await ws.accept()

    # I can store stuff in ws.state,
    try:
        while True:
            data = await ws.receive_json()

            assert isinstance(data, list)
            name, *args = data
            func: Optional[Callable] = message_handlers.get(name)

            if func is None:
                await notify(ws, f"no such function: {name}", "danger")
            else:
                try:
                    await func(ws, *args)
                except Exception as e:
                    print(e)
                    
                    await notify(ws, f"Error calling {name}: {e}", "warning")
    except WebSocketDisconnect:
        print('disconnect')
        pass
