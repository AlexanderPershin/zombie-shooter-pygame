import pygame

import utils
from bullet import Bullet
from guns import Gun

BULLET_SPAWN_OFFSET = 32
FRAME_COUNT = 8
ANIMATION_SPEED_MS = 150


class Player:
    def __init__(
        self,
        hp: int,
        pos: pygame.Vector2,
        speed: int,
        frames: list[pygame.Surface],
        footsteps_sound: pygame.mixer.Sound,
        guns: list[Gun],
    ):
        self.current_frame = 0
        self.frames = frames

        self.guns = guns
        self.gun_index = 0
        self.gun = self.guns[self.gun_index]

        self.footsteps_sound = footsteps_sound

        self.max_hp = hp
        self.hp = hp
        self.speed = speed

        self.invincible_timer = 0.0
        self.invincible_duration = 0.5

        self.pos = pos
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=self.pos)

        self.animation_timer = 0
        self.was_moving = False

        self.bullets: list[Bullet] = []

    @property
    def is_dead(self) -> bool:
        return self.hp <= 0

    def _update_footsteps(self, move: pygame.Vector2) -> None:
        is_moving = move.length_squared() > 0

        if is_moving and not self.was_moving:
            self.footsteps_sound.play(-1)
        elif not is_moving and self.was_moving:
            self.footsteps_sound.stop()

        self.was_moving = is_moving

    def _update_animation(self, move: pygame.Vector2, dt: float) -> None:
        if move.length_squared() > 0:
            self.animation_timer += dt * 1000
            if self.animation_timer >= ANIMATION_SPEED_MS:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % FRAME_COUNT
        else:
            self.current_frame = 0

    def _update_bullets(self, dt: float) -> None:
        for bullet in self.bullets:
            bullet.update(dt)

    def _shoot(self, direction: pygame.Vector2):
        bullet = self.gun.shoot(self.pos, direction)
        if bullet is not None:
            self.bullets.append(bullet)

    def _reload(self) -> None:
        self.gun.reload()

    def hit(self, rect: pygame.Rect, damage: int):
        if self.rect.colliderect(rect) and self.invincible_timer <= 0:
            self.hp = max(self.hp - damage, 0)
            self.invincible_timer = self.invincible_duration

    def update(
        self,
        move: pygame.Vector2,
        is_left_mouse: bool,
        is_wheel_down: bool,
        is_reload: bool,
        mouse_pos,
        dt: float,
    ):
        self.pos += move * self.speed * dt

        direction = utils.aim_direction(self.pos, mouse_pos)
        angle = utils.direction_to_angle(direction)

        self.gun.update(dt)

        if is_left_mouse:
            self._shoot(direction)
        else:
            self.fire_cooldown = 0.0

        if is_reload:
            self._reload()

        if is_wheel_down:
            self.gun_index = (self.gun_index + 1) % len(self.guns)
            self.gun = self.guns[self.gun_index]

        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        self._update_footsteps(move)
        self._update_animation(move, dt)
        self._update_bullets(dt)

        self.image = pygame.transform.rotate(
            self.frames[self.current_frame], angle - 90
        )
        self.rect = self.image.get_rect(center=self.pos)

    def _draw_bullets(self, screen: pygame.Surface):
        for bullet in self.bullets:
            bullet.draw(screen)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

        self._draw_bullets(screen)
