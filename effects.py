import enum
import random

import pygame


class GroundEffectTypes(enum.Enum):
    BLOOD = enum.auto()


class BloodSplat(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: pygame.Vector2,
        direction: pygame.Vector2,
        scale: float,
        image: pygame.Surface,
    ):
        pygame.sprite.Sprite.__init__(self)

        angle = direction.angle_to(pygame.Vector2(0, -1))

        angle += random.uniform(-20, 20)
        self.image = pygame.transform.rotate(image, angle)

        new_size = (
            int(self.image.get_width() * scale),
            int(self.image.get_height() * scale),
        )
        self.image = pygame.transform.scale(self.image, new_size)
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.age = 0.0

    def update(self, dt: float, *args, **kwargs) -> None:
        self.age += dt
