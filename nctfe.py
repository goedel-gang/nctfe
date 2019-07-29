"""
2048: NCurses + Vi edition
"""

import curses
import curses.ascii
import argparse

from tfe_base import TFEBoard, ANSI_VALS, ilog

class DefaultSentinel:
    """
    Little class to store default values, but also allow testing against its ID
    to see if an actual argument was given.
    """
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return str(self.val)

def get_args():
    """
    Parse arg
    """
    chunk_sentinel = DefaultSentinel(1000)
    parser = argparse.ArgumentParser(description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--allow-arrows", action="store_true",
            help="Allow using the arrow keys. Not recommended for cool people")
    parser.add_argument("--auto", action="store_true",
            help="Play automatically, by trying to go left, up, right, down")
    parser.add_argument("--auto-chunk", type=int, default=chunk_sentinel,
            help="Number of game steps to do in between refreshing the screen")
    parser.add_argument("n", type=int, nargs="?", default=4,
            help="Board size")
    args = parser.parse_args()
    if args.auto_chunk is not chunk_sentinel and not args.auto:
        parser.error("--auto-chunk can only be used with --auto")
    if args.auto_chunk is chunk_sentinel:
        args.auto_chunk = args.auto_chunk.val
    return args

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
                stdscr.addstr("{:{}}".format(square, cell_width),
                              curses.color_pair(
                                    min(ilog(square), len(ANSI_VALS))))
                stdscr.addstr("|")
            else:
                stdscr.addstr("{}|".format(" " * cell_width))
    stdscr.addstr(y + 2 * board.n, x, ("-" * cell_width)
                                        .join("+" * (board.n + 1)))

def main(stdscr, n, allow_arrows, auto, auto_chunk):
    """
    The main function, to be wrapped by curses
    """
    curses.curs_set(False)
    if auto:
        stdscr.nodelay(True)
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
        stdscr.refresh()
        stdscr.erase()
        stdscr.addstr(0, 0, "Score: {}".format(board.score))
        ncfmt(1, 0, stdscr, board)
        c = stdscr.getch()
        if c in {ord("q"), ord("Q"), curses.ascii.ESC}:
            break
        # automatically redraw after window resize
        elif c in {curses.KEY_RESIZE, curses.ascii.ctrl(ord("L"))}:
            stdscr.clear()
        elif auto:
            i_want_to_break_free = False
            for _ in range(auto_chunk):
                for move in [board.left, board.up, board.right, board.down]:
                    if move():
                        break
                else:
                    i_want_to_break_free = True
                    break
            if i_want_to_break_free:
                break
        else:
            if c in move_map:
                move_map[c]()
    if auto:
        stdscr.nodelay(False)
    stdscr.erase()
    stdscr.addstr(0, 0, "GAME OVER: {}".format(board.score),
                  curses.color_pair(1))
    ncfmt(1, 0, stdscr, board)
    while True:
        if stdscr.getch() in {ord("q"), ord("Q"), curses.ascii.ESC}:
            break

if __name__ == "__main__":
    args = get_args()
    curses.wrapper(lambda stdscr: main(stdscr, **vars(args)))
