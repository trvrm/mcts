"""
    Python generics
"""
from typing import Protocol, Any, List, TypeVar, Generic

from .common import Result, Player, other_player


class StateProtocol(Protocol):
    """
    I haven't yet figured out how to make *this* class generic on 'Command'
    """

    def apply(self, command: Any) -> "StateProtocol":
        ...

    player: Player
    result: Result
    commands: List


StateType = TypeVar("StateType", bound=StateProtocol)


class Node(Generic[StateType]):
    def __init__(self, state: StateType) -> None:
        self.state = state

    def test(self) -> int:

        return 1 + len(self.state.commands)


class MyState:
    def __init__(self, player: Player, result: Result) -> None:
        self.commands: List = []
        self.player = Player.ONE
        self.result = Result.INPROGRESS

    def apply(self, command: Any) -> "MyState":
        return MyState(other_player(self.player), Result.INPROGRESS)


class MyNotState:
    pass


def test() -> None:
    s = MyState(Player.ONE, Result.INPROGRESS)

    n: Node[MyState]
    n = Node(s)
    i: int = n.test()
