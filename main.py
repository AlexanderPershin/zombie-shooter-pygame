import random

import pygame
import typer

import utils
from config import Config
from enemies import Mob
from guns import Gun
from items import Item, Medpack
from player import FRAME_COUNT, Player

MOB_SPAWN_DELAY_MS = 3000
SCREEN_MARGIN = 40

CONFIG = Config.load_from_ini()


def main(
    width: int | None = typer.Option(None, "--width"),
    height: int | None = typer.Option(None, "--height"),
    fps: int | None = typer.Option(None, "--fps"),
    speed: int | None = typer.Option(None, "--speed"),
    tile_size: int | None = typer.Option(None, "--tile-size"),
    bullet_speed: int | None = typer.Option(None, "--bullet-speed"),
    bullet_damage: int | None = typer.Option(None, "--bullet-damage"),
    fire_interval: int | None = typer.Option(None, "--fire-interval"),
    mob_max_hp: int | None = typer.Option(None, "--mob-max-hp"),
    mob_speed: int | None = typer.Option(None, "--mob-speed"),
    gui_font_size: int | None = typer.Option(None, "--gui-font-size"),
    gui_text_color: str | None = typer.Option(None, "--gui-text-color"),
):
    config = CONFIG.parse_cli(
        window_width=width,
        window_height=height,
        fps=fps,
        speed=speed,
        tile_size=tile_size,
        bullet_speed=bullet_speed,
        bullet_damage=bullet_damage,
        fire_interval=fire_interval,
        mob_max_hp=mob_max_hp,
        mob_speed=mob_speed,
        gui_font_size=gui_font_size,
        gui_text_color=gui_text_color,
    )

    run_game(config)


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

        self.screen = pygame.display.set_mode(
            (self.config.window_width, self.config.window_height)
        )
        pygame.display.set_caption("OOP Shooter")

        self.clock = pygame.time.Clock()
        self.screen_bounds = self.screen.get_rect().inflate(
            SCREEN_MARGIN, SCREEN_MARGIN
        )

        self.mouse_pos = pygame.Vector2()

        self.enemies: list[Mob] = []
        self.items: list[Item] = []

        self.dt = 0.0
        self.is_left_mouse = False
        self.is_wheel_down = False
        self.is_reload = False
        self.score = 0
        self.keys = pygame.key.get_pressed()

        self._load_font()
        self._load_images()
        self._load_sounds()
        self._create_guns()

        player_pos = pygame.Vector2(
            self.screen.get_rect().center,
        )

        self.player = Player(
            120,
            player_pos,
            self.config.speed,
            self.player_frames,
            self.footsteps_sound,
            self.guns,
        )

        self.running = True

        self.mobs_positions: list[pygame.Vector2] = (
            utils.generate_mobs_positions(
                self.config.tile_size,
                self.config.window_width,
                self.config.window_height,
                SCREEN_MARGIN,
            )
        )

        pygame.event.post(pygame.event.Event(self.SPAWN_ENEMY_EVENT))

        return self

    def __exit__(self, *args):
        pygame.quit()

    def _load_font(self) -> None:
        self.font = pygame.font.Font(
            "fonts/BlackOpsOne-Regular.ttf", self.config.gui_font_size
        )

    def _load_images(self) -> None:
        player_sprite_sheet = pygame.image.load(
            "images/character_sprite.svg"
        ).convert_alpha()
        self.player_frames = utils.load_sprite_frames(
            player_sprite_sheet, FRAME_COUNT, self.config.tile_size
        )

        self.zombie_image = pygame.transform.scale(
            pygame.image.load("images/zombie.svg").convert_alpha(),
            (self.config.tile_size, self.config.tile_size),
        )
        self.bullet_image = pygame.image.load(
            "images/bullet.svg"
        ).convert_alpha()

        land_images: pygame.Surface = []
        for i in range(1, 6):
            land_image = pygame.image.load(
                f"images/land/land{i}.svg"
            ).convert()
            land_images.append(land_image)

        self.background = utils.tile_background(
            land_images, self.config.window_width, self.config.window_height
        )

        self.medpack_image = pygame.image.load(
            "images/medpack.svg"
        ).convert_alpha()

        self.crosshair_image = pygame.transform.scale2x(
            pygame.image.load("images/crosshair.svg").convert_alpha()
        )
        pygame.mouse.set_visible(False)

    def _load_sounds(self) -> None:
        self.shot_sound = pygame.mixer.Sound("sounds/shot.wav")
        self.impact_sound = pygame.mixer.Sound("sounds/impact.wav")
        self.zombie_sound = pygame.mixer.Sound("sounds/zombie.wav")
        self.footsteps_sound = pygame.mixer.Sound("sounds/footsteps.wav")

        pygame.mixer.music.load("sounds/theme.wav")
        pygame.mixer.music.play(-1)

    def _create_guns(self) -> None:
        deagle_sound = self.shot_sound.copy()
        self.shot_sound.set_volume(0.1)

        glock = Gun(
            "Glock 19",
            self.bullet_image,
            self.config.bullet_damage,
            self.config.bullet_speed,
            self.config.fire_interval,
            15,
            1,
            self.shot_sound,
        )

        deagle_bullet = pygame.transform.scale_by(self.bullet_image, 1.5)
        deagle_sound.set_volume(1.0)

        desert_eagle = Gun(
            "Desert Eagle",
            deagle_bullet,
            self.config.bullet_damage * 2,
            self.config.bullet_speed * 2,
            self.config.fire_interval * 5,
            7,
            2,
            deagle_sound,
        )

        self.guns = [glock, desert_eagle]

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
                case self.SPAWN_ENEMY_EVENT:
                    for y_pos in random.choices(self.mobs_positions, k=3):
                        self.enemies.append(
                            Mob(
                                self.zombie_image,
                                self.config.mob_max_hp,
                                y_pos.copy(),
                                self.zombie_sound,
                                self.impact_sound,
                                self.config.tile_size,
                                self.config.mob_speed,
                            )
                        )

        self.keys = pygame.key.get_pressed()

    def update(self):
        move = utils.get_movement_direction(self.keys)

        if not self.game_over:
            self.player.update(
                move,
                self.is_left_mouse,
                self.is_wheel_down,
                self.is_reload,
                self.mouse_pos,
                self.dt,
            )
            self.game_over = self.player.is_dead
            self.is_wheel_down = False
            self.is_reload = False

        for item in self.items[:]:
            is_used = item.use(self.player)
            if is_used:
                self.items.remove(item)

        for enemy in self.enemies:
            self.player.hit(enemy.rect, self.config.bullet_damage)

        if not self.game_over:
            for enemy in self.enemies:
                enemy.update(self.player.rect, self.dt)

        for bullet in self.player.bullets[:]:
            if not self.screen_bounds.collidepoint(bullet.pos):
                self.player.bullets.remove(bullet)
                continue

            is_hit = False
            for enemy in self.enemies[:]:
                is_hit = enemy.hit(bullet.pos, bullet.damage)

                if not enemy.is_alive:
                    self.score += 1

                    n = random.randint(0, 4)
                    if n == 2:
                        medpack = Medpack(self.medpack_image, enemy.pos, 25)
                        self.items.append(medpack)

                    self.enemies.remove(enemy)

                if not self.enemies:
                    pygame.time.set_timer(
                        self.SPAWN_ENEMY_EVENT, MOB_SPAWN_DELAY_MS, loops=1
                    )

            if is_hit:
                self.player.bullets.remove(bullet)

        self.crosshair_rect = self.crosshair_image.get_rect(
            center=self.mouse_pos
        )

    def _draw_hp_bar(
        self,
        x: int,
        y: int,
        font: pygame.font.Font,
        color: str,
    ):
        bar_width = 200
        bar_height = 20

        pygame.draw.rect(self.screen, "#330000", (x, y, bar_width, bar_height))

        fill = int(bar_width * self.player.hp / self.player.max_hp)
        pygame.draw.rect(self.screen, "#00cc00", (x, y, fill, bar_height))

        hp_text = font.render(f"HP: {self.player.hp}", False, color)
        self.screen.blit(hp_text, (x, y - 25))

    def display_hud(self):
        score_text = self.font.render(
            f"Score: {self.score}",
            antialias=False,
            color=self.config.gui_text_color,
        )
        self.screen.blit(score_text, score_text.get_rect(left=10, top=10))

        x = 10
        y = self.screen.get_rect().height - 50
        self._draw_hp_bar(x, y, self.font, self.config.gui_text_color)

        gun_info = self.font.render(
            str(self.player.gun),
            self.config.gui_font_size,
            self.config.gui_text_color,
        )
        y = self.screen.get_rect().height - 125
        self.screen.blit(gun_info, (x, y))

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.display_hud()

        if not self.game_over:
            self.player.draw(self.screen)

        for item in self.items:
            item.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.screen.blit(self.crosshair_image, self.crosshair_rect)
        pygame.display.flip()


def run_game(config: Config):
    with Game(config) as game:
        game.run()


if __name__ == "__main__":
    typer.run(main)
