import pygame


class Bullet:
    def __init__(
        self,
        image: pygame.Surface,
        pos: pygame.Vector2,
        direction: pygame.Vector2,
        speed: int,
        damage: int,
    ):
        self.image = image
        self.pos = pos
        self.direction = direction
        self.speed = speed
        self.rect = self.image.get_rect(center=self.pos)
        self.damage = damage

    def update(self, dt: float) -> None:
        self.pos += self.direction * self.speed * dt
        self.rect = self.image.get_rect(center=self.pos)

    def draw(self, screen: pygame.Surface):
        phi = self.direction.as_polar()[1]
        rotated_bullet = pygame.transform.rotate(self.image, -phi - 90)

        screen.blit(
            rotated_bullet,
            rotated_bullet.get_rect(center=self.pos),
        )
