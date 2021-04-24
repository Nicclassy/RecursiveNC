__all__ = ["Grid", "IMAGES", "DIMENSION", "INNER_DIMENSION"]
__author__ = "Luca Napoli"
__version__ = "1.1"

import sys
import os
from typing import Union, Optional, Any, NamedTuple, Tuple, List
from PIL import Image  # type: ignore
import pygame

folder_dir = os.path.dirname(os.path.abspath(__file__))
# Given this file is run in a virtual environment, an AssertionError is unlikely to be raised
assert os.getcwd() == folder_dir, f"Current directory is {os.getcwd()}, should be {folder_dir}"

Number = Union[int, float]
IntTuple = Tuple[int, int]
Lines = List[Tuple[IntTuple, ...]]


class Coordinate(NamedTuple):
    x: Number
    y: Number


Combination = Tuple[IntTuple, IntTuple, IntTuple]


def _add_to_tuple(tuple_: Tuple[Number, Number], x: Number, y: Number, /) -> Coordinate:
    return Coordinate(tuple_[0] + x, tuple_[1] + y)


def _image_resize(name: str, directory: str, resize_values: IntTuple):
    image = Image.open(directory)
    new_image = image.resize(resize_values, Image.ANTIALIAS)
    new_image.save(os.path.dirname(sys.argv[0]) + '/assets/' + name + '.png')


def _generate_small_images(dimension: int):
    _image_resize('IX', cross_path, (dimension, dimension))
    _image_resize('IO', nought_path, (dimension, dimension))


def _generate_highlighted_images(colour: Tuple[int, int, int]):
    def _highlight_image(filename: str):
        img = Image.open(filename)
        white = (255,) * 3

        for x in range(img.width):
            for y in range(img.height):
                pixel = img.getpixel((x, y))
                if pixel[:-1] == white:
                    img.putpixel((x, y), colour)

        img.save('C' + filename)

    _highlight_image('X.png')
    _highlight_image('O.png')


def _add_offset_to_iter(iterable: Tuple[IntTuple, ...]) -> Tuple[IntTuple, ...]:
    return tuple((int(coordinate[0]), int(coordinate[1] + Y_OFFSET)) for coordinate in iterable)


def apply_y_offset(lines: Lines) -> Lines:
    return list(map(_add_offset_to_iter, lines))


SMALL_IMAGES = {
    'X': pygame.image.load(os.path.join(folder_dir, 'assets', 'IX.png')),
    'O': pygame.image.load(os.path.join(folder_dir, 'assets', 'IO.png')),
}

cross_path = os.path.join("assets", "X.png")
nought_path = os.path.join("assets", "O.png")

IMAGES = {
    'X': pygame.image.load(cross_path),
    'O': pygame.image.load(nought_path),
}

OFFSET = 10
DIMENSION = 200
Y_OFFSET = int(DIMENSION / 2)
# (x + offset, y), (x - offset, y)
GRID_LINES = [((0 + OFFSET, DIMENSION), (DIMENSION * 3 - OFFSET, DIMENSION)),
              ((0 + OFFSET, DIMENSION * 2), (DIMENSION * 3 - OFFSET, DIMENSION * 2)),
              ((DIMENSION, 0 + OFFSET), (DIMENSION, DIMENSION * 3 - OFFSET)),
              ((DIMENSION * 2, 0 + OFFSET), (DIMENSION * 2, DIMENSION * 3 - OFFSET))
              ]
INNER_OFFSET = OFFSET * 1.5
INNER_DIMENSION = DIMENSION / 3
INNER_GRID_LINES = [
    ((0 + INNER_OFFSET, INNER_DIMENSION), (DIMENSION - INNER_OFFSET, INNER_DIMENSION)),
    ((0 + INNER_OFFSET, INNER_DIMENSION * 2), (DIMENSION - INNER_OFFSET, INNER_DIMENSION * 2)),
    ((INNER_DIMENSION, 0 + INNER_OFFSET), (INNER_DIMENSION, DIMENSION - INNER_OFFSET)),
    ((INNER_DIMENSION * 2, 0 + INNER_OFFSET), (INNER_DIMENSION * 2, DIMENSION - INNER_OFFSET))
]
WIN_COMBINATIONS = [
    ((0, 0), (0, 1), (0, 2)),
    ((0, 0), (1, 0), (2, 0)),
    ((1, 0), (1, 1), (1, 2)),
    ((0, 1), (1, 1), (2, 1)),
    ((2, 0), (2, 1), (2, 2)),
    ((0, 2), (1, 2), (2, 2)),
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0))
]


class Grid:
    """
    Initializes a two-dimensional array with the values of each row set to value.
    This value can either be a NoneType or a Grid object (for recursively creating child grids).
    The parent grid is a four-dimensional array.

    Attributes
    ----------
    played : bool
        indicates whether or not a grid has been played. A grid is played if
        a draw or win is achieved
    winner : str | None
        the winner of the grid
    is_child : bool
        indicates whether or not a Grid object is a child of another Grid object
    """

    __slots__ = "_array", "played", "winner", "is_child"

    def __init__(self, value: Optional[Any] = None, /):
        self._array: list = [[value() if value is not None else None for _ in range(3)] for _ in range(3)]
        self.played: bool = False
        self.winner: Union[None, str] = None
        self.is_child: bool = True if value is None else False

    def __iter__(self):
        """Returns the grid as an iterator."""
        return iter(self._array)

    def __repr__(self):
        """Returns repr() of the grid"""
        return repr(self._array)

    def __len__(self):
        """Returns the length of the grid"""
        return len(self._array)

    def __getitem__(self, index: int):
        """Returns the element at position index of the grid"""
        return self._array[index]

    def __setitem__(self, index: int, value: str):
        """Sets the element of grid at position index to value"""
        self._array[index] = value

    @staticmethod
    def get_value(value: Any) -> Union[bool, str, None]:
        """Returns the winner of the value if it is an instance of the Grid class.
        If not, the function returns the value.
        This function allows the win and draw functions to be called both on a child grid and the parent."""
        if type(value) is Grid:
            return value.winner
        else:
            return value

    def win(self, value: Union[str, None], /, *, winning_combination: Optional[bool] = False) -> Union[Combination, bool]:  # syntax changes to bool | list in 3.10
        """
        Evaluates whether or not a win can be achieved in a grid.
        The value can be either 'X' or 'O', and the returned winning combination is 
        returned to show which combination won the grid (using a colour).
        """
        for combination in WIN_COMBINATIONS:
            if all(Grid.get_value(self[position[0]][position[1]]) == value for position in combination):
                self.played = True
                self.winner = value
                return combination if winning_combination else True
        else:
            return False

    def draw(self) -> bool:
        """
        Evaluates whether or not a grid has been drawn. A grid is drawn if all squares
        are occupied.
        """
        if all(Grid.get_value(value) for row in self for value in row):
            self.played = True
            return True
        else:
            return False

    def draw_grid(self, screen: pygame.Surface):
        """Draws the grid on the pygame interface. Called on the parent grid."""
        for line in GRID_LINES:
            pygame.draw.line(screen, (200, 200, 200), line[0],
                             line[1], 2)

        for y in range(len(self)):
            y_pos = INNER_DIMENSION * y
            for x in range(len(self[y])):
                x_pos = INNER_DIMENSION * x
                if not (inner := self[y][x]).played:
                    x_shift, y_shift = x * DIMENSION / 1.5, y * DIMENSION / 1.5
                    for line in INNER_GRID_LINES:
                        pygame.draw.line(screen, (200, 200, 200), _add_to_tuple(line[0], x_pos + x_shift, y_pos + y_shift),
                                         _add_to_tuple(line[1], x_pos + x_shift, y_pos + y_shift), 2)
                    for iy in range(len(inner)):
                        for ix in range(len(inner[iy])):
                            if (inner_position := inner[iy][ix]) is not None:
                                screen.blit(SMALL_IMAGES[inner_position], (
                                    x * DIMENSION + ix * INNER_DIMENSION, y * DIMENSION + iy * INNER_DIMENSION))
                else:
                    if inner.winner is not None:
                        screen.blit(IMAGES[inner.winner], (x * DIMENSION, y * DIMENSION))

    # def draw_winner(self, winning_combination: Combination, screen: pygame.Surface):
    #     for coordinate in winning_combination:
    #         y, x = coordinate
    #         screen.blit(self[y][x])

    @staticmethod
    def get_grid_positions(number: Number, /) -> Coordinate:
        large_val, remainder = divmod(number, DIMENSION)
        small_val = remainder // INNER_DIMENSION
        return Coordinate(int(large_val), int(small_val))

    @staticmethod
    def switch_player(current_player: str, /) -> str:
        if current_player == 'X':
            return 'O'
        else:
            return 'X'

    @staticmethod
    def print_grid(grid: list):
        """Prints a formatted version of a grid (passed in as a list) to the console."""
        top_row, mid_row, bottom_row = " ─ ┬", " ─ ┼", " ─ ┴"
        print(f"┌{top_row * 2} ─ ┐")
        for count, row in enumerate(grid):
            print(("| {} " + ("│ {} " * 2) + "│").format(*map(lambda value: ' ' if value is None else value, row)))
            if count != 2:
                print(f"├{mid_row * 2} ─ ┤")
        print(f"└{bottom_row * 2} ─ ┘")

    def print_all_grids(self):
        """Prints all grids within the parent grid with their index and grid number."""
        grid_number = 1
        for y, row in enumerate(self):
            for x, grid in enumerate(row):
                print("Grid", grid_number, (y, x))
                Grid.print_grid(grid)
                grid_number += 1
