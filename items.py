from typing import Protocol

import pygame

from player import Player


class Item(Protocol):
    def use(self, player: Player) -> bool: ...


class Medpack(pygame.sprite.Sprite):
    def __init__(
        self, image: pygame.Surface, pos: pygame.Vector2, heal_amount: int
    ):
        pygame.sprite.Sprite.__init__(self)

        self.image = image

        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.heal_amount = heal_amount

    def use(self, player: Player) -> bool:
        if player.hp < player.max_hp:
            player.hp = min(player.hp + self.heal_amount, player.max_hp)

            self.kill()

            return True
        return False
