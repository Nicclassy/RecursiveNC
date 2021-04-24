import os

from src.game import Game
from src.grid import DIMENSION

os.chdir(os.path.dirname(__file__))

game = Game(DIMENSION)
while game.running:
    game.current_menu.display_menu()
    game.play_game()
