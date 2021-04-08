import time
from .node import Node, mcts
from .common import Result
from .tictactoe import State, Command


def get_command() -> Command:
    s = input("COMMAND> ")
    j, i = s.strip().split(" ")
    return Command(int(j), int(i))


def apply_command(root: Node, command: Command) -> Node:
    # Either get child node that has this command or
    # create a new root
    for child in root.children:
        if child.state.command == command:
            return child
    else:
        state = root.state.apply(command)

        # Entirely new tree: no parent, no parent command etc.
        return Node(state)


def pick_move(root: Node, seconds: float) -> Command:
    end = time.time() + seconds
    while time.time() < end:
        mcts(root)

    return root.best().state.command


def main() -> None:

    s = State()
    root = Node(s)

    print(root.state)
    while root.state.result == Result.INPROGRESS:
        human = get_command()

        root = apply_command(root, human)

        if root.state.result == Result.INPROGRESS:
            computer = pick_move(root, 0.5)
            root = apply_command(root, computer)
        print(root.state)
        print("")
    print(f"GAME OVER, result is {root.state.result}")

    # fails as expected :-)
    # n2=Node("something wrong")
