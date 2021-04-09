from enum import Enum

# maybe this should be win/draw/inprogress, with a separate
# winner field that can be none?
class Result(str, Enum):
    PLAYER1 = "PLAYER 1 WINS"
    PLAYER2 = "PLAYER 2 WINS"
    DRAW = "DRAW"
    INPROGRESS = "IN PROGRESS"

    def __repr__(self) -> str:
        return self.name


class Player(str, Enum):
    ONE = "ONE"
    TWO = "TWO"

    def __repr__(self) -> str:
        return self.name


def other_player(player: Player) -> Player:
    return {Player.ONE: Player.TWO, Player.TWO: Player.ONE}[player]
