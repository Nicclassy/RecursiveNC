__all__ = ["Graphics", "Projectile"]

import os
import random
from typing import Tuple, Optional
from pprint import pprint
import pygame
from src.grid import SMALL_IMAGES, IMAGES, ASSETS_PATH

HIGHLIGHTED_IMAGES = {
    'X': pygame.image.load(os.path.join(ASSETS_PATH, "CX.png")),
    'O': pygame.image.load(os.path.join(ASSETS_PATH, "CO.png")),
}

ALL_IMAGES = {
    0: IMAGES,
    1: SMALL_IMAGES,
    2: HIGHLIGHTED_IMAGES,
    3: SMALL_IMAGES,
}


class Projectile:

    def __init__(self, player: str, number: int, speed: float, position: Tuple[int, int]):
        self.IMAGE = ALL_IMAGES[number][player]
        self.y, self.x = position
        self.speed = speed

    def __repr__(self):
        return f"Projectile(width={self.IMAGE.get_width()}, y={self.y}, x={self.x}, speed={self.speed})"

    def __iter__(self):
        return self

    def __next__(self):
        self.y += self.speed
        return self.y

    @classmethod
    def generate(cls, domain):
        return cls(random.choice(('X', 'O')), random.randint(0, 3), random.randint(1, 5),
                   (0, random.randint(0, domain)))

    def get_position(self):
        return self.x, self.y

    def draw(self, screen: pygame.Surface):
        screen.blit(self.IMAGE, self.get_position())


class Graphics:

    def __init__(self, domain: Optional[int] = 600, size: Optional[int] = 50):
        sections = range(size, domain + 1, size)
        projectiles = map(Projectile.generate, sections)
        self.sections = dict(zip(sections, projectiles))
        self.domain = domain
        self.section = size

    def __getitem__(self, item):
        return self.sections[item]

    def __setitem__(self, key, value):
        self.sections[key] = value

    def set_next_state(self):
        for projectile in self.sections.values():
            yield next(projectile)

    def get_next_state(self):
        yield from self.set_next_state()

    def next(self):
        return list(self.get_next_state())


if __name__ == '__main__':
    graphics = Graphics()
    pprint(graphics.sections)
    print('\n')
    graphics.next()
    pprint(graphics.sections)



