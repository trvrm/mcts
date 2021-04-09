"""
    Enforcing the generic type rules here is turning out to be far harder than I 
    expected.
    
    I want Node to be templated on a State type, 
    and I want State to be required to define a Command type.
    
    I'm actually not sure that this is possible
    
    What if Node only knows about State, not about Command?
"""

import time
from typing import Optional, List, Protocol, Any, Dict, TypeVar, Generic
from math import sqrt, log
import random

from .common import Result, Player, other_player


class StateProtocol(Protocol):
    """
    A game state class is any class that can provide a current player,
    a current result, a list of available commands, and a
    way of aquiring a new state by applying a command
    """

    def apply(self, command: Any) -> "StateProtocol":
        ...

    player: Player
    result: Result
    commands: List


StateType = TypeVar("StateType", bound=StateProtocol)


class MCTSException(Exception):
    pass


class Node(Generic[StateType]):

    "State is immutable, nodes are not"

    def __init__(self, state: StateType, parent: Optional["Node"] = None) -> None:

        assert parent is not self
        self.parent = parent
        self.state = state
        self.children: Dict[Any, Node] = {}
        self.playouts = 0
        self.wins = 0.0

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

        # We always run a playout when we create a new node.
        assert all(child.playouts > 0 for child in self.children.values())

        return False

    @property
    def size(self) -> int:
        return 1 + sum(child.size for command, child in self.children.items())

    @property
    def depth(self) -> int:
        "It would be better to compute this once during backprop"
        return 1 + max(
            (child.depth for command, child in self.children.items()), default=0
        )

    @property
    def ratio(self) -> float:
        if self.wins == 0:
            return 0
        return self.wins / self.playouts

    def select(self) -> "Node":
        """
        Given a node return a node that is a leaf.

        Here is where we do explore vs exploit.

        If this node is a leaf we return it, otherwise we pick a child
        and call select on it
        """
        if self.is_leaf:
            return self

        # I'm not a leaf. Therefore the number of
        # children I have is equal to the number of legal moves
        assert len(self.children) == len(self.state.commands)

        # we can't go down any further, but this node can't be expanded.
        if len(self.state.commands) == 0:
            assert self.state.result != Result.INPROGRESS
            assert len(self.children) == 0
            return self

        for child in self.children.values():
            assert child.parent is self

        highest_scoring_child = max(self.children.values(), key=uct_score)
        return highest_scoring_child.select()

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
        available = list(set(self.state.commands) - set(self.children.keys()))

        command = random.choice(available)

        child: Node = Node(
            state=self.state.apply(command),
            parent=self,
        )

        self.children[command] = child

        return child

    def best(self) -> Any:
        """
        Wikipedia says
        "the move with the most simulations made (i.e. the highest denominator)
        is chosen as the final answer."
        """

        commands = self.children.keys()
        return max(commands, key=lambda command: self.children[command].playouts)


def uct_score(node: Node) -> float:
    """
    UCT is 'Upper Confidence Bound Applied to Trees'.

    See https://en.wikipedia.org/wiki/Monte_Carlo_tree_search#Exploration_and_exploitation
    """
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


def update_node(node: Node, result: Result) -> None:
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


def backprop(node: Node, result: Result) -> None:

    """node.state.player is the player to play, so the player who has just played the move
    is the one we care about

    """
    update_node(node, result)

    if node.parent is not None:
        backprop(node.parent, result)


def playout(node) -> Result:
    state = node.state
    while state.result == Result.INPROGRESS:
        command = random.choice(state.commands)
        state = state.apply(command)
    return state.result


def mcts(root: Node) -> None:
    leaf = root.select()
    c = leaf.expand()
    result = playout(c)
    backprop(c, result)
