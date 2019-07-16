"""
Simple shell-like interface to a TFEboard
"""

import argparse

from tfe_base import TFEBoard

def get_args():
    """
    Parse arg
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-ansi", dest="ansi", action="store_false",
            help="Don't use ansi codes to colour squares")
    parser.add_argument("n", type=int, nargs="?", default=4,
            help="Board size")
    return parser.parse_args()

MOVES = {"H": TFEBoard.left,
         "J": TFEBoard.down,
         "K": TFEBoard.up,
         "L": TFEBoard.right}

def play(n, ansi):
    """
    Play a round of 2048
    """
    board = TFEBoard(n)
    while True:
        print("Score: {}".format(board.score))
        print(board.w_fmt(ansi=ansi))
        move = input().upper()
        if move in MOVES:
            MOVES[move](board)
        else:
            print("invalid move: {!r}".format(move))

if __name__ == "__main__":
    args = get_args()
    play(args.n, args.ansi)
