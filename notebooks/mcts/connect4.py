from typing import Optional
from dataclasses import dataclass
import numpy as np
from .common import Result, Player, other_player, GameOver, Illegal


def default_m() -> np.ndarray:
    return np.array([[0 for i in range(7)] for j in range(6)])


SIZE = 4


def _sub_result(m: np.ndarray) -> Result:
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

    return Result.INPROGRESS


def _result(m) -> Result:
    """
    We compute results by considering every possible
    4x4 grid and seeing if _that_ has a line in it, using
    the same algorithm as tic-tac-toe
    """
    for j in range(3):
        for i in range(4):
            sub = m[j : j + 4, i : i + 4]
            assert sub.size == 16
            assert sub.shape == (4, 4)
            r = _sub_result(sub)
            if r != Result.INPROGRESS:
                return r

    if not (m == 0).any():
        return Result.DRAW
        
    return Result.INPROGRESS


@dataclass(frozen=True)
class Command:
    column: int

    def __post_init__(self) -> None:
        assert 0 <= self.column <= 6, "column must be between 0 and 6"

    def __repr__(self) -> str:
        return f"({self.column})"


class State:
    def __init__(self, m: Optional[np.ndarray] = None, player: Optional[Player] = None):

        if m is None:
            assert player is None
            self.player = Player.ONE
            self._m = default_m()
        else:
            assert player is not None
            self._m = m
            self.player = player
        self.result = _result(self._m)

        top_row = self._m[0]
        if self.result==Result.INPROGRESS:
            self.commands = [Command(i) for i, value in enumerate(top_row) if value == 0]
        else:
            self.commands=[]

    def __repr__(self)->str:
        return f"""
            {self._m}
            {self.player}
            {self.result}
            {self.commands}
        """

    def apply(self,command:Command)->"State":
        if self.result != Result.INPROGRESS:
            raise GameOver()

        if command not in self.commands:
            raise Illegal()
            
        m = self._m.copy()
        v = {Player.ONE: 1, Player.TWO: -1}[self.player]
        
        col = m[:,command.column]

        assert col[0]==0
        
        j=[j for j, val in enumerate(col) if val==0][-1]
        
        col[j]=v
        
        return State(m, other_player(self.player))
        
        
        
        