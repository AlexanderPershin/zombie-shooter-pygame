import pygame

import utils
from animation import FRAME_COUNT, Animation
from config import Config
from scenes import (
    GameOverScene,
    GameScene,
    MainMenuScene,
    SceneManager,
    VictoryScene,
)


class Game:
    def __init__(self, config: Config):
        self.running = False
        self.config = config

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
        pygame.display.set_caption("Zombie Shooter")

        self.clock = pygame.time.Clock()

        self.dt = 0.0
        self.is_left_mouse = False
        self.is_wheel_down = False
        self.is_reload = False
        self.score = 0

        self._load_font()
        self._load_images()
        self._load_sounds()

        self.player_animations = {
            "idle": Animation(self.player_frames_idle, 150, loop=True),
            "locked": Animation(self.player_frames_locked, 150, loop=True),
            "attack": Animation(self.player_frames, 150, loop=True),
        }

        self.zombie_animations = {
            "idle": Animation(self.zombie_frames_idle, 200, loop=True),
            "walk": Animation(self.zombie_frames_walk, 150, loop=True),
            "attack": Animation(self.zombie_frames_attack, 100, loop=True),
        }

        self.manager = SceneManager(self.ui_sound)
        self.manager.register(
            "menu",
            MainMenuScene(
                self.manager,
                self.config,
                self.font,
                self.menu_image,
            ),
        )

        self.manager.register(
            "game",
            GameScene(
                self.manager,
                self.config,
                self.player_animations,
                self.zombie_animations,
                self.blood_splatter,
                self.bullet_image,
                self.glock_side_view_image,
                self.glock_top_view_image,
                self.desert_eagle_side_view_image,
                self.desert_eagle_top_view_image,
                self.background,
                self.medpack_image,
                self.crosshair_image,
                self.shot_sound,
                self.reload_sound,
                self.impact_sound,
                self.zombie_sound,
                self.footsteps_sound,
                self.player_hit_sound,
                self.font,
            ),
        )
        self.manager.register(
            "gameover",
            GameOverScene(
                self.manager,
                self.config,
                self.font,
            ),
        )
        self.manager.register(
            "victory",
            VictoryScene(
                self.manager,
                self.config,
                self.font,
            ),
        )
        self.manager.switch("menu")
        self.running = True

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
        self.menu_image = pygame.image.load(
            "images/main_menu.svg"
        ).convert_alpha()

    def _load_sounds(self) -> None:
        self.shot_sound = pygame.mixer.Sound("sounds/shot.wav")
        self.reload_sound = pygame.mixer.Sound("sounds/reloading.wav")
        self.impact_sound = pygame.mixer.Sound("sounds/impact.wav")
        self.zombie_sound = pygame.mixer.Sound("sounds/zombie.wav")
        self.footsteps_sound = pygame.mixer.Sound("sounds/footsteps.wav")
        self.player_hit_sound = pygame.mixer.Sound("sounds/player_hit.wav")
        self.ui_sound = pygame.mixer.Sound("sounds/ui.wav")

        pygame.mixer.music.load("sounds/theme.wav")
        pygame.mixer.music.play(-1)

    def run(self):
        while self.running:
            self.dt = self.clock.tick(self.config.fps) / 1000

            self.watch_for_events()

            self.update()

            self.draw()

    def watch_for_events(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case _:
                    self.manager.handle_event(event)

    def update(self):
        self.manager.update(self.dt, screen_rect=self.screen.get_rect())

    def draw(self):
        self.screen.fill("black")

        self.manager.draw(self.screen)

        pygame.display.flip()
