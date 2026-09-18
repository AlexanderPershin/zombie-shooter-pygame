import random

import pygame

import utils
from animation import Animation
from bullet import Bullet
from camera import Camera
from config import Config
from crosshair import Crosshair
from effects import BloodSplat, GroundEffectTypes
from enemies import Mob
from guns import Gun
from items import Item, Medpack
from player import Player
from scenes.scene import AbstractScene
from scenes.scene_manager import SceneManager
from ui import Ui

PLAYER_MAX_HP = 100
MOB_SPAWN_DELAY_MS = 3000
SCREEN_MARGIN = 100
MAX_GROUND_EFFECTS = 500
MAX_MOBS_COUNT = 100

LEVELS = [
    {
        "threshold": 10,
        "enemy_speed": (80, 160),
        "enemy_damage": 10,
        "enemies_count": 5,
        "enemies_increment": 5,
    },
    {
        "threshold": 20,
        "enemy_speed": (100, 180),
        "enemy_damage": 20,
        "enemies_count": 10,
        "enemies_increment": 10,
    },
    {
        "threshold": 30,
        "enemy_speed": (120, 200),
        "enemy_damage": 30,
        "enemies_count": 15,
        "enemies_increment": 15,
    },
]


class GameScene(AbstractScene):
    def __init__(
        self,
        manager: SceneManager,
        config: Config,
        player_animations: dict[str, Animation],
        zombie_animations: dict[str, Animation],
        blood_splatter_image: pygame.Surface,
        bullet_image: pygame.Surface,
        glock_side_view_image: pygame.Surface,
        glock_top_view_image: pygame.Surface,
        deagle_side_view_image: pygame.Surface,
        deagle_top_view_image: pygame.Surface,
        background_image: pygame.Surface,
        medpack_image: pygame.Surface,
        crosshair_image: pygame.Surface,
        shot_sound: pygame.Sound,
        reload_sound: pygame.Sound,
        impact_sound: pygame.Sound,
        zombie_sound: pygame.Sound,
        footsteps_sound: pygame.Sound,
        player_hit_sound: pygame.Sound,
        font: pygame.Font,
    ):
        self.manager = manager
        self.config = config

        self.player_animations = player_animations
        self.zombie_animations = zombie_animations

        self.blood_splatter_image = blood_splatter_image
        self.bullet_image = bullet_image
        self.glock_side_view_image = glock_side_view_image
        self.glock_top_view_image = glock_top_view_image
        self.deagle_side_view_image = deagle_side_view_image
        self.deagle_top_view_image = deagle_top_view_image
        self.background_image = background_image
        self.medpack_image = medpack_image
        self.crosshair_image = crosshair_image
        self.shot_sound = shot_sound
        self.reload_sound = reload_sound
        self.impact_sound = impact_sound
        self.zombie_sound = zombie_sound
        self.footsteps_sound = footsteps_sound
        self.player_hit_sound = player_hit_sound
        self.font = font

        self.SPAWN_ENEMY_EVENT = pygame.event.custom_type()

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.ground_effects = pygame.sprite.Group()
        self.ui_sprites = pygame.sprite.LayeredUpdates()

        self.player_bullets: pygame.sprite.Group[Bullet] = (
            pygame.sprite.Group()
        )
        self.enemies: pygame.sprite.Group[Mob] = pygame.sprite.Group()
        self.items: pygame.sprite.Group[Item] = pygame.sprite.Group()

        self._create_guns()

        self.world_bounds = pygame.Rect(
            0, 0, self.config.world_width, self.config.world_height
        ).inflate(SCREEN_MARGIN, SCREEN_MARGIN)

        self.mouse_pos = pygame.Vector2()

        self.is_left_mouse = False
        self.is_wheel_down = False
        self.is_reload = False

        self.score = 0
        self.level_index = 0

        self.player = None

        self.mobs_positions: list[pygame.Vector2] = (
            utils.generate_mobs_positions(
                self.config.tile_size,
                self.config.world_width,
                self.config.world_height,
                SCREEN_MARGIN,
            )
        )

        self.mobs_number = self.level_config["enemies_count"]

        self.crosshair = Crosshair(self.crosshair_image)
        self.ui_sprites.add(self.crosshair, layer=4)

        self.camera = Camera(
            self.config.window_width,
            self.config.window_height,
            self.config.world_width,
            self.config.world_height,
        )

        self.ui = Ui(
            self.config.window_width,
            self.config.window_height,
            pygame.Vector2(10, self.config.window_height - 50),
            self.font,
            self.config.gui_text_color,
            self.config.gui_font_size,
            self.config.world_width,
            self.config.world_height,
        )
        self.ui_sprites.add(self.ui, layer=10)

    @property
    def level_config(self):
        return LEVELS[self.level_index]

    @property
    def level_number(self):
        return self.level_index + 1

    def _create_guns(self) -> None:
        deagle_sound = self.shot_sound.copy()
        self.shot_sound.set_volume(0.1)

        glock = Gun(
            "Glock 19",
            self.glock_side_view_image,
            self.glock_top_view_image,
            self.bullet_image,
            self.config.bullet_damage,
            self.config.bullet_speed,
            self.config.fire_interval,
            15,
            1,
            self.shot_sound,
            self.reload_sound,
            self.all_sprites,
            self.player_bullets,
        )

        deagle_bullet = pygame.transform.scale_by(self.bullet_image, 1.5)
        deagle_sound.set_volume(1.0)

        desert_eagle = Gun(
            "Desert Eagle",
            self.deagle_side_view_image,
            self.deagle_top_view_image,
            deagle_bullet,
            self.config.bullet_damage * 2,
            self.config.bullet_speed * 2,
            self.config.fire_interval * 5,
            7,
            2,
            deagle_sound,
            self.reload_sound,
            self.all_sprites,
            self.player_bullets,
        )

        self.guns = [glock, desert_eagle]

    def handle_event(self, event: pygame.Event):
        match event.type:
            case pygame.MOUSEMOTION:
                self.mouse_pos = pygame.Vector2(event.pos)
            case pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.is_left_mouse = True
                if event.button == 5:
                    self.is_wheel_down = True
            case pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_left_mouse = False
            case pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.is_reload = True
                elif event.key == pygame.K_ESCAPE:
                    self.manager.switch("menu", game_in_progress=True)
            case self.SPAWN_ENEMY_EVENT:
                for mob_pos in random.choices(
                    self.mobs_positions, k=self.mobs_number
                ):
                    mob = Mob(
                        self.zombie_animations,
                        self.config.mob_max_hp,
                        mob_pos.copy(),
                        self.zombie_sound,
                        self.impact_sound,
                        self.config.tile_size,
                        random.uniform(*self.level_config["enemy_speed"]),
                        self.level_config["enemy_damage"],
                    )
                    self.enemies.add(mob)
                    self.all_sprites.add(mob, layer=3)

                self.mobs_number = min(
                    self.mobs_number + self.level_config["enemies_increment"],
                    MAX_MOBS_COUNT,
                )

    def _separate_enemies(self):
        mobs = list(self.enemies)
        for i in range(len(mobs)):
            for j in range(i + 1, len(mobs)):
                a, b = mobs[i], mobs[j]
                diff = a.pos - b.pos
                dist = diff.length()
                if 0 < dist < self.config.tile_size:
                    a.pos += diff / dist
                    b.pos -= diff / dist
        for mob in mobs:
            mob.rect.center = mob.pos

    def update(self, dt: float, *args, **kwargs):
        self.camera.update(self.player.rect)

        world_mouse_pos = self.mouse_pos + pygame.Vector2(
            self.camera.rect.x, self.camera.rect.y
        )

        self.all_sprites.update(
            dt,
            is_left_mouse=self.is_left_mouse,
            is_wheel_down=self.is_wheel_down,
            is_reload=self.is_reload,
            player=self.player,
            score=self.score,
            world_mouse_pos=world_mouse_pos,
        )

        self.ui_sprites.update(
            dt,
            player=self.player,
            score=self.score,
            enemies=self.enemies,
            items=self.items,
        )
        self._separate_enemies()

        self.is_wheel_down = False
        self.is_reload = False

        for picked_item in pygame.sprite.spritecollide(
            self.player, self.items, False, pygame.sprite.collide_mask
        ):
            picked_item.use(self.player)

        attackers: list[Mob] = pygame.sprite.spritecollide(
            self.player, self.enemies, False, pygame.sprite.collide_mask
        )
        for attacker in attackers:
            self.player.hit(attacker.damage)

        if self.player.is_dead:
            self.manager.switch(
                "gameover",
                final_score=self.score,
                reached_level=self.level_number,
            )

        enemies_hit: dict[Mob, list[Bullet]] = pygame.sprite.groupcollide(
            self.enemies,
            self.player_bullets,
            False,
            True,
            collided=pygame.sprite.collide_mask,
        )
        for enemy_hit, bullets_spent in enemies_hit.items():
            for bullet_spent in bullets_spent:
                is_dead = enemy_hit.hit(bullet_spent.damage)

                self.add_ground_effect(
                    GroundEffectTypes.BLOOD,
                    enemy_hit.pos,
                    bullet_spent.direction,
                    bullet_spent.speed / 2000.0,
                )
                if is_dead:
                    self.score += 1

                    threshold = self.level_config["threshold"]

                    if self.score >= threshold:
                        self._advance_level()

                    elif len(self.enemies) == 0 and self.score < threshold:
                        self.ui.flash_message(
                            f"Next wave in {MOB_SPAWN_DELAY_MS // 1000} seconds!"
                        )

                        pygame.time.set_timer(
                            self.SPAWN_ENEMY_EVENT, MOB_SPAWN_DELAY_MS, loops=1
                        )

                        self._spawn_items(enemy_hit.pos)
                    break

        for bullet in self.player_bullets:
            if not self.world_bounds.colliderect(bullet):
                bullet.kill()

    def _spawn_items(self, pos: pygame.Vector2) -> None:
        guess = random.randint(1, 10)

        match guess:
            case 8:
                medpack = Medpack(self.medpack_image, pos, 25)
                self.all_sprites.add(medpack, layer=2)
                self.items.add(medpack)

    def add_ground_effect(
        self,
        kind: GroundEffectTypes,
        pos: pygame.Vector2,
        direction: pygame.Vector2,
        scale: float,
    ):
        if len(self.ground_effects) == MAX_GROUND_EFFECTS:
            oldest = max(self.ground_effects, key=lambda s: s.age)
            oldest.kill()

        match kind:
            case GroundEffectTypes.BLOOD:
                splat = BloodSplat(
                    pos,
                    direction,
                    scale,
                    self.blood_splatter_image,
                )
                self.ground_effects.add(splat)
                self.all_sprites.add(splat)

    def draw(self, surf: pygame.Surface):
        surf.fill("black")
        surf.blit(
            self.background_image,
            self.camera.cut(self.background_image.get_rect()),
        )

        for sprite in pygame.sprite.spritecollide(
            self.camera, self.all_sprites, False
        ):
            surf.blit(sprite.image, self.camera.cut(sprite.rect))

        self.ui_sprites.draw(surf)

        pygame.display.flip()

    def on_enter(self, *args, do_reset: bool = True, **kwargs) -> None:
        pygame.mixer.music.stop()
        pygame.mixer.music.load("sounds/theme.wav")
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play(-1)
        pygame.mouse.set_visible(False)

        if do_reset:
            self.score = 0
            self.level_index = 0
            self.mobs_number = self.level_config["enemies_count"]

            self.ui.flash_message(f"LEVEL {self.level_number}")

            self._setup_level()

    def _setup_level(self):
        self.enemies.empty()
        self.ground_effects.empty()
        self.player_bullets.empty()
        self.items.empty()
        self.all_sprites.empty()

        self.is_left_mouse = False
        self.is_wheel_down = False
        self.is_reload = False

        player_pos = (
            self.player.pos
            if self.player is not None
            else pygame.Vector2(
                self.config.window_width // 2, self.config.window_height // 2
            )
        )

        self.player = Player(
            PLAYER_MAX_HP,
            player_pos,
            self.config.speed,
            self.player_animations,
            self.footsteps_sound,
            self.player_hit_sound,
            self.guns,
            self.config.world_width,
            self.config.world_height,
        )
        self.all_sprites.add(self.player, layer=3)

        pygame.event.post(pygame.event.Event(self.SPAWN_ENEMY_EVENT))

    def _advance_level(self) -> None:
        self.level_index += 1

        self.ui.flash_message(f"LEVEL {self.level_number}")

        if self.level_index == len(LEVELS):
            self.manager.switch(
                "victory",
                final_score=self.score,
                reached_level=self.level_number - 1,
            )
            return
        self._setup_level()
