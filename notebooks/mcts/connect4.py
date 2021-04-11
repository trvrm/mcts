from typing import Optional
from dataclasses import dataclass
import numpy as np
from .common import Result, Player, other_player, GameOver, Illegal


def default_m() -> np.ndarray:
    return np.array([[0 for i in range(7)] for j in range(6)])


SIZE = 4


def diagonals_a(m):
    for offset in range(-2,5):
        d=m.diagonal(offset)
        for l in range(0, len(d)-3):
            yield(d[l:4+l])

def diagonals_b(m):
    f=np.fliplr(m)
    for offset in range(-2,5):
        d=f.diagonal(offset)
        for l in range(0, len(d)-3):
            yield(d[l:4+l])
def horizontals(m):
    
    # horizontals
    for i in range(4):
        for j in range(6):
            yield m[j,i:i+4]
def verticals(m):
   
    for i in range(7):
        for j in range(3):
            yield m[j:4+j,i]
             
def all_lines(m):
    yield from diagonals_a(m)
    yield from diagonals_b(m)
    yield from horizontals(m)
    yield from verticals(m)
    

def _result(m)->Result:
    # This is  3-4 times faster than my first attempt.
    l=np.array(list(all_lines(m)))
    
    
    
    if any(l.sum(axis=1)==4):return Result.PLAYER1
    if any(l.sum(axis=1)==-4):return Result.PLAYER2
    if not (m == 0).any(): return Result.DRAW
    return Result.INPROGRESS


@dataclass(frozen=True)
class Command:
    column: int

    def __post_init__(self) -> None:
        assert 0 <= self.column <= 6, "column must be between 0 and 6"

    def __repr__(self) -> str:
        return f"{self.column}"


 

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
        if self.result == Result.INPROGRESS:
            self.commands = [
                Command(i) for i, value in enumerate(top_row) if value == 0
            ]
        else:
            self.commands = []

    def __repr__(self) -> str:
        return f"""
            {self._m}
            {self.player}
            {self.result}
            {self.commands}
        """

    def apply(self, command: Command) -> "State":
        if self.result != Result.INPROGRESS:
            raise GameOver()

        if command not in self.commands:
            raise Illegal()

        m = self._m.copy()
        v = {Player.ONE: 1, Player.TWO: -1}[self.player]

        col = m[:, command.column]

        assert col[0] == 0

        j = [j for j, val in enumerate(col) if val == 0][-1]

        col[j] = v

        return State(m, other_player(self.player))
