__all__ = ["Game"]

import sys
import os
import socket
import threading
import pygame
import pygame.cursors
from src.menu import MainMenu, OptionsMenu, PostGameMenu, ColourMenu, MultiplayerMenu, TutorialMenu
from src.grid import Grid, DIMENSION, ASSETS_PATH, generate_highlighted_images


class Game:
    SHORT_TO_LONG = {
        "X": "Crosses",
        "O": "Noughts",
    }

    def __init__(self, dimension: float):
        """Initializes pygame and the instance of the game that is created."""
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
        self.font_name = pygame.font.match_font('comicsansms')
        self.last_winner = None
        self.highlight = (255, 0, 0)
        self.main_menu = MainMenu(self)
        self.options_menu = OptionsMenu(self)
        self.post_game_menu = PostGameMenu(self)
        self.colour_menu = ColourMenu(self)
        self.multiplayer_menu = MultiplayerMenu(self)
        self.tutorial_menu = TutorialMenu(self)
        self.current_menu = self.main_menu
        self.generate_highlighted_images()
        self.H_IMAGES = {
            'X': pygame.image.load(os.path.join(ASSETS_PATH, 'CX.png')),
            'O': pygame.image.load(os.path.join(ASSETS_PATH, 'CO.png')),
        }

    def play_game(self):
        self.check_events()
        if self.playing:
            if self.current_menu.state == "Play":
                self.game_loop()
            elif self.current_menu.state == "Host":
                self.server_multiplayer()
            elif self.current_menu.state == "Join":
                self.client_multiplayer()

    def game_loop(self):
        """The main event loop which runs while the game is being played."""
        pygame.mouse.set_visible(True)
        grid = Grid(Grid)
        player, current, previous, played = 'X', None, None, False
        play, win, draw = False, False, False
        turn_str = "' turn"
        status_message = Game.SHORT_TO_LONG[player] + turn_str
        clock = pygame.time.Clock()
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)
        while self.playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                        self.playing = False
                        self.current_menu = self.main_menu
                        self.reset_keys()
                        pygame.mouse.set_visible(False)
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
                            if previous == 'X':
                                pygame.mouse.set_cursor(*pygame.cursors.diamond)
                            else:
                                pygame.mouse.set_cursor(*pygame.cursors.broken_x)
                            player = Grid.switch_player(player)
                            play = False
                            status_message = Game.SHORT_TO_LONG[player] + turn_str
                            if not grid[large_y][large_x].win(previous):
                                grid[large_y][large_x].draw()
                            if win := grid.win(previous, winning_combination=True):
                                status_message = Game.SHORT_TO_LONG[previous] + " is the winner!"
                                played = True
                            elif grid.draw():
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
                Grid.draw_winner(Grid.switch_player(player), win, self.window, self.H_IMAGES)
            elif played and draw:
                status_message = "Draw!"
            if played:
                pygame.display.update()
                pygame.time.delay(5000)
                pygame.mouse.set_visible(False)
                self.playing = False
                self.post_game_menu.message = status_message
                self.current_menu = self.post_game_menu
                self.reset_keys()
                break
            pygame.display.update()
            clock.tick(60)

    def server_multiplayer(self):
        host = '127.0.0.1'
        port = 65432
        connection_established = False
        connection, address = None, None

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((host, port))
            sock.listen(1)
        except OSError:
            self.display.fill(self.BLACK)
            self.draw_text("A game is already being hosted", 30, int(self.DISPLAY_WIDTH / 2),
                           int(self.DISPLAY_HEIGHT / 2))
            self.window.blit(self.display, (0, 0))
            pygame.display.flip()
            self.current_menu = self.main_menu
            self.playing = False
            pygame.time.delay(3000)
            return

        def receive_data():
            nonlocal turn, player, status_message, current
            while True:
                data = connection.recv(1024).decode()
                y, x, iy, ix, playing, current = data.split('-')
                y, x, iy, ix, current = int(y), int(x), int(iy), int(ix), eval(current)
                grid[y][x][iy][ix] = 'O'
                turn = True
                if not eval(playing):
                    self.playing = False
                player = 'X'
                status_message = Game.SHORT_TO_LONG[player] + turn_str
                grid[y][x].win('O')
                grid[y][x].draw()

        def await_connection():
            nonlocal connection_established, connection, address, status_message
            connection, address = sock.accept()  # wait for a connection; blocking call
            status_message = 'Client has connected'
            connection_established = True
            receive_data()

        thread = threading.Thread(target=await_connection)
        thread.daemon = True
        thread.start()
        pygame.mouse.set_visible(True)
        grid = Grid(Grid)
        player, current, previous, played = 'X', None, None, False
        play, win, draw = False, False, False
        turn_str = "' turn"
        turn = True
        status_message = "Waiting for client..."
        while self.playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                        self.playing = False
                        self.current_menu = self.main_menu
                        self.reset_keys()
                        return
                if event.type == pygame.MOUSEBUTTONDOWN and connection_established:
                    if pygame.mouse.get_pressed()[0]:
                        if turn:
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
                                grid[large_y][large_x][small_y][small_x] = 'X'
                                previous, = player
                                player = Grid.switch_player(player)
                                if not grid[large_y][large_x].win(previous):
                                    grid[large_y][large_x].draw()
                                if win := grid.win(previous, winning_combination=True):
                                    status_message = Game.SHORT_TO_LONG[previous] + " is the winner!"
                                    played = True
                                elif grid.draw():
                                    played = True
                                elif not inner_grid.played and not grid[small_y][small_x].played:
                                    current = (small_y, small_x)
                                else:
                                    current = None
                                if not played:
                                    send_data = f"{large_y}-{large_x}-{small_y}-{small_x}-{self.playing}-{current}".encode()
                                    connection.send(send_data)
                                    play, turn = False, False
                                    status_message = Game.SHORT_TO_LONG[player] + turn_str
                        else:
                            status_message = "It is not your turn"

            self.display.fill(self.BLACK)
            self.draw_top_text(status_message)
            self.window.blit(self.display, (0, 0))
            grid.draw_grid(self.window)

            if played and win:
                Grid.draw_winner(Grid.switch_player(player), win, self.window, self.H_IMAGES)
            elif played and draw:
                status_message = "Draw!"
            if played:
                pygame.display.update()
                pygame.time.delay(5000)
                pygame.mouse.set_visible(False)
                self.playing = False
                self.post_game_menu.message = status_message
                self.current_menu = self.post_game_menu
                self.reset_keys()
                break
            pygame.display.update()

    def client_multiplayer(self):
        host = "127.0.0.1"
        port = 65432

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
        except ConnectionRefusedError:
            self.display.fill(self.BLACK)
            self.draw_text("No games found", 30, int(self.DISPLAY_WIDTH / 2), int(self.DISPLAY_HEIGHT / 2))
            self.window.blit(self.display, (0, 0))
            pygame.display.flip()
            self.current_menu = self.main_menu
            self.playing = False
            pygame.time.delay(3000)
            return

        def receive_data():
            nonlocal turn, player, status_message, current
            while True:
                data = sock.recv(1024).decode()
                y, x, iy, ix, playing, current = data.split('-')
                y, x, iy, ix, current = int(y), int(x), int(iy), int(ix), eval(current)
                turn = True
                grid[y][x][iy][ix] = 'X'
                if not eval(playing):
                    self.playing = False
                player = 'O'
                status_message = Game.SHORT_TO_LONG[player] + turn_str
                grid[y][x].win('X')
                grid[y][x].draw()

        thread = threading.Thread(target=receive_data)
        thread.daemon = True
        thread.start()
        pygame.mouse.set_visible(True)
        grid = Grid(Grid)
        player, current, played = 'X', None, False
        play, win, draw = False, False, False
        turn_str = "' turn"
        turn = False
        status_message = "Connected to server"
        while self.playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                        self.playing = False
                        self.current_menu = self.main_menu
                        self.reset_keys()
                        return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]:
                        if turn:
                            mouse_position = pygame.mouse.get_pos()
                            large_y, small_y = Grid.get_grid_positions(mouse_position[1] - self.Y_OFFSET)
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
                                grid[large_y][large_x][small_y][small_x] = 'O'
                                previous, = player
                                player = Grid.switch_player(player)
                                if not grid[large_y][large_x].win(previous):
                                    grid[large_y][large_x].draw()
                                if win := grid.win(previous, winning_combination=True):
                                    status_message = Game.SHORT_TO_LONG[previous] + " is the winner!"
                                    played = True
                                elif grid.draw():
                                    played = True
                                elif not inner_grid.played and not grid[small_y][small_x].played:
                                    current = (small_y, small_x)
                                else:
                                    current = None
                                if not played:
                                    send_data = f"{large_y}-{large_x}-{small_y}-{small_x}-{self.playing}-{current}".encode()
                                    sock.send(send_data)
                                    turn, play = False, False
                                    status_message = Game.SHORT_TO_LONG[player] + turn_str
                        else:
                            status_message = "It is not your turn"

            self.display.fill(self.BLACK)
            self.draw_top_text(status_message)
            self.window.blit(self.display, (0, 0))
            grid.draw_grid(self.window)

            if played and win:
                Grid.draw_winner(Grid.switch_player(player), win, self.window, self.H_IMAGES)
            elif played and draw:
                status_message = "Draw!"
            if played:
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
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
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
        if not os.path.exists(os.path.join(ASSETS_PATH, 'CX.png')):
            os.remove(os.path.join(ASSETS_PATH, 'CX.png'))
            os.remove(os.path.join(ASSETS_PATH, 'CO.png'))
        generate_highlighted_images(self.highlight)

    def quit(self):
        """Function used to quit the game and de-initialize pygame."""
        self.highlight = (255, 0, 0)
        self.generate_highlighted_images()
        self.running, self.playing = False, False
        self.current_menu.run_display = False
        pygame.quit()
        sys.exit()
