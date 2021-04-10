from typing import Dict, Callable, Any, Optional
import pathlib
import random 
import string
import functools 
import asyncio
import concurrent.futures
import json
from fastapi import FastAPI, WebSocket 
import time
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import models
from . import tictactoe
from .common import Player, Result
from .node import Node, mcts
app = FastAPI()
  

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
STATIC_ROOT = PROJECT_ROOT / "static"

@app.get("/")
async def get()->HTMLResponse:
    
    html = (PROJECT_ROOT / "static"/"index.html").read_text()
    return HTMLResponse(html)


app.mount("/static", StaticFiles(directory=str(STATIC_ROOT)), name="static")



# ractive helpers 


def default_encoder(thing:Any)->Any:
    if hasattr(thing, "__json__"):
        return thing.__json__()
    
    raise TypeError(repr(thing) + " is not JSON serializable")
    
dumps = functools.partial(
    json.dumps, indent=0, sort_keys=True, ensure_ascii=False, default=default_encoder
)


async def send_json(ws:WebSocket, data:Any)->None:
    await ws.send_text(dumps(data))

async def ractive_set(ws:WebSocket, keypath:str, value:Any):
    await send_json(ws, ["set", keypath, value])


async def ractive_push(ws:WebSocket, keypath:str, value:Any):
    await send_json(ws, ["push", keypath, value])

async def notify(ws:WebSocket, text:str, level:str="info")->None:
    await ractive_push(ws, "notifications", {"text": text, "level": level})

message_handlers:Dict[str,Callable] = {}

def handle(name:str):
    def wrapper(func:Callable):
        message_handlers[name] = func
        return func

    return wrapper


class Game:
    def __init__(self,name:str)->None:
        self.name=name
        self.state=tictactoe.State()
        
        
    def __json__(self):
        return {
            "commands":[dict(i=cmd.i, j=cmd.j) for cmd in self.state.commands],
            "player":self.state.player,
            "result":self.state.result,
            "board":[
                [
                {0:"empty",-1:"X",+1:"O"}[cell]
                    for cell in row
                ]
                for row in self.state._m
            ],
            "name":self.name,
            "size":tictactoe.SIZE
            
        }

games:Dict[str, Game]={}

def new_name()->str:
    return "".join(random.choices(string.ascii_letters,k=8))
    
@handle("new_game")
async def handle_new_game(ws:WebSocket , who:str):
    assert who in ("human", "bot")
    name=new_name()
    game = Game(name)
    
    games[name]=game # not hashable :-(
    
    await ractive_set(ws, "current_game",game)
    
@handle("play_move")
async def handle_play_move(ws:WebSocket,name:str, j:int, i:int):
    game = games[name]
    assert game.state.player==Player.ONE
    command=tictactoe.Command(j=j,i=i)
    if command not in game.state.commands:
        return 
    
    game.state=game.state.apply(command)
        
    await ractive_set(ws, "current_game",game) 
    
    if game.state.result==Result.INPROGRESS:
        task = asyncio.create_task(play_move(ws, name, game.state))
    else:
        print(f"No, result is {game.state.result}")
    
async def play_move(ws:WebSocket, name:str, state:tictactoe.State)->None:
    loop = asyncio.get_running_loop()

    SECONDS=0.75
    end=time.time()+SECONDS
    root:Node[tictactoe.State]=Node(state)
    
    def blocking():
        mcts(root)
        i=0
        while time.time()<end:
            print(f'mcts {i}')
            path=mcts(root)
            i+=1
        return root.best()
    
    best = await loop.run_in_executor( None, blocking)
    game=games[name]
    assert game.state.player==Player.TWO 
    
    
    game.state = state.apply(best) 
    
    await ractive_set(ws, "current_game",game)
    #await ractive_set(ws, "root_info",str(root)) 
    
    
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket)->None:

    await ws.accept()
    while True:
        data = await ws.receive_json()
        print(data)
        assert isinstance(data,list)
        name, *args = data
        func:Optional[Callable] = message_handlers.get(name)
        
        if func is None:
            await notify(ws, f"no such function: {name}", "danger")
        else:
            await func(ws, *args)
         