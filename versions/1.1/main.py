import os
import pygame
from menu import MainMenu, OptionsMenu, PostGameMenu
from grid import Grid, DIMENSION


class Game:  # State machine

    def __init__(self, dimension: int):
        pygame.init()
        pygame.display.set_caption('Recursive Noughts and Crosses')
        pygame.display.set_icon(pygame.image.load(os.path.join('assets', 'icon.png')))
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.Y_OFFSET = DIMENSION / 2
        self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT = dimension * 3, dimension * 3 + self.Y_OFFSET
        self.display = pygame.Surface(DISPLAY_VALUES := (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        self.window = pygame.display.set_mode(DISPLAY_VALUES)
        self.font_name = pygame.font.get_default_font()
        self.BLACK, self.WHITE = (0, 0, 0), (255, 255, 255)
        self.HIGHLIGHT = (255, 0, 0)
        self.main_menu = MainMenu(self)
        self.options_menu = OptionsMenu(self)
        self.post_game_menu = PostGameMenu(self)
        self.current_menu = self.main_menu

    def game_loop(self):
        self.check_events()
        if self.START_KEY:
            self.playing = True
        if self.playing:
            grid = Grid(Grid)
            player, current, played = 'X', None, True
            while self.playing:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.playing = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if pygame.mouse.get_pressed()[0]:
                            mouse_position = pygame.mouse.get_pos()
                            large_y, small_y = Grid.get_grid_positions(mouse_position[1])
                            large_x, small_x = Grid.get_grid_positions(mouse_position[0])
                            if (inner_grid := grid[large_y][large_x])[small_y][small_x] is not None:
                                "IAW"
                            elif current is None:
                                play = True
                            else:
                                if inner_grid.played:
                                    "IAW"
                                elif current == (large_y, large_x):
                                    play = True
                                else:
                                    "IAW"

                            if play:
                                grid[large_y][large_x][small_y][small_x] = player
                                previous, = player
                                player = Grid.switch_player(player)
                                play = False
                                if not grid[large_y][large_x].win(previous):
                                    grid[large_y][large_x].draw()
                                win = grid.win(previous, winning_combination=True)
                                if win or grid.draw():
                                    print("We got a winner:", previous)
                                    played = True
                                    # Wait some time then exit/play again
                                    self.playing = False
                                elif not inner_grid.played and not grid[small_y][small_x].played:
                                    current = (small_y, small_x)
                                else:
                                    current = None

                self.display.fill(self.BLACK)
                self.window.blit(self.display, (0, 0))
                grid.draw_grid(self.window)
                # if played:
                #     pygame.time.delay(5000)
                #     grid.draw_winner(win)
                #     pygame.time.delay(5000)
                pygame.display.update()
                self.reset_keys()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                self.current_menu.run_display = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE:
                    self.BACK_KEY = True
                if event.key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP:
                    self.UP_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False

    def draw_text(self, text: str, size: int, x: int, y: int, /):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, self.HIGHLIGHT if y == self.current_menu.cursor_rect.y else self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display.blit(text_surface, text_rect)


if __name__ == '__main__':
    game = Game(DIMENSION)
    while game.running:
        game.current_menu.display_menu()
        game.game_loop()
