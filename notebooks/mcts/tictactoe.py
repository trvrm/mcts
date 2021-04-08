from typing import Optional, Dict
import numpy as np
import time
from random import choice
from collections import Counter

from dataclasses import dataclass


from .common import Result, Player, other_player


class Illegal(Exception):
    pass


class GameOver(Exception):
    pass


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


# We need at least an implicit guarantee that State is immutable
class State:
    def __init__(
        self,
        m: Optional[np.ndarray] = None,
        player: Optional[Player] = None,
        command: Optional[Command] = None,
    ) -> None:
        if m is None:
            assert player is None
            self.player = Player.ONE
            self._m = np.array([[0 for i in range(SIZE)] for j in range(SIZE)])
            self.command = None
        else:
            assert player is not None
            assert command is not None
            self._m = m
            self.player = player

            # The command that led to this state
            self.command = command

        self.result = _result(self._m)

        self.commands = [
            Command(j, i)
            for j in range(SIZE)
            for i in range(SIZE)
            if self._m[j, i] == 0
        ]

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
        # check legality
        if command not in self.commands:
            raise Illegal()

        if self._m[command.j, command.i] != 0:
            raise Illegal()

        m = self._m.copy()
        v = {Player.ONE: 1, Player.TWO: -1}[self.player]
        m[command.j, command.i] = v
        return State(m, other_player(self.player), command)

    def playout(self) -> Result:
        state = self
        while state.result == Result.INPROGRESS:
            command = choice(state.commands)
            state = state.apply(command)
        return state.result


def do_playouts(state: State, seconds: float) -> Counter[str]:
    c: Counter[str] = Counter()
    end = seconds + time.time()
    assert seconds > 0
    while time.time() < end:
        result = state.playout()
        c[result.name] += 1
    return c


# we don't need the rest for MCTS, but is useful for comparison


def evaluate(state: State, player: Player, seconds: float) -> float:
    c = do_playouts(state, seconds)
    playouts = sum(c.values())

    if player == Player.ONE:
        wins = c["PLAYER1"]
    elif player == Player.TWO:
        wins = c["PLAYER2"]
    else:
        assert 0
    return wins / playouts


def get_command_scores(state: State, seconds: float) -> Dict[Command, float]:

    assert len(state.commands) > 0
    per_command = seconds / len(state.commands)
    return {
        command: evaluate(state.apply(command), state.player, per_command)
        for command in state.commands
    }


def pick_move_by_playouts(state: State, seconds: float) -> Command:
    command_scores = get_command_scores(state, seconds)
    # return highest scoring command
    return max(command_scores.items(), key=lambda cmd_score: cmd_score[1])[0]
