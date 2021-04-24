__all__ = ["Graphics", "Projectile"]

import os
import random
from typing import Tuple, Optional
import pygame
from src.grid import SMALL_IMAGES, IMAGES, ASSETS_PATH


class Projectile:

    __slots__ = "IMAGE", "y", "x", "speed"

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
    def generate(cls, domain: int):
        return cls(random.choice(('X', 'O')), random.randint(0, 4), random.randint(10, 50) / 10,
                   (random.randint(-100, 0), random.randint(0, domain)))

    def get_position(self):
        return self.x, self.y

    def draw(self, screen: pygame.Surface):
        screen.blit(self.IMAGE, self.get_position())


class Graphics:

    __slots__ = "sections", "domain", "section"

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

    @classmethod
    def reload(cls):
        ALL_IMAGES[len(ALL_IMAGES) - 1] = {'X': pygame.image.load(os.path.join(ASSETS_PATH, "CX.png")),
                                           'O': pygame.image.load(os.path.join(ASSETS_PATH, "CO.png"))}


ALL_IMAGES = {
    0: IMAGES,
    1: SMALL_IMAGES,
    2: SMALL_IMAGES,
    3: SMALL_IMAGES,
    4: {'X': pygame.image.load(os.path.join(ASSETS_PATH, "CX.png")),
        'O': pygame.image.load(os.path.join(ASSETS_PATH, "CO.png"))},
}
