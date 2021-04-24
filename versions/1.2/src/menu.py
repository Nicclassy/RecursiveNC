__all__ = ["MainMenu", "OptionsMenu", "PostGameMenu", "ColourMenu"]

import sys
import operator
import pygame
from src.graphics import Graphics, Projectile


class Menu:

    def __init__(self, game):
        """Creates an instance of the menu class.
        Called when instances of various menu subclasses are initialized."""
        self.game = game
        self.mid_width, self.mid_height = self.game.DISPLAY_WIDTH / 2, self.game.DISPLAY_HEIGHT / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20)
        self.offset = -100
        self.font_size = 30
        self.bottom_padding = 30
        self.starting_y = 30
        self.graphics = Graphics()

    def draw_cursor(self):
        """Draws the cursor to the screen."""
        self.game.draw_text('>>>', self.font_size, self.cursor_rect.x, self.cursor_rect.y)

    def blit_screen(self):
        """Draws the display's current state to the window."""
        self.game.window.blit(self.game.display, (0, 0))
        pygame.display.update()
        self.game.reset_keys()

    def draw_graphics(self):
        """Draws the graphics to the screen."""
        for key, projectile in self.graphics.sections.items():
            if projectile.y > self.game.DISPLAY_WIDTH:
                self.graphics[key] = Projectile.generate(self.game.DISPLAY_WIDTH)
            self.game.display.blit(self.graphics[key].IMAGE, self.graphics[key].get_position())
        self.graphics.next()


class MainMenu(Menu):

    def __init__(self, game):
        super().__init__(game)
        self.state = "Tutorial"
        self.play_x, self.play_y = self.mid_width, self.mid_height + self.starting_y
        self.options_x, self.options_y = self.mid_width, self.mid_height + self.starting_y + self.bottom_padding
        self.tutorial_x, self.tutorial_y = self.mid_width, self.mid_height + self.starting_y + self.bottom_padding * 2
        self.quit_x, self.quit_y = self.mid_width, self.mid_height + self.starting_y + self.bottom_padding * 3
        self.cursor_rect.midtop = (self.tutorial_x + self.offset, self.tutorial_y)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.draw_graphics()
            self.game.draw_text("Recursive", 40, self.game.DISPLAY_WIDTH / 2,
                                self.game.DISPLAY_HEIGHT / 2 - self.font_size * 2 - 10)
            self.game.draw_text("Noughts & Crosses", 40, self.game.DISPLAY_WIDTH / 2,
                                self.game.DISPLAY_HEIGHT / 2 - self.font_size)
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
                pygame.quit()
                sys.exit()
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
            self.game.display.fill(self.game.BLACK)
            self.draw_graphics()
            self.game.draw_text("Options", 40, self.game.DISPLAY_WIDTH / 2,
                                self.game.DISPLAY_HEIGHT / 2 - self.font_size)
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
            if self.state == "Controls":
                self.game.current_menu = self.game.colour_menu
            self.run_display = False


class PostGameMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.state = "Play Again"
        self.pa_x, self.pa_y = self.mid_width, self.mid_height + self.starting_y
        self.mm_x, self.mm_y = self.mid_width, self.mid_height + self.starting_y + self.bottom_padding
        self.cursor_rect.midtop = (self.pa_x + self.offset, self.pa_y)
        self.message = None

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.draw_graphics()
            self.game.draw_text(self.message, 40, self.game.DISPLAY_WIDTH / 2,
                                self.game.DISPLAY_HEIGHT / 2 - self.font_size)
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
        if self.game.BACK_KEY:
            self.game.current_menu = self.game.main_menu


class ColourMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.state = "Red"
        self.R, self.G, self.B = self.game.highlight
        self.R_X, self.R_Y = self.mid_width, self.mid_height + self.starting_y
        self.G_X, self.G_Y = self.mid_width, self.mid_height + self.starting_y + self.bottom_padding
        self.B_X, self.B_Y = self.mid_width, self.mid_height + self.starting_y + self.bottom_padding * 2
        self.save_x, self.save_y = self.mid_width, self.mid_height + self.starting_y + self.bottom_padding * 4
        self.cursor_rect.midtop = (self.R_X + self.offset, self.R_Y)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.draw_graphics()
            self.game.draw_text("Change colour", 40, self.game.DISPLAY_WIDTH / 2,
                                self.game.DISPLAY_HEIGHT / 2 - self.font_size)
            self.game.draw_text(f"Red: {self.R}", self.font_size, self.R_X, self.R_Y)
            self.game.draw_text(f"Green: {self.G}", self.font_size, self.G_X, self.G_Y)
            self.game.draw_text(f"Blue: {self.B}", self.font_size, self.B_X, self.B_Y)
            self.game.draw_text("Save", self.font_size, self.save_x, self.save_y)
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if self.game.RIGHT_KEY or self.game.LEFT_KEY:
            operation = operator.add if self.game.RIGHT_KEY else operator.sub
            if self.state == "Red":
                self.R = operation(self.R, 1)
                if self.R == 256:
                    self.R = 0
                if self.R == -1:
                    self.R = 255
            elif self.state == "Blue":
                self.B = operation(self.B, 1)
                if self.B == 256:
                    self.B = 0
                if self.B == -1:
                    self.B = 255
            elif self.state == "Green":
                self.G = operation(self.G, 1)
                if self.G == 256:
                    self.G = 0
                if self.G == -1:
                    self.G = 255
        if self.game.BACK_KEY:
            self.game.current_menu = self.game.options_menu
            self.run_display = False
        elif self.game.DOWN_KEY:
            if self.state == "Green":
                self.state = "Blue"
                self.cursor_rect.midtop = (self.B_X + self.offset, self.B_Y)
            elif self.state == "Red":
                self.state = "Green"
                self.cursor_rect.midtop = (self.G_X + self.offset, self.G_Y)
            elif self.state == "Blue":
                self.state = "Save"
                self.cursor_rect.midtop = (self.save_x + self.offset, self.save_y)
            elif self.state == "Save":
                self.state = "Red"
                self.cursor_rect.midtop = (self.R_X + self.offset, self.R_Y)
        elif self.game.UP_KEY:
            if self.state == "Save":
                self.state = "Blue"
                self.cursor_rect.midtop = (self.B_X + self.offset, self.B_Y)
            elif self.state == "Blue":
                self.state = "Green"
                self.cursor_rect.midtop = (self.G_X + self.offset, self.G_Y)
            elif self.state == "Red":
                self.state = "Save"
                self.cursor_rect.midtop = (self.save_x + self.offset, self.save_y)
            elif self.state == "Green":
                self.state = "Red"
                self.cursor_rect.midtop = (self.R_X + self.offset, self.R_Y)
        if self.game.START_KEY:
            if self.state == "Save":
                self.game.highlight = (self.R, self.G, self.B)
                self.game.generate_highlighted_images()
                self.game.load_images()
                self.game.current_menu = self.game.main_menu
            self.run_display = False
        elif self.game.BACK_KEY:
            self.run_display = False
            self.game.current_menu = self.game.options_menu


if __name__ == '__main__':
    MENUS = Menu.__subclasses__()
    for menu in MENUS:
        print(menu.__qualname__)

