import pygame

import utils
from animation import Animation


class Mob(pygame.sprite.Sprite):
    def __init__(
        self,
        animations: dict[str, Animation],
        max_hp: int,
        pos: pygame.Vector2,
        spawn_sound: pygame.mixer.Sound,
        hit_sound: pygame.mixer.Sound,
        tile_size: int,
        speed: int,
        damage: int,
        attack_range: float = 50.0,
    ):
        pygame.sprite.Sprite.__init__(self)

        self.animations = {
            name: Animation(
                anim.frames, int(anim.frame_duration * 1000), anim.loop
            )
            for name, anim in animations.items()
        }
        for anim in self.animations.values():
            anim.reset()

        self.current_anim_name = "idle"
        self.last_anim_name = "idle"

        self.max_hp = max_hp
        self.hp = max_hp
        self.pos = pos

        self.spawn_sound = spawn_sound
        self.hit_sound = hit_sound

        self.tile_size = tile_size
        self.speed = speed
        self.damage = damage
        self.attack_range = attack_range

        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.direction = pygame.Vector2(1, 0)

        self.spawn_sound.play()

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def hit(
        self,
        damage: int,
    ):
        self.hp = max(self.hp - damage, 0)
        self.hit_sound.play()

        if not self.is_alive:
            self.kill()

        return not self.is_alive

    def _get_anim_state(self, player_pos: pygame.Vector2) -> str:
        distance = self.pos.distance_to(player_pos)
        if distance < self.attack_range:
            return "attack"
        elif distance < 4000:
            return "walk"
        else:
            return "idle"

    def update(self, dt: float, *args, player: pygame.sprite.Sprite, **kwargs):
        player_pos = pygame.Vector2(player.rect.center)
        self.direction = utils.aim_direction(self.pos, player_pos)
        angle = utils.direction_to_angle(self.direction)

        new_anim_name = self._get_anim_state(player_pos)
        if new_anim_name != self.last_anim_name:
            if new_anim_name in self.animations:
                self.animations[new_anim_name].reset()
            self.last_anim_name = new_anim_name

        self.current_anim_name = new_anim_name

        anim = self.animations[self.current_anim_name]
        raw_frame = anim.update(dt)

        if (
            self.is_alive
            and self.current_anim_name != "attack"
            and self.pos.distance_to(player_pos) > self.attack_range
        ):
            step = self.speed * dt
            self.pos += self.direction * step

        self.image = pygame.transform.rotate(raw_frame, angle - 90)
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
