__all__ = ["Game"]

import sys
import os
import pygame
from src.menu import MainMenu, OptionsMenu, PostGameMenu, ColourMenu
from src.grid import Grid, DIMENSION, ASSETS_PATH, generate_highlighted_images


class Game:

    SHORT_TO_LONG = {
        "X": "Crosses",
        "O": "Noughts",
    }

    def __init__(self, dimension: float):
        """Initializes pygame and the instance of the game that is created."""
        self.H_IMAGES = {
            'X': pygame.image.load(os.path.join(ASSETS_PATH, 'CX.png')),
            'O': pygame.image.load(os.path.join(ASSETS_PATH, 'CO.png')),
        }
        pygame.init()
        pygame.display.set_caption('Recursive Noughts and Crosses')
        pygame.display.set_icon(pygame.image.load(os.path.join(ASSETS_PATH, 'icon.png')))
        pygame.mouse.set_visible(False)
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        # variables which store the state of a key
        self.RIGHT_KEY, self.LEFT_KEY = False, False
        self.Y_OFFSET = DIMENSION / 2
        self.BLACK, self.WHITE = (0, 0, 0), (255, 255, 255)
        self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT = int(dimension * 3), int(dimension * 3 + self.Y_OFFSET)
        self.display = pygame.Surface(DISPLAY_VALUES := (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        self.window = pygame.display.set_mode(DISPLAY_VALUES)
        self.font_name = pygame.font.get_default_font()
        self.last_winner = None
        self.highlight = (255, 0, 0)
        self.main_menu = MainMenu(self)
        self.options_menu = OptionsMenu(self)
        self.post_game_menu = PostGameMenu(self)
        self.colour_menu = ColourMenu(self)
        self.current_menu = self.main_menu
        self.generate_highlighted_images()
        self.load_images()

    def load_images(self):
        self.H_IMAGES = {
            'X': pygame.image.load(os.path.join(ASSETS_PATH, 'CX.png')),
            'O': pygame.image.load(os.path.join(ASSETS_PATH, 'CO.png')),
        }

    def play_game(self):
        self.check_events()
        if self.playing:
            self.game_loop()

    def game_loop(self):
        """The main event loop which runs while the game is being played."""
        # set_values = {
        #     (0, 2): [(0, 0), (0, 1), (0, 2)],
        #     (1, 1): [(0, 0), (0, 1), (0, 2)],
        #     (2, 0): [(0, 0), (0, 1)],
        # }
        # grid.set_values('X', set_values)
        pygame.mouse.set_visible(True)
        grid = Grid(Grid)
        player, current, previous, played = 'X', None, None, True
        play, win, draw = False, False, False
        turn_str = "' turn"
        status_message = Game.SHORT_TO_LONG[player] + turn_str
        while self.playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.playing = False
                        self.current_menu = self.main_menu
                        self.reset_keys()
                        return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]:
                        mouse_position = pygame.mouse.get_pos()
                        large_y, small_y = Grid.get_grid_positions(mouse_position[1] - 100)
                        large_x, small_x = Grid.get_grid_positions(mouse_position[0])
                        if (inner_grid := grid[large_y][large_x])[small_y][small_x] is not None:
                            status_message = "This square is already taken"
                        elif current is None:
                            play = True
                        else:
                            if inner_grid.played:
                                status_message = "This grid has already been played"
                            elif current == (large_y, large_x):
                                play = True
                            else:
                                status_message = "You cannot play in this square"

                        if play:
                            grid[large_y][large_x][small_y][small_x] = player
                            previous, = player
                            player = Grid.switch_player(player)
                            play = False
                            status_message = Game.SHORT_TO_LONG[player] + turn_str
                            if not grid[large_y][large_x].win(previous):
                                grid[large_y][large_x].draw()
                            if win := grid.win(previous, winning_combination=True) or grid.draw():
                                played = True
                            elif not inner_grid.played and not grid[small_y][small_x].played:
                                current = (small_y, small_x)
                            else:
                                current = None

            self.display.fill(self.BLACK)
            self.draw_top_text(status_message)
            self.window.blit(self.display, (0, 0))
            grid.draw_grid(self.window)

            if played and win:
                status_message = Game.SHORT_TO_LONG[previous] + " is the winner!"
                Grid.draw_winner(Grid.switch_player(player), win, self.window, self.H_IMAGES)
            elif played and draw:
                status_message = "Draw!"
            if played and (draw or win):
                pygame.display.update()
                pygame.time.delay(5000)
                pygame.mouse.set_visible(False)
                self.playing = False
                self.post_game_menu.message = status_message
                self.current_menu = self.post_game_menu
                self.reset_keys()
                break
            pygame.display.update()

    def check_events(self):
        """Gets data from the event loop and sets the values of the key state variables"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                self.current_menu.run_display = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE:
                    self.BACK_KEY = True
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.UP_KEY = True
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.RIGHT_KEY = True
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.LEFT_KEY = True

    def reset_keys(self):
        """Resets all the key state variables to False (not pressed)."""
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.LEFT_KEY, self.RIGHT_KEY = \
            False, False, False, False, False, False

    def draw_text(self, text: str, size: int, x: int, y: int, /):
        """Draws text to the game's display."""
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.highlight if y == self.current_menu.cursor_rect.y else self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display.blit(text_surface, text_rect)

    def draw_top_text(self, text: str):
        """Draws text to the top of the screen. Used during the game to provide status messages to the user."""
        self.draw_text(text, 40, int(self.DISPLAY_WIDTH / 2), 50)

    def generate_highlighted_images(self):
        """
        Generates the highlighted noughts and crosses.
        Used when the game is initialized and when the user changes the highlight colour.
        """
        if os.path.exists(os.path.join(ASSETS_PATH, 'CX.png')):
            os.remove(os.path.join(ASSETS_PATH, 'CX.png'))
            os.remove(os.path.join(ASSETS_PATH, 'CO.png'))
        generate_highlighted_images(self.highlight)
