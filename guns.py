import pygame

from bullet import Bullet


class Gun:
    def __init__(
        self,
        name: str,
        side_image: pygame.Surface,
        top_image: pygame.Surface,
        bullet_image: pygame.Surface,
        damage: int,
        bullet_speed: int,
        fire_interval: int,
        clip_size: int,
        reload_interval: int,
        shot_sound: pygame.mixer.Sound,
        reload_sound: pygame.mixer.Sound,
        all_sprites: pygame.sprite.LayeredUpdates,
        bullets_group: pygame.sprite.Group,
    ):
        self.name = name

        self.side_image = pygame.transform.scale_by(side_image, 0.3)
        self.top_image = pygame.transform.scale_by(top_image, 0.25)
        self.image = top_image
        self.rect = self.image.get_rect()

        self.bullet_image = bullet_image
        self.damage = damage
        self.bullet_speed = bullet_speed
        self.fire_interval = fire_interval
        self.reload_interval = reload_interval

        self.shot_sound = shot_sound
        self.reload_sound = reload_sound

        self.all_sprites = all_sprites
        self.bullets_group = bullets_group

        self.clip_size = clip_size
        self.bullets_shot = 0

        self.fire_cooldown = 0.0
        self.reload_cooldown = 0.0

    @property
    def is_reloading(self) -> bool:
        return bool(self.reload_cooldown)

    def __str__(self) -> str:
        clip_info = "|" * (self.clip_size - self.bullets_shot)
        info = "Reloading…" if self.is_reloading else clip_info
        return f"{self.name} {info}"

    def update(self, dt) -> None:
        self.fire_cooldown = max(self.fire_cooldown - dt, 0.0)
        self.reload_cooldown = max(self.reload_cooldown - dt, 0.0)

    def shoot(self, pos: pygame.Vector2, direction: pygame.Vector2) -> None:
        if self.reload_cooldown <= 0 and self.fire_cooldown <= 0:
            self.reload_sound.stop()
            self.shot_sound.play()

            self.bullets_shot += 1
            bullet = Bullet(
                self.bullet_image,
                pos.copy(),
                direction,
                self.bullet_speed,
                self.damage,
            )

            self.all_sprites.add(bullet, layer=1)
            self.bullets_group.add(bullet)

            self.fire_cooldown = self.fire_interval
            if self.bullets_shot >= self.clip_size:
                self.reload()

    def reload(self) -> None:
        self.reload_sound.play()

        self.reload_cooldown = self.reload_interval
        self.fire_cooldown = 0.0
        self.bullets_shot = 0
