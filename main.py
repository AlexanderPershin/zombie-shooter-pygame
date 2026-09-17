import random

import pygame
import typer

import utils
from config import Config
from enemies import Mob

FRAME_COUNT = 8
ANIMATION_SPEED_MS = 150
BULLET_SPAWN_OFFSET = 32
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

        self.player_max_hp = 100
        self.player_hp = 100
        self.invincible_timer = 0.0
        self.invincible_duration = 0.5

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

        self.player_pos = pygame.Vector2(self.screen.get_rect().center)
        self.mouse_pos = pygame.Vector2()
        self.bullets: list[dict[str, pygame.Vector2]] = []
        self.fire_cooldown = 0.0

        self.enemies: list[Mob] = []

        self.dt = 0.0
        self.is_left_mouse = False
        self.score = 0
        self.keys = pygame.key.get_pressed()

        self._load_font()
        self._load_images()
        self._load_sounds()

        self.current_frame = 0
        self.player = self.frames[self.current_frame]
        self.player_rect = self.player.get_rect(center=self.player_pos)

        self.animation_timer = 0
        self.was_moving = False

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
        self.frames = utils.load_sprite_frames(
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
                case pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.is_left_mouse = False
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
        self.player_pos += move * self.config.speed * self.dt

        direction = utils.aim_direction(self.player_pos, self.mouse_pos)
        angle = utils.direction_to_angle(direction)

        if self.is_left_mouse and not self.game_over:
            self.fire_cooldown -= self.dt
            if self.fire_cooldown <= 0:
                self.shot_sound.play()
                self.bullets.append(
                    {
                        "pos": self.player_pos
                        + direction * BULLET_SPAWN_OFFSET,
                        "dir": pygame.Vector2(direction),
                    }
                )
                self.fire_cooldown = self.config.fire_interval
        else:
            self.fire_cooldown = 0.0

        if self.invincible_timer > 0:
            self.invincible_timer -= self.dt

        for enemy in self.enemies:
            if enemy.is_alive and enemy.rect.colliderect(self.player_rect):
                if self.invincible_timer <= 0:
                    self.player_hp -= 10
                    self.invincible_timer = self.invincible_duration
                    if self.player_hp <= 0:
                        self.player_hp = 0
                        self.game_over = True
                        return

                    offset = enemy.pos - self.player_pos
                    if offset.length_squared() > 1:
                        direction_away = offset.normalize()
                        enemy.pos += direction_away * 30
                    else:
                        enemy.pos.x += 20
                        enemy.pos.y += 20

                    direction_away = (enemy.pos - self.player_pos).normalize()
                    enemy.pos += direction_away * 30

        if not self.game_over:
            for enemy in self.enemies:
                enemy.update(self.player_pos, self.dt)

        for bullet in self.bullets[:]:
            bullet["pos"] += bullet["dir"] * self.config.bullet_speed * self.dt

            if not self.screen_bounds.collidepoint(bullet["pos"]):
                self.bullets.remove(bullet)
                continue

            hit_occurred = False
            for enemy in self.enemies[:]:
                if enemy.is_alive and enemy.check_hit(bullet["pos"]):
                    enemy.hit(self.config.bullet_damage)

                    if not enemy.is_alive:
                        self.score += 1
                        self.enemies.remove(enemy)

                    if not self.enemies:
                        pygame.time.set_timer(
                            self.SPAWN_ENEMY_EVENT, MOB_SPAWN_DELAY_MS, loops=1
                        )
                    hit_occurred = True
                    break

            if hit_occurred:
                self.bullets.remove(bullet)

        self._update_footsteps(move)
        self._update_animation(move)

        self.player = pygame.transform.rotate(
            self.frames[self.current_frame], angle - 90
        )
        self.player_rect = self.player.get_rect(center=self.player_pos)
        self.crosshair_rect = self.crosshair_image.get_rect(
            center=self.mouse_pos
        )

    def _update_footsteps(self, move: pygame.Vector2) -> None:
        is_moving = move.length_squared() > 0

        if is_moving and not self.was_moving:
            self.footsteps_sound.play(-1)
        elif not is_moving and self.was_moving:
            self.footsteps_sound.stop()

        self.was_moving = is_moving

    def _update_animation(self, move: pygame.Vector2) -> None:
        if move.length_squared() > 0:
            self.animation_timer += self.dt * 1000
            if self.animation_timer >= ANIMATION_SPEED_MS:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % FRAME_COUNT
        else:
            self.current_frame = 0

    def draw_player_hp(self):
        bar_width = 200
        bar_height = 20
        x = 10
        y = self.screen.get_rect().height - 50
        pygame.draw.rect(self.screen, "#330000", (x, y, bar_width, bar_height))
        fill = int(bar_width * self.player_hp / self.player_max_hp)
        pygame.draw.rect(self.screen, "#00cc00", (x, y, fill, bar_height))
        hp_text = self.font.render(
            f"HP: {self.player_hp}", False, self.config.gui_text_color
        )
        self.screen.blit(hp_text, (x, y - 25))

    def display_hud(self):
        score_text = self.font.render(
            f"Score: {self.score}",
            antialias=False,
            color=self.config.gui_text_color,
        )
        self.screen.blit(score_text, score_text.get_rect(left=10, top=10))
        self.draw_player_hp()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.display_hud()

        if not self.game_over:
            self.screen.blit(self.player, self.player_rect)

        for bullet in self.bullets:
            phi = bullet["dir"].as_polar()[1]
            rotated_bullet = pygame.transform.rotate(
                self.bullet_image, -phi - 90
            )
            self.screen.blit(
                rotated_bullet,
                rotated_bullet.get_rect(center=bullet["pos"]),
            )

        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.screen.blit(self.crosshair_image, self.crosshair_rect)
        pygame.display.flip()


def run_game(config: Config):
    with Game(config) as game:
        game.run()


if __name__ == "__main__":
    typer.run(main)
