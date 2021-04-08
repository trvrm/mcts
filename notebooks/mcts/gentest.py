"""
    clearly i don't understand python generics
"""
from typing import Protocol


class StateProto(Protocol):
    def meth(self) -> int:
        pass

    class Command:
        pass


class Node:
    def __init__(self, state: StateProto) -> None:
        self.state = state

    def test(self) -> int:
        return 1 + self.state.meth()


class MyState:
    def meth(self) -> int:
        return 42


class MyNotState:
    pass


def test() -> None:

    s = MyState()  # Fails mypy if we replace this with MyNotState
    n: Node = Node(s)

    assert 43 == n.test()
