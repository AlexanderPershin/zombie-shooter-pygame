import pygame

import utils


class Mob:
    HP_BAR_HEIGHT = 6
    HP_BAR_OFFSET = 10

    def __init__(
        self,
        image: pygame.Surface,
        max_hp: int,
        pos: pygame.Vector2,
        spawn_sound: pygame.mixer.Sound,
        hit_sound: pygame.mixer.Sound,
        tile_size: int,
        speed: int,
    ):
        self.image = image

        self.max_hp = max_hp
        self.hp = max_hp

        self.pos = pos

        player_pos = pygame.Vector2()
        self.direction = utils.aim_direction(self.pos, player_pos)

        self.spawn_sound = spawn_sound
        self.hit_sound = hit_sound

        self.tile_size = tile_size

        self.speed = speed

        self.rect: pygame.Rect = self.image.get_rect(center=self.pos)

        self.spawn_sound.play()

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def hit(self, pos: pygame.Vector2, damage: int):
        if self.rect.collidepoint(pos):
            self.hp = max(self.hp - damage, 0)
            self.hit_sound.play()
            return True

        return False

    def update(self, player_rect: pygame.Rect, dt: float):
        player_pos = pygame.Vector2(player_rect.center)
        self.direction = utils.aim_direction(self.pos, player_pos)

        if not self.rect.colliderect(player_rect):
            step = self.speed * dt
            self.pos += self.direction * step

        self.rect = self.image.get_rect(center=self.pos)

    def draw(self, screen: pygame.Surface):
        rotation_angle = utils.direction_to_angle(self.direction) - 90

        rotated_image = pygame.transform.rotate(self.image, rotation_angle)
        screen.blit(rotated_image, rotated_image.get_rect(center=self.pos))

        half = self.tile_size / 2
        bar_width = self.tile_size
        bar_x = self.pos.x - half
        bar_y = self.pos.y - half - self.HP_BAR_OFFSET

        pygame.draw.rect(
            screen,
            "#330000",
            (bar_x, bar_y, bar_width, self.HP_BAR_HEIGHT),
        )
        if self.hp >= 0:
            fill_width = int(bar_width * self.hp / self.max_hp)
            pygame.draw.rect(
                screen,
                "#fa5252",
                (bar_x, bar_y, fill_width, self.HP_BAR_HEIGHT),
            )
