import pygame
import typer

from config import Config

FRAME_COUNT = 8
ANIMATION_SPEED_MS = 150
BULLET_SPAWN_OFFSET = 32
MOB_SPAWN_DELAY_MS = 3000
MOB_HP_DEAD = -1
HP_BAR_HEIGHT = 6
HP_BAR_OFFSET = 10
BULLET_SCREEN_MARGIN = 40

CONFIG = Config.load_from_ini()


def get_movement_direction(keys: pygame.key.ScancodeWrapper) -> pygame.Vector2:
    move = pygame.Vector2()

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        move.y -= 1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        move.y += 1
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        move.x -= 1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        move.x += 1

    if move.length_squared() > 0:
        move.normalize_ip()

    return move


def aim_direction(
    from_pos: pygame.Vector2, to_pos: pygame.Vector2
) -> pygame.Vector2:
    to_target = to_pos - from_pos
    if to_target.length_squared():
        return to_target.normalize()
    return pygame.Vector2(1, 0)


def direction_to_angle(direction: pygame.Vector2) -> float:
    return -direction.as_polar()[1]


def load_sprite_frames(
    sprite_sheet: pygame.Surface, frame_count: int, tile_size: int
) -> list[pygame.Surface]:
    frame_width = sprite_sheet.get_width() // frame_count
    frame_height = sprite_sheet.get_height()
    frames = []

    for i in range(frame_count):
        frame_surface = pygame.Surface(
            (frame_width, frame_height), pygame.SRCALPHA
        )
        frame_surface.blit(
            sprite_sheet,
            (0, 0),
            (i * frame_width, 0, frame_width, frame_height),
        )
        frames.append(
            pygame.transform.scale(frame_surface, (tile_size, tile_size))
        )

    return frames


def tile_background(
    land_image: pygame.Surface, width: int, height: int
) -> pygame.Surface:
    bg_surface = pygame.Surface((width, height))
    tile_w = land_image.get_width()
    tile_h = land_image.get_height()

    for y in range(0, height, tile_h):
        for x in range(0, width, tile_w):
            bg_surface.blit(land_image, (x, y))

    return bg_surface


def mob_rect(pos: pygame.Vector2, tile_size: int) -> pygame.Rect:
    half = tile_size / 2
    return pygame.Rect(pos.x - half, pos.y - half, tile_size, tile_size)


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
        gui_font_size=gui_font_size,
        gui_text_color=gui_text_color,
    )

    run_game(config)


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

        self.SPAWN_ENEMY_EVENT = pygame.event.custom_type()

        self.screen = pygame.display.set_mode(
            (self.config.window_width, self.config.window_height)
        )
        pygame.display.set_caption("OOP Shooter")

        self.clock = pygame.time.Clock()
        self.screen_bounds = self.screen.get_rect().inflate(
            BULLET_SCREEN_MARGIN, BULLET_SCREEN_MARGIN
        )

        self.player_pos = pygame.Vector2(self.screen.get_rect().center)
        self.mouse_pos = pygame.Vector2()
        self.bullets: list[dict[str, pygame.Vector2]] = []
        self.fire_cooldown = 0.0
        self.mob_pos = pygame.Vector2(
            self.config.window_width * 0.75, self.config.window_height // 2
        )
        self.mob_hp = self.config.mob_max_hp
        self.dt = 0.0
        self.is_left_mouse = False
        self.score = 0
        self.keys = pygame.key.get_pressed()

        self._load_font()
        self._load_images()
        self._load_sounds()

        self.current_frame = 0
        self.animation_timer = 0
        self.was_moving = False
        self.running = True

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
        self.frames = load_sprite_frames(
            player_sprite_sheet, FRAME_COUNT, self.config.tile_size
        )

        self.zombie_image = pygame.transform.scale(
            pygame.image.load("images/zombie.svg").convert_alpha(),
            (self.config.tile_size, self.config.tile_size),
        )
        self.bullet_image = pygame.image.load(
            "images/bullet.svg"
        ).convert_alpha()

        land_image = pygame.image.load("images/land.svg").convert_alpha()
        self.background = tile_background(
            land_image, self.config.window_width, self.config.window_height
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
                    if self.mob_hp == MOB_HP_DEAD:
                        self.zombie_sound.play()
                        self.mob_hp = self.config.mob_max_hp

        self.keys = pygame.key.get_pressed()

    def update(self):
        move = get_movement_direction(self.keys)
        self.player_pos += move * self.config.speed * self.dt

        direction = aim_direction(self.player_pos, self.mouse_pos)
        angle = direction_to_angle(direction)

        if self.is_left_mouse:
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

        current_mob_rect = (
            mob_rect(self.mob_pos, self.config.tile_size)
            if self.mob_hp > 0
            else None
        )
        self.bullets = self._update_bullets(current_mob_rect)

        self._update_footsteps(move)
        self._update_animation(move)

        self.player = pygame.transform.rotate(
            self.frames[self.current_frame], angle - 90
        )
        self.player_rect = self.player.get_rect(center=self.player_pos)
        self.crosshair_rect = self.crosshair_image.get_rect(
            center=self.mouse_pos
        )

    def _update_bullets(
        self, current_mob_rect: pygame.Rect | None
    ) -> list[dict[str, pygame.Vector2]]:
        remaining_bullets = []

        for bullet in self.bullets:
            bullet["pos"] += bullet["dir"] * self.config.bullet_speed * self.dt

            if not self.screen_bounds.collidepoint(bullet["pos"]):
                continue

            if current_mob_rect and current_mob_rect.collidepoint(
                bullet["pos"]
            ):
                self.mob_hp = max(self.mob_hp - self.config.bullet_damage, 0)
                self.impact_sound.play()

                if self.mob_hp == 0:
                    self.score += 1
                    pygame.time.set_timer(
                        self.SPAWN_ENEMY_EVENT, MOB_SPAWN_DELAY_MS, loops=1
                    )
                    self.mob_hp = MOB_HP_DEAD
                continue

            remaining_bullets.append(bullet)

        return remaining_bullets

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

    def display_hud(self):
        score_text = self.font.render(
            f"Score: {self.score}",
            antialias=False,
            color=self.config.gui_text_color,
        )
        self.screen.blit(score_text, score_text.get_rect(left=0, top=0))

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.display_hud()
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

        if self.mob_hp > 0:
            self.draw_mob(self.mob_pos, self.mob_hp)

        self.screen.blit(self.crosshair_image, self.crosshair_rect)
        pygame.display.flip()

    def draw_mob(self, pos: pygame.Vector2, hp: int):
        direction = aim_direction(pos, self.player_pos)
        rotation_angle = direction_to_angle(direction) - 90

        rotated_image = pygame.transform.rotate(
            self.zombie_image, rotation_angle
        )
        self.screen.blit(rotated_image, rotated_image.get_rect(center=pos))

        half = self.config.tile_size / 2
        bar_width = self.config.tile_size
        bar_x = pos.x - half
        bar_y = pos.y - half - HP_BAR_OFFSET

        pygame.draw.rect(
            self.screen, "#330000", (bar_x, bar_y, bar_width, HP_BAR_HEIGHT)
        )
        if hp > 0:
            fill_width = int(bar_width * hp / self.config.mob_max_hp)
            pygame.draw.rect(
                self.screen,
                "#fa5252",
                (bar_x, bar_y, fill_width, HP_BAR_HEIGHT),
            )


def run_game(config: Config):
    with Game(config) as game:
        game.run()


if __name__ == "__main__":
    typer.run(main)
