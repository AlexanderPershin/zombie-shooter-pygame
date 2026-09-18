import pygame


class Bullet(pygame.sprite.Sprite):
    def __init__(
        self,
        image: pygame.Surface,
        pos: pygame.Vector2,
        direction: pygame.Vector2,
        speed: int,
        damage: int,
    ):
        pygame.sprite.Sprite.__init__(self)

        self.pos = pos
        self.direction = direction
        self.speed = speed
        self.damage = damage

        phi = self.direction.as_polar()[1]
        self.image = pygame.transform.rotate(image, -phi - 90)

        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt: float, *args, **kwargs) -> None:
        self.pos += self.direction * self.speed * dt
        self.rect = self.image.get_rect(center=self.pos)
