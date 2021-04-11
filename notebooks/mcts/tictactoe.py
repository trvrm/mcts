from typing import Optional, Dict
import numpy as np
import time
from collections import Counter

from dataclasses import dataclass


from .common import Result, Player, other_player, Illegal, GameOver


SIZE = 3


def _result(m: np.ndarray) -> Result:
    if any((m.sum(axis=1)) == SIZE):
        return Result.PLAYER1
    if any((m.sum(axis=0)) == SIZE):
        return Result.PLAYER1
    if m.trace() == SIZE:
        return Result.PLAYER1
    if np.fliplr(m).trace() == SIZE:
        return Result.PLAYER1

    if any((m.sum(axis=1)) == -SIZE):
        return Result.PLAYER2
    if any((m.sum(axis=0)) == -SIZE):
        return Result.PLAYER2
    if m.trace() == -SIZE:
        return Result.PLAYER2
    if np.fliplr(m).trace() == -SIZE:
        return Result.PLAYER2

    if not (m == 0).any():
        return Result.DRAW

    return Result.INPROGRESS


@dataclass(frozen=True)
class Command:
    j: int
    i: int

    def __post_init__(self):
        assert 0 <= self.i < SIZE, f"i must be between 0 and {SIZE-1}"
        assert 0 <= self.j < SIZE, f"j must be between 0 and {SIZE-1}"

    def __repr__(self) -> str:
        return f"({self.i},{self.j})"


# State classes should be treated as immutable
class State:
    def __init__(
        self,
        m: Optional[np.ndarray] = None,
        player: Optional[Player] = None,
    ) -> None:
        if m is None:
            assert player is None
            self.player = Player.ONE
            self._m = np.array([[0 for i in range(SIZE)] for j in range(SIZE)])
        else:
            assert player is not None
            self._m = m
            self.player = player

        self.result = _result(self._m)

        if self.result == Result.INPROGRESS:
            self.commands = [
                Command(j, i)
                for j in range(SIZE)
                for i in range(SIZE)
                if self._m[j, i] == 0
            ]
        else:
            self.commands = []

    def __repr__(self) -> str:
        d = {0: " ", -1: "X", 1: "O"}
        return (
            ("\n" + "-" * (SIZE * 2 - 1) + "\n").join(
                ["|".join(d[el] for el in line) for line in self._m]
            )
        ) + f"    player {self.player}"

    def apply(self, command: Command) -> "State":

        if self.result != Result.INPROGRESS:
            raise GameOver()

        if command not in self.commands:
            raise Illegal()

        if self._m[command.j, command.i] != 0:
            raise Illegal()

        m = self._m.copy()
        v = {Player.ONE: 1, Player.TWO: -1}[self.player]
        m[command.j, command.i] = v
        return State(m, other_player(self.player))
