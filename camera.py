import pygame


class Camera(pygame.sprite.Sprite):
    def __init__(
        self,
        width: int,
        height: int,
        world_width: int,
        world_height: int,
    ):
        pygame.sprite.Sprite.__init__(self)

        self.width = width
        self.height = height

        self.world_width = world_width
        self.world_height = world_height

        self.image = pygame.Surface((self.width, self.height))
        self.rect = pygame.Rect(0, 0, self.width, self.height)

        self.is_fixed = (
            self.world_width <= self.width and self.world_height <= self.height
        )

        if self.is_fixed:
            self.rect.x = (self.world_width - self.width) // 2
            self.rect.y = (self.world_height - self.height) // 2

    def update(self, target_rect: pygame.Rect) -> None:
        if self.is_fixed:
            return

        self.rect.x = target_rect.centerx - self.width // 2
        self.rect.y = target_rect.centery - self.height // 2

        self.rect.x = max(0, min(self.rect.x, self.world_width - self.width))
        self.rect.y = max(0, min(self.rect.y, self.world_height - self.height))

    def cut(self, rect):
        return rect.move(-self.rect.x, -self.rect.y)
