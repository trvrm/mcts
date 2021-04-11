import cProfile, pstats, io
from pstats import SortKey

import time
from typing import Any
from .node import Node,mcts
from .common import Result, Player
from .import connect4
import random
Command=Any
def apply_command(node: Node, command: Any) -> Node:
    if command in node.children:
        return node.children[command]
    else:
        return Node(node.state.apply(command))


def pick_move(root: Node, seconds: float) -> Command:
    end = time.time() + seconds
    while time.time() < end:
        mcts(root)
        return root.best()

def play():

    node = Node(connect4.State())
    while node.state.result == Result.INPROGRESS:
        move = pick_move(node, 1)
        node = apply_command(node, move)
    print(f"GAME OVER, result is {node.state.result}")

if __name__ == "__main__":
    random.seed(12345)
    pr = cProfile.Profile()
    pr.enable()
    
    for i in range(10):
        play()
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
    