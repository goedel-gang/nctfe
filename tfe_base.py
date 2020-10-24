"""
Base class for 2048. UI implementation is left to the caller, although this
class does provide some string formatting.
"""

from itertools import repeat, chain, starmap
from random import choice, random
from functools import lru_cache

# the xterm-256 type colours to be used in SGR escapes to colour tiles.
ANSI_VALS = [
        (0, 15), (226, 0), (46, 0), (208, 15), (33, 15), (135, 15), (130, 15),
        (125, 15), (123, 0), (120, 0), (52, 15), (160, 15), (214, 0), (53, 15),
        (17, 15), (87, 0), (255, 0), *((i, 0) for i in range(1, 16))
        ]

ANSI_ESCS = list(starmap("\x1b[48;5;{}m\x1b[38;5;{}m".format, ANSI_VALS))

def ilog(n, base=2):
    """
    Simple iterative integer logarithm.
    Even though there's a loop, this is linear in the number of bits of the
    input, so basically pretty fast
    """
    exp = 0
    while n > 0:
        n //= base
        exp += 1
    return exp

# cached to speed it up
@lru_cache()
def make_templ(n, cell_width):
    """
    Make a template for str.format for a board, in the most ghastly one-liner I
    could possibly think of.
    """
    return ("{}\n".format(
                "{{}}{{:{}}}{{}}".format(cell_width)
                    .join(repeat("|", (n + 1))))
                        .join(repeat("{}\n".format(("-" * cell_width)
                            .join("+" * (n + 1))), n + 1)))

class GameOver(Exception):
    """
    Exception to raise when a player reaches game-over
    """
    pass

class TFEBoard:
    """
    A 2048 board
    """
    def __init__(self, n):
        self.n = n
        self.score = 0
        # safe because 0 is immutable
        self.squares = [0] * n ** 2
        # sequences of squares to meld, represented as iterables of integers,
        # starting from the "wall" against which to send.
        self.up_seq = [range(i, n ** 2, n) for i in range(n)]
        # [::-1] is permissible because range slicing is f a s t
        self.down_seq = [r[::-1] for r in self.up_seq]
        self.left_seq = [range(i, i + n) for i in range(0, n * n, n)]
        self.right_seq = [r[::-1] for r in self.left_seq]
        for _ in range(2):
            self.add_random()

    def add_random(self):
        """
        Randomly insert a new tile, with 90% chance of being a 2, and 10% chance
        of being a 4.
        """
        available = [ind for ind, i in enumerate(self.squares) if i == 0]
        # currently this isn't actually ever reached.
        if not available:
            raise GameOver("The board is full.")
        loc = choice(available)
        if random() < 0.9:
            self.squares[loc] = 2
        else:
            self.squares[loc] = 4

    def sift(self, seq):
        """
        Sift squares down the indices in `seq`.
        """
        # flag to track if anything changed
        any_moved = False
        for ind, i in enumerate(seq):
            prev_i = i
            sift_square = self.squares[i]
            if sift_square != 0:
                # even though this looks terrible, it should be basically really
                # fast because it's all implemented with range arithmetic (in C)
                for step_i in seq[:ind][::-1]:
                    target_square = self.squares[step_i]
                    if target_square <= 0:
                        any_moved = True
                        self.squares[step_i] = sift_square
                        self.squares[prev_i] = 0
                        if target_square == -1:
                            break
                    else:
                        if target_square == sift_square:
                            any_moved = True
                            self.squares[step_i] = sift_square * 2
                            self.score += sift_square * 2
                            # -1 here flags that this square has already merged
                            self.squares[prev_i] = -1
                        break
                    prev_i = step_i
        # clean up -1s
        for i in seq:
            if self.squares[i] == -1:
                self.squares[i] = 0
        return any_moved

    def sift_all(self, seqs):
        """
        Sift for each seq in seqs, and then add another random square. Basically
        functions as a "turn".
        """
        # Check if anything moved. Could be done with a list comprehension and
        # any(), but that's a waste of space and I'm not going to unironically
        # use a deque here.
        any_moved = False
        for seq in seqs:
            # Make sure not to short-circuit
            any_moved = self.sift(seq) or any_moved
        # only add another if the move had some effect
        if any_moved:
            self.add_random()
        return any_moved

    def up(self):
        """
        Sift up
        """
        return self.sift_all(self.up_seq)

    def down(self):
        """
        Sift down
        """
        return self.sift_all(self.down_seq)

    def left(self):
        """
        Sift left
        """
        return self.sift_all(self.left_seq)

    def right(self):
        """
        Sift right
        """
        return self.sift_all(self.right_seq)

    def w_fmt(self, cell_width=7, ansi=False, hide_z=True):
        """
        Separate method because it supports various other flags
        """
        return (make_templ(self.n, cell_width)
                    .format(
                        *chain.from_iterable(
                                (ANSI_ESCS[min(ilog(s), len(ANSI_ESCS) - 1)]
                                    if ansi else '',
                                 s or ' ' if hide_z else s,
                                 "\x1b[0m" if ansi else '')
                                for s in self.squares)))

    def __str__(self):
        """
        String format as a nice grid.
        """
        return self.w_fmt()

    def __repr__(self):
        """
        Very bare representation.
        """
        return "TFEBoard({})".format(self.n)

if __name__ == "__main__":
    from time import sleep
    board = TFEBoard(5)
    for regions in (board.up_seq, board.down_seq,
                    board.left_seq, board.right_seq):
        for region in regions:
            for ind, i in enumerate(region, 1):
                board.squares[i] = ind
        print(board)
        board.squares = [0] * len(board.squares)
    for _ in range(10):
        board.add_random()
    for direc in board.up, board.down, board.left, board.right:
        print(board.w_fmt(ansi=True))
        direc()
        sleep(1)
    print(board.w_fmt(ansi=True))
