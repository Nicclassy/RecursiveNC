import pygame

__all__ = ["MainMenu", "OptionsMenu", "PostGameMenu"]


class Menu:

    def __init__(self, game):
        self.game = game
        self.mid_width, self.mid_height = self.game.DISPLAY_WIDTH / 2, self.game.DISPLAY_HEIGHT / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20)
        self.offset = -100
        self.font_size = 30
        self.bottom_padding = 30
        self.starting_y = 30

    def draw_cursor(self):
        self.game.draw_text('*', self.font_size, self.cursor_rect.x, self.cursor_rect.y)

    def blit_screen(self):
        self.game.window.blit(self.game.display, (0, 0))
        pygame.display.update()
        self.game.reset_keys()


class MainMenu(Menu):

    def __init__(self, game):
        super().__init__(game)
        self.state = "Play"
        self.play_x, self.play_y = self.mid_width, self.mid_height + self.starting_y
        self.options_x, self.options_y = self.mid_width, self.mid_height + self.starting_y + self.bottom_padding
        self.tutorial_x, self.tutorial_y = self.mid_width, self.mid_height + self.starting_y + self.bottom_padding * 2
        self.quit_x, self.quit_y = self.mid_width, self.mid_height + self.starting_y + self.bottom_padding * 3
        self.cursor_rect.midtop = (self.play_x + self.offset, self.play_y)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text('Main Menu', 40, self.game.DISPLAY_WIDTH / 2, self.game.DISPLAY_HEIGHT / 2 - self.font_size)
            self.game.draw_text("Play", self.font_size, self.play_x, self.play_y)
            self.game.draw_text("Options", self.font_size, self.options_x, self.options_y)
            self.game.draw_text("Tutorial", self.font_size, self.tutorial_x, self.tutorial_y)
            self.game.draw_text("Quit", self.font_size, self.quit_x, self.quit_y)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == "Play":
                self.cursor_rect.midtop = (self.options_x + self.offset, self.options_y)
                self.state = "Options"
            elif self.state == "Options":
                self.cursor_rect.midtop = (self.tutorial_x + self.offset, self.tutorial_y)
                self.state = "Tutorial"
            elif self.state == "Tutorial":
                self.cursor_rect.midtop = (self.quit_x + self.offset, self.quit_y)
                self.state = "Quit"
            elif self.state == "Quit":
                self.cursor_rect.midtop = (self.play_x + self.offset, self.play_y)
                self.state = "Play"
        elif self.game.UP_KEY:
            if self.state == "Play":
                self.cursor_rect.midtop = (self.quit_x + self.offset, self.quit_y)
                self.state = "Quit"
            elif self.state == "Options":
                self.cursor_rect.midtop = (self.play_x + self.offset, self.play_y)
                self.state = "Play"
            elif self.state == "Tutorial":
                self.cursor_rect.midtop = (self.options_x + self.offset, self.options_y)
                self.state = "Options"
            elif self.state == "Quit":
                self.cursor_rect.midtop = (self.tutorial_x + self.offset, self.tutorial_y)
                self.state = "Tutorial"

    def check_input(self):
        self.move_cursor()
        if self.game.START_KEY:
            if self.state == "Play":
                self.game.playing = True
            elif self.state == "Options":
                self.game.current_menu = self.game.options_menu
            elif self.state == "Quit":
                quit()
            self.run_display = False


class OptionsMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.state = "Volume"
        self.volume_x, self.volume_y = self.mid_width, self.mid_height + self.starting_y
        self.controls_x, self.controls_y = self.mid_width, self.mid_height + self.starting_y + self.bottom_padding
        self.cursor_rect.midtop = (self.volume_x + self.offset, self.volume_y)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill((0, 0, 0))
            self.game.draw_text("Options", 40, self.game.DISPLAY_WIDTH / 2, self.game.DISPLAY_HEIGHT / 2 - self.font_size)
            self.game.draw_text("Volume", self.font_size, self.volume_x, self.volume_y)
            self.game.draw_text("Controls", self.font_size, self.controls_x, self.controls_y)
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if self.game.BACK_KEY:
            self.game.current_menu = self.game.main_menu
            self.run_display = False
        elif self.game.UP_KEY or self.game.DOWN_KEY:
            if self.state == "Volume":
                self.state = "Controls"
                self.cursor_rect.midtop = (self.controls_x + self.offset, self.controls_y)
            elif self.state == "Controls":
                self.state = "Volume"
                self.cursor_rect.midtop = (self.volume_x + self.offset, self.volume_y)
        elif self.game.START_KEY:
            pass


class PostGameMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.state = "Play Again"
        self.pa_x, self.pa_y = self.mid_width, self.mid_height + self.starting_y
        self.mm_x, self.mm_y = self.mid_width, self.mid_height + self.starting_y + self.bottom_padding
        self.cursor_rect.midtop = (self.pa_x + self.offset, self.pa_y)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill((0, 0, 0))
            self.game.draw_text("Someone won", 40, self.game.DISPLAY_WIDTH / 2, self.game.DISPLAY_HEIGHT / 2 - self.font_size)
            self.game.draw_text("Play Again", self.font_size, self.pa_x, self.pa_y)
            self.game.draw_text("Main Menu", self.font_size, self.mm_x, self.mm_y)
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if self.game.UP_KEY or self.game.DOWN_KEY:
            if self.state == "Play Again":
                self.state = "Main Menu"
                self.cursor_rect.midtop = (self.mm_x + self.offset, self.mm_y)
            elif self.state == "Main Menu":
                self.state = "Play Again"
                self.cursor_rect.midtop = (self.pa_x + self.offset, self.pa_y)
            if self.game.START_KEY:
                if self.state == "Play Again":
                    self.game.playing = True
                elif self.state == "Main Menu":
                    self.game.current_menu = self.game.main_menu
                self.run_display = False


