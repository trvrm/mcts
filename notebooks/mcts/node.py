"""
    Enforcing the generic type rules here is turning out to be far harder than I 
    expected.
    
    I want Node to be templated on a State type, 
    and I want State to be required to define a Command type.
    
    I'm actually not sure that this is possible
    
    What if Node only knows about State, not about Command?
"""

import time
from typing import Optional, List, Protocol, Any
from math import sqrt, log
import random

from .common import Result, Player, other_player

#
class StateProtocol(Protocol):
    def apply(self, command: Any) -> "StateProtocol":
        ...

    def playout(self) -> Result:
        ...

    player: Player
    commands: List
    result: Result
    command: Any

class MCTSException(Exception):
    pass
 

# This is going to be generic on command, state
class Node:
    "State is immutable, nodes are not"

    def __init__(self, state: StateProtocol, parent: Optional["Node"] = None) -> None:

        assert parent is not self
        self.parent = parent
        self.state = state
        # we may want this to be a set?
        self.children: List[Node] = []
        self.playouts = 0
        self.wins = 0.0

        self.depth: int = 0 if self.parent is None else 1 + self.parent.depth

    def __repr__(self) -> str:
        ratio = self.ratio
        if ratio is not None:
            ratio = round(ratio, 2)
        return f"Node(depth={self.depth},wins={self.wins},playouts={self.playouts}, ratio={ratio}, children={len(self.children)})"

    @property
    def is_leaf(self) -> bool:
        "'leaf' is any node that has a potential child from which no playout has been run."
        if len(self.children) < len(self.state.commands):
            return True

        if any(node.playouts == 0 for node in self.children):
            assert 0, str([c.playouts for c in self.children])
            assert 0, f"Does this ever happen? {self}"

            return True
        return False

    def size(self) -> int:
        return 1 + sum(child.size() for child in self.children)

    @property
    def ratio(self) -> float:
        if self.wins == 0:
            return 0
        return self.wins / self.playouts

    def expand(self) -> "Node":
        "create a new child state from this node"

        if self.state.result != Result.INPROGRESS:
            # can't really expand any more, so we'll just
            # backprop the value of the finished game
            return self

        assert len(self.state.commands) > 0
        assert self.is_leaf
        assert len(self.children) < len(self.state.commands)

        # pick a command that hasn't been used already
        possible = set(self.state.commands)  # available legal commands

        used = set(
            child.state.command for child in self.children
        )  # commands that we've already expanded into the tree

        available = list(possible - used)
        command = random.choice(available)

        child: Node = Node(
            state=self.state.apply(command),
            parent=self,
        )
        self.children.append(child)

        return child

    def best(self) -> "Node":
        """
        Wikipedia says
        "the move with the most simulations made (i.e. the highest denominator)
        is chosen as the final answer."
        """
        assert len(self.children)
        # if len(root.children)==0:
        #     return None # we haven't explored any commands from this node

        return max(self.children, key=lambda n: n.playouts)

    def select(self) -> "Node":
        """
        given a node return a node that is a leaf.
        Implement explore vs exploit here!

        If this node is a leaf we return it, otherwise we pick a child
        and call select on it
        """
        if self.is_leaf:
            return self

        # ok, I'm not a leaf. Therefore the number of
        # children I have is equal to the number of legal moves
        assert len(self.children) == len(self.state.commands)

        # we can't go down any further, but this node can't be expanded.
        if len(self.state.commands) == 0:
            assert self.state.result != Result.INPROGRESS
            assert len(self.children) == 0
            return self

        for child in self.children:
            assert child.parent is self

        scores = [uct_score(child) for child in self.children]
        index = scores.index(max(scores))

        return self.children[index].select()


def uct_score(node: Node) -> float:
    assert node.parent is not None
    # choose in each node of the game tree the move for which the expression UCT has the highest value
    s_i = node.playouts
    s_p = node.parent.playouts
    assert node.parent is not None, "UCT requires node has a parent"
    assert s_p > 0, "How come parent hasn't had any playouts?"
    w_i = node.wins
    c = sqrt(2)  # exploration parameter

    # https://medium.com/@quasimik/monte-carlo-tree-search-applied-to-letterpress-34f41c86e238
    return w_i / s_i + c * sqrt(log(s_p) / s_i)


def backprop(node: Node, result: Result) -> None:

    """node.state.player is the player to play, so the player who has just played the move
    is the one we care about

    """
    assert result in (Result.PLAYER1, Result.PLAYER2, Result.DRAW)

    # the player who just played the move that got us to this state
    player = other_player(node.state.player)

    if result == Result.PLAYER1 and player == Player.ONE:
        node.wins += 1

    if result == Result.PLAYER2 and player == Player.TWO:
        node.wins += 1

    if result == Result.DRAW:
        node.wins += 0.5

    node.playouts += 1

    if node.parent is not None:
        backprop(node.parent, result)


def mcts(root: Node) -> None:
    leaf = root.select()
    c = leaf.expand()
    result = c.state.playout()
    backprop(c, result)
    
    
def learn(root:Node, seconds:float)->None:
    end=time.time()+seconds
    while time.time()<end:
        mcts(root)
