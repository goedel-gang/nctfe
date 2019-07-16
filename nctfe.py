"""
NCurses 2048
"""

import curses
import argparse

from tfe_base import TFEBoard, ANSI_VALS, ilog

def get_args():
    """
    Parse arg
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-arrows", action="store_true",
            help="Allow using the arrow keys. Not recommended for cool people")
    parser.add_argument("n", type=int, nargs="?", default=4,
            help="Board size")
    return parser.parse_args()

def ncfmt(y, x, stdscr, board, cell_width=7):
    """
    Printing a board with curses primitives
    """
    for i in range(board.n):
        stdscr.addstr(y + 2 * i, x, ("-" * cell_width)
                                        .join("+" * (board.n + 1)))
        stdscr.addstr(y + 2 * i + 1, x, "|")
        for j in range(board.n):
            square = board.squares[i * board.n + j]
            if square:
                stdscr.addstr(y + 2 * i + 1, x + 1 + (cell_width + 1) * j,
                              "{:{}}".format(square, cell_width),
                              curses.color_pair(
                                    min(ilog(square), len(ANSI_VALS))))
                stdscr.addstr(y + 2 * i + 1, x + (cell_width + 1) * (j + 1),
                              "|")
            else:
                stdscr.addstr(y + 2 * i + 1, x + 1 + (cell_width + 1) * j,
                              "{}|".format(" " * cell_width))
    stdscr.addstr(y + 2 * board.n, x, ("-" * cell_width)
                                        .join("+" * (board.n + 1)))

def main(stdscr, n, allow_arrows):
    """
    The main function, to be wrapped by curses
    """
    curses.curs_set(False)
    board = TFEBoard(n)
    move_map = {}
    for move, action, key in zip("HJKL", [board.left, board.down,
                                          board.up, board.right],
                                         [curses.KEY_LEFT,
                                          curses.KEY_DOWN,
                                          curses.KEY_UP,
                                          curses.KEY_RIGHT]):
        move_map[ord(move)] = action
        move_map[ord(move.lower())] = action
        if allow_arrows:
            move_map[key] = action
    for ind, i in enumerate(ANSI_VALS, 1):
            curses.init_pair(ind, *reversed(i))
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Score: {}".format(board.score))
        ncfmt(1, 0, stdscr, board)
        c = stdscr.getch()
        if c in {ord("q"), ord("Q")}:
            break
        elif c in move_map:
            move_map[c]()
        stdscr.refresh()

if __name__ == "__main__":
    args = get_args()
    curses.wrapper(lambda stdscr: main(stdscr, **vars(args)))
