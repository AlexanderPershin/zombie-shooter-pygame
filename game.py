import random

import pygame

import utils
from animation import FRAME_COUNT, Animation
from bullet import Bullet
from camera import Camera
from config import Config
from crosshair import Crosshair
from effects import BloodSplat, GroundEffectTypes
from enemies import Mob
from guns import Gun
from items import Item, Medpack
from player import Player
from ui import Ui

MOB_SPAWN_DELAY_MS = 3000
SCREEN_MARGIN = 100
MAX_GROUND_EFFECTS = 500
MAX_MOBS_COUNT = 100


class Game:
    def __init__(self, config: Config):
        self.running = False
        self.config = config

        self.SPAWN_ENEMY_EVENT = pygame.event.custom_type()

        self.game_over = False

    def __enter__(self):
        pygame.mixer.pre_init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=512,
            allowedchanges=pygame.AUDIO_ALLOW_ANY_CHANGE,
        )
        pygame.init()
        pygame.mixer.set_num_channels(16)

        self.flags = 0
        if self.config.fullscreen:
            self.flags |= pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(
            (self.config.window_width, self.config.window_height),
            flags=self.flags,
        )
        pygame.display.set_caption("Shooter")

        self.clock = pygame.time.Clock()

        self.world_bounds = pygame.Rect(
            0, 0, self.config.world_width, self.config.world_height
        ).inflate(SCREEN_MARGIN, SCREEN_MARGIN)

        self.mouse_pos = pygame.Vector2()

        self.dt = 0.0
        self.is_left_mouse = False
        self.is_wheel_down = False
        self.is_reload = False
        self.score = 0
        self.keys = pygame.key.get_pressed()

        self._load_font()
        self._load_images()
        self._load_sounds()

        player_pos = pygame.Vector2(
            self.screen.get_rect().center,
        )

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.ground_effects = pygame.sprite.Group()
        self.ui_sprites = pygame.sprite.LayeredUpdates()

        self.player_bullets: pygame.sprite.Group[Bullet] = (
            pygame.sprite.Group()
        )
        self.enemies: pygame.sprite.Group[Mob] = pygame.sprite.Group()
        self.items: pygame.sprite.Group[Item] = pygame.sprite.Group()

        self._create_guns()

        player_animations = {
            "idle": Animation(self.player_frames_idle, 150, loop=True),
            "locked": Animation(self.player_frames_locked, 150, loop=True),
            "attack": Animation(self.player_frames, 150, loop=True),
        }
        self.player = Player(
            120,
            player_pos,
            self.config.speed,
            player_animations,
            self.footsteps_sound,
            self.player_hit_sound,
            self.guns,
            self.config.world_width,
            self.config.world_height,
        )
        self.all_sprites.add(self.player, layer=3)

        self.zombie_animations = {
            "idle": Animation(self.zombie_frames_idle, 200, loop=True),
            "walk": Animation(self.zombie_frames_walk, 150, loop=True),
            "attack": Animation(self.zombie_frames_attack, 100, loop=True),
        }

        self.mobs_positions: list[pygame.Vector2] = (
            utils.generate_mobs_positions(
                self.config.tile_size,
                self.config.world_width,
                self.config.world_height,
                SCREEN_MARGIN,
            )
        )

        self.mobs_number = 3

        pygame.event.post(pygame.event.Event(self.SPAWN_ENEMY_EVENT))

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

        self.running = True

        self.is_paused = False

        return self

    def __exit__(self, *args):
        pygame.quit()

    def _load_font(self) -> None:
        self.font = pygame.font.Font(
            "fonts/BlackOpsOne-Regular.ttf", self.config.gui_font_size
        )

    def _load_images(self) -> None:
        # Player animations
        player_sprite_sheet_idle = pygame.image.load(
            "images/character_sprite_idle.svg"
        ).convert_alpha()
        self.player_frames_idle = utils.load_sprite_frames(
            player_sprite_sheet_idle, FRAME_COUNT, self.config.tile_size
        )

        player_sprite_sheet_locked = pygame.image.load(
            "images/character_sprite_locked.svg"
        ).convert_alpha()
        self.player_frames_locked = utils.load_sprite_frames(
            player_sprite_sheet_locked, FRAME_COUNT, self.config.tile_size
        )

        player_sprite_sheet = pygame.image.load(
            "images/character_sprite_attack.svg"
        ).convert_alpha()
        self.player_frames = utils.load_sprite_frames(
            player_sprite_sheet, FRAME_COUNT, self.config.tile_size
        )

        # Zombie animations
        zombie_sprite_sheet_idle = pygame.image.load(
            "images/zombie_sprite_idle.svg"
        ).convert_alpha()
        self.zombie_frames_idle = utils.load_sprite_frames(
            zombie_sprite_sheet_idle, FRAME_COUNT, self.config.tile_size
        )

        zombie_sprite_sheet_walk = pygame.image.load(
            "images/zombie_sprite_walk.svg"
        ).convert_alpha()
        self.zombie_frames_walk = utils.load_sprite_frames(
            zombie_sprite_sheet_walk, FRAME_COUNT, self.config.tile_size
        )

        zombie_sprite_sheet_attack = pygame.image.load(
            "images/zombie_sprite_attack.svg"
        ).convert_alpha()
        self.zombie_frames_attack = utils.load_sprite_frames(
            zombie_sprite_sheet_attack, FRAME_COUNT, self.config.tile_size
        )

        self.blood_splatter = pygame.image.load("images/blood_splatter.svg")

        self.bullet_image = pygame.image.load(
            "images/bullet.svg"
        ).convert_alpha()

        self.glock_side_view_image = pygame.image.load(
            "images/glock_side_view.svg"
        ).convert_alpha()
        self.glock_top_view_image = pygame.image.load(
            "images/glock_top_view.svg"
        ).convert_alpha()

        self.desert_eagle_side_view_image = pygame.image.load(
            "images/desert_eagle_side_view.svg"
        ).convert_alpha()
        self.desert_eagle_top_view_image = pygame.image.load(
            "images/desert_eagle_top_view.svg"
        ).convert_alpha()

        land_images: pygame.Surface = []
        for i in range(1, 6):
            land_image = pygame.image.load(
                f"images/land/land{i}.svg"
            ).convert()
            land_images.append(land_image)

        self.background = utils.tile_background(
            land_images, self.config.world_width, self.config.world_height
        )

        self.medpack_image = pygame.image.load(
            "images/medpack.svg"
        ).convert_alpha()

        self.crosshair_image = pygame.transform.scale(
            pygame.image.load("images/crosshair.svg").convert_alpha(),
            (self.config.tile_size, self.config.tile_size),
        )
        pygame.mouse.set_visible(False)

    def _load_sounds(self) -> None:
        self.shot_sound = pygame.mixer.Sound("sounds/shot.wav")
        self.reload_sound = pygame.mixer.Sound("sounds/reloading.wav")
        self.impact_sound = pygame.mixer.Sound("sounds/impact.wav")
        self.zombie_sound = pygame.mixer.Sound("sounds/zombie.wav")
        self.footsteps_sound = pygame.mixer.Sound("sounds/footsteps.wav")
        self.player_hit_sound = pygame.mixer.Sound("sounds/player_hit.wav")

        pygame.mixer.music.load("sounds/theme.wav")
        pygame.mixer.music.play(-1)

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
            self.desert_eagle_side_view_image,
            self.desert_eagle_top_view_image,
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

    def run(self):
        while self.running:
            self.dt = self.clock.tick(self.config.fps) / 1000
            self.watch_for_events()

            if not self.is_paused:
                self.update()

            # self.update()
            self.draw()

    def watch_for_events(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
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
                    elif event.key == pygame.K_p:
                        self.is_paused = not self.is_paused
                case self.SPAWN_ENEMY_EVENT:
                    for y_pos in random.choices(
                        self.mobs_positions, k=self.mobs_number
                    ):
                        mob = Mob(
                            self.zombie_animations,
                            self.config.mob_max_hp,
                            y_pos.copy(),
                            self.zombie_sound,
                            self.impact_sound,
                            self.config.tile_size,
                            self.config.mob_speed,
                            10,
                        )
                        self.enemies.add(mob)
                        self.all_sprites.add(mob, layer=3)
                    self.mobs_number = min(
                        self.mobs_number + 10,
                        MAX_MOBS_COUNT,
                    )

        self.keys = pygame.key.get_pressed()

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

    def update(self):
        self.camera.update(self.player.rect)

        world_mouse_pos = self.mouse_pos + pygame.Vector2(
            self.camera.rect.x, self.camera.rect.y
        )

        if not self.game_over:
            self.all_sprites.update(
                self.dt,
                is_left_mouse=self.is_left_mouse,
                is_wheel_down=self.is_wheel_down,
                is_reload=self.is_reload,
                player=self.player,
                score=self.score,
                world_mouse_pos=world_mouse_pos,
            )

            self.ui_sprites.update(
                self.dt,
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

        self.game_over = self.player.is_dead

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

                    if len(self.enemies) == 0:
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
                    self.blood_splatter,
                )
                self.ground_effects.add(splat)
                self.all_sprites.add(splat)

    def draw(self):
        self.screen.fill("black")
        self.screen.blit(
            self.background,
            self.camera.cut(self.background.get_rect()),
        )

        for sprite in pygame.sprite.spritecollide(
            self.camera, self.all_sprites, False
        ):
            self.screen.blit(sprite.image, self.camera.cut(sprite.rect))

        self.ui_sprites.draw(self.screen)

        pygame.display.flip()
