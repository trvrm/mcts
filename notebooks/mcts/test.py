import time
from .node import Node, mcts
from .common import Result
from . import tictactoe
from .tictactoe import State, Command


def get_command(state) -> Command:
    while True:
        try:
            s = input("COMMAND (x,y)> ")
            x, y = s.strip().split(" ")
            command = Command(int(y) - 1, int(x) - 1)
        except Exception as e:
            print(f"Couldn't parse command: {e}")
            continue
        if command in state.commands:
            return command
        else:
            print("Illegal command")


def apply_command(root: Node, command: Command) -> Node:
    """
    Either get the child node that has this command or
    create a new root
    """

    if command in root.children:
        return root.children[command]

    else:
        # This was never explored, create a new node
        # from scratch
        return Node(root.state.apply(command))


def pick_move(root: Node, seconds: float) -> Command:
    print("Computer thinking...")
    end = time.time() + seconds
    while time.time() < end:
        mcts(root)

    print(root)

    print("Best line:", root.best_line())
    return root.best()


def main() -> None:

    s = tictactoe.State()
    root: Node[tictactoe.State] = Node(s)

    print(root.state)
    print("")
    while root.state.result == Result.INPROGRESS:

        human = get_command(root.state)
        root = apply_command(root, human)
        print(root.state)
        print("")
        if root.state.result == Result.INPROGRESS:
            computer = pick_move(root, 1.5)
            root = apply_command(root, computer)
        print(root.state)
        print("")
    print(f"GAME OVER, result is {root.state.result}")
