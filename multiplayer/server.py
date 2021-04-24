import os

from src.game import Game
from src.grid import DIMENSION

os.chdir(os.path.dirname(__file__))

game = Game(DIMENSION)
game.playing = True
game.current_menu.run_display = False
game.current_menu = game.multiplayer_menu
game.current_menu.state = "Host"
game.START_KEY = True
while game.running:
    game.current_menu.display_menu()
    game.play_game()
