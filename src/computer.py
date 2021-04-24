"""
Computer AI for single player
"""

import copy
from typing import Optional
from src.grid import Grid, Coordinate, WIN_COMBINATIONS

__all__ = ["ComputerAI"]


class ComputerAI:

    __slots__ = 'player', '_current_grid'

    def __init__(self, player: str = 'O', current_grid: Optional[Coordinate] = None):
        self.player = player
        self._current_grid = current_grid

    def get_status(self):
        ...
        #  -1, occupied by player, 0, free, 1 occupied by comp

    def find_win(self, grid: Grid):
        for combination in WIN_COMBINATIONS:
            a, b, c = combination


    def check_for_win(self, grid: Grid, outer: Coordinate, inner: Optional[Coordinate] = None) -> bool:
        "Requires depth"
        # grid = copy.deepcopy(grid)
        # grid.set_coordinates(outer, inner := self._current_grid, self.player)
        # return grid.win(self.player)
        ...

    def set_current_grid(self, coordinate: Optional[Coordinate] = None):
        self._current_grid = coordinate

    def test_for_fork(self, grid: Grid, outer: Coordinate, inner: Coordinate, depth: Optional[int] = 2) -> bool:
        grid = copy.deepcopy(grid)
        grid.set_coordinates(outer, inner, self.player)
        iy, ix = self._current_grid
        winning_moves = 0

        if depth == 1:
            for y in range(3):
                for x in range(3):
                    if self.check_for_win(grid, outer, inner) and grid[y][x].winner == self.player:
                        winning_moves += 1
        elif depth == 2:
            for y in range(3):
                for x in range(3):
                    if self.check_for_win(grid, outer, inner) and grid[y][x][iy][ix] is None:
                        winning_moves += 1
        return winning_moves >= 2





# def testForkMove(b, mark, i):
#     # Determines if a move opens up a fork
#     bCopy = getBoardCopy(b)
#     bCopy[i] = mark
#     winningMoves = 0
#     for j in range(0, 9):
#         if testWinMove(bCopy, mark, j) and bCopy[j] == ' ':
#             winningMoves += 1
#     return winningMoves >= 2
