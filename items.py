from typing import Protocol

import pygame

from player import Player


class Item(Protocol):
    def use(self, player: Player) -> bool: ...

    def draw(self, screen: pygame.Surface) -> None: ...


class Medpack:
    def __init__(
        self, image: pygame.Surface, pos: pygame.Vector2, heal_amount: int
    ):
        self.image = image
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)
        self.heal_amount = heal_amount

    def use(self, player: Player) -> bool:
        if player.rect.colliderect(self.rect):
            player.hp = min(player.hp + self.heal_amount, player.max_hp)
            return True
        return False

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)
