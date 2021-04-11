import time
from typing import Optional, List, Protocol, Any, Dict, TypeVar, Generic
from math import sqrt, log
import random

from .common import Result, Player, other_player

Command = Any


class StateProtocol(Protocol):
    """
    A game state class is any class that can provide a current player,
    a current result, a list of available commands, and a
    way of aquiring a new state by applying a command
    """

    def apply(self, command: Command) -> "StateProtocol":
        ...

    player: Player
    result: Result
    commands: List


StateType = TypeVar("StateType", bound=StateProtocol)


class MCTSException(Exception):
    pass


class Node(Generic[StateType]):

    "State is immutable, nodes are not"

    def __init__(self, state: StateType) -> None:
        self.state = state
        self.children: Dict[Command, Node] = {}
        self.playouts = 0
        self.wins = 0.0

    def __repr__(self) -> str:
        return f"Node{type(self.state)}(playouts={self.playouts}, ratio={round(self.ratio,3)})"

    @property
    def is_leaf(self) -> bool:
        "'leaf' is any node that has a potential child from which no playout has been run."

        if len(self.children) < len(self.state.commands):
            return True

        # We always run a playout when we create a new node.
        assert all(child.playouts > 0 for child in self.children.values())

        return False

    @property
    def ratio(self) -> float:
        if self.wins == 0:
            return 0
        return self.wins / self.playouts

    def select(self) -> List["Node"]:
        """
        Given a node return a node that is a leaf.

        If this node is a leaf we return it, otherwise we pick a child
        and call select on it

        We return the full path from self to the leaf, to make backprop easier.

        Here is where we do explore vs exploit.

        """
        if self.is_leaf:
            return [self]
        if len(self.state.commands) == 0:
            # This is a terminal state
            return [self]

        highest_scoring_child = max(
            self.children.values(), key=lambda node: node.uct_score(self.playouts)
        )

        return [self] + highest_scoring_child.select()

    def expand(self) -> "Node":
        "create a new child state from this node"

        if self.state.result != Result.INPROGRESS:
            print(self.state)
        assert self.state.result == Result.INPROGRESS
        assert len(self.state.commands) > 0
        assert self.is_leaf
        assert len(self.children) < len(self.state.commands)

        # pick a command that hasn't been used already
        available = list(set(self.state.commands) - set(self.children.keys()))

        command = random.choice(available)

        child: Node = Node(state=self.state.apply(command))

        self.children[command] = child

        return child

    def best(self) -> Command:
        """
        Wikipedia says
        "the move with the most simulations made (i.e. the highest denominator)
        is chosen as the final answer."
        """

        commands = self.children.keys()
        return max(commands, key=lambda command: self.children[command].playouts)

    def best_line(self) -> List:
        if len(self.children):
            best = self.best()
            return [best] + self.children[best].best_line()
        else:
            return []
    
    def best_line2(self)->List["Node"]:
        if len(self.children):
            best=self.best()
            return [self] + self.children[best].best_line2()
        else:
            return [self]
    
    def uct_score(self, parent_playouts: int) -> float:
        """
        UCT is 'Upper Confidence Bound Applied to Trees'.

        See https://en.wikipedia.org/wiki/Monte_Carlo_tree_search#Exploration_and_exploitation

        and

        https://medium.com/@quasimik/monte-carlo-tree-search-applied-to-letterpress-34f41c86e238

        """
        assert parent_playouts > 0

        # explore-vs-exploit parameter
        C = sqrt(2)

        explore = self.wins / self.playouts
        exploit = C * sqrt(log(parent_playouts) / self.playouts)

        return explore + exploit


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


def backprop(path: List[Node], result: Result) -> None:
    for node in path:
        update_node(node, result)


def playout(node) -> Result:
    state = node.state
    while state.result == Result.INPROGRESS:
        command = random.choice(state.commands)
        state = state.apply(command)
    return state.result


def expand(path: List[Node]) -> List[Node]:
    "Expand if possible, modify path to include new node"
    leaf = path[-1]

    if leaf.state.commands:
        path.append(leaf.expand())
    return path


def select(node: Node) -> List[Node]:
    return node.select()


def mcts(root: Node) -> None:
    assert root.state.result == Result.INPROGRESS
    path = select(root)
    path = expand(path)
    result = playout(path[-1])
    backprop(path, result)
