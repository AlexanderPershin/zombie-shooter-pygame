import pygame

import utils
from animation import Animation
from guns import Gun


class Player(pygame.sprite.Sprite):
    def __init__(
        self,
        hp: int,
        pos: pygame.Vector2,
        speed: int,
        animations: dict[str, Animation],
        footsteps_sound: pygame.mixer.Sound,
        hit_sound: pygame.mixer.Sound,
        guns: list[Gun],
    ):
        pygame.sprite.Sprite.__init__(self)

        self.animations = animations
        self.current_anim_name = "idle"
        self.last_anim_name = "idle"

        self.guns = guns
        self.gun_index = 0
        self.gun = self.guns[self.gun_index]

        self.footsteps_sound = footsteps_sound
        self.hit_sound = hit_sound

        self.max_hp = hp
        self.hp = hp
        self.speed = speed

        self.invincible_timer = 0.0
        self.invincible_duration = 0.5

        self.pos = pos

        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.was_moving = False
        self.is_left_mouse = False
        self.is_reload = False

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

    def _shoot(self, direction: pygame.Vector2):
        self.gun.shoot(self.pos, direction)

    def _reload(self) -> None:
        self.gun.reload()
        self.is_reload = False

    def hit(self, damage: int) -> None:
        if self.invincible_timer <= 0:
            self.hit_sound.play()
            self.hp = max(self.hp - damage, 0)
            self.invincible_timer = self.invincible_duration

    def update(
        self,
        dt: float,
        *args,
        is_left_mouse: bool,
        is_wheel_down: bool,
        is_reload: bool,
        **kwargs,
    ) -> None:
        self.is_left_mouse = is_left_mouse
        keys = pygame.key.get_pressed()
        move = utils.get_movement_direction(keys)

        mouse_pos = pygame.mouse.get_pos()
        self.pos += move * self.speed * dt

        direction = utils.aim_direction(self.pos, mouse_pos)
        angle = utils.direction_to_angle(direction)

        self.gun.update(dt)

        if self.is_left_mouse:
            self._shoot(direction)

        if is_reload:
            self._reload()

        if is_wheel_down:
            self.gun_index = (self.gun_index + 1) % len(self.guns)
            self.gun = self.guns[self.gun_index]

        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        is_moving = move.length_squared() > 0

        if is_moving:
            new_anim_name = "attack"
        elif self.is_left_mouse:
            new_anim_name = "locked"
        else:
            new_anim_name = "idle"

        if new_anim_name != self.last_anim_name:
            self.animations[new_anim_name].reset()
            self.last_anim_name = new_anim_name

        self.current_anim_name = new_anim_name
        anim = self.animations[self.current_anim_name]
        raw_frame = anim.update(dt)

        self._update_footsteps(move)

        base_frame = raw_frame.copy()
        base_frame_rect = base_frame.get_rect()
        gun_rect = self.gun.top_image.get_rect(
            centerx=base_frame_rect.centerx,
            bottom=base_frame_rect.centery,
        )
        base_frame.blit(self.gun.top_image, gun_rect)
        self.image = pygame.transform.rotate(base_frame, angle - 90)

        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
