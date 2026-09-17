import pygame
import typer

from config import Config

SPAWN_ENEMY_EVENT = pygame.event.custom_type()


def draw_mob(screen, image, pos, player_pos, hp, max_hp, tile_size):
    to_player = player_pos - pos
    if to_player.length_squared() > 0:
        direction = to_player.normalize()
    else:
        direction = pygame.Vector2(1, 0)

    angle = -direction.as_polar()[1]
    rotation_angle = angle - 90

    rotated_image = pygame.transform.rotate(image, rotation_angle)
    image_rect = rotated_image.get_rect(center=pos)
    screen.blit(rotated_image, image_rect)

    half = tile_size / 2
    bar_width = tile_size
    bar_height = 6
    bar_x = pos.x - half
    bar_y = pos.y - half - 10

    pygame.draw.rect(screen, "#330000", (bar_x, bar_y, bar_width, bar_height))
    if hp > 0:
        fill_width = int(bar_width * hp / max_hp)
        pygame.draw.rect(
            screen, "#fa5252", (bar_x, bar_y, fill_width, bar_height)
        )


def tile_background(
    land_image: pygame.Surface, screen_width: int, screen_height: int
) -> pygame.Surface:
    bg_surface = pygame.Surface((screen_width, screen_height))
    tile_w = land_image.get_width()
    tile_h = land_image.get_height()

    for y in range(0, screen_height, tile_h):
        for x in range(0, screen_width, tile_w):
            bg_surface.blit(land_image, (x, y))

    return bg_surface


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


def run_game(config: Config):
    pygame.mixer.pre_init(
        frequency=44100,
        size=-16,
        channels=2,
        buffer=512,
        allowedchanges=pygame.AUDIO_ALLOW_ANY_CHANGE,
    )
    pygame.init()

    pygame.mixer.set_num_channels(16)

    screen = pygame.display.set_mode(
        (config.window_width, config.window_height)
    )

    pygame.display.set_caption("Sounds")

    clock = pygame.time.Clock()

    player_pos = pygame.Vector2(screen.get_rect().center)

    mouse_pos = pygame.Vector2()

    bullets = []
    fire_cooldown = 0.0

    mob_pos = pygame.Vector2(
        config.window_width * 0.75, config.window_height // 2
    )
    mob_hp = config.mob_max_hp

    dt = 0

    running = True

    is_left_mouse = False

    score = 0

    font = pygame.font.Font(
        "fonts/BlackOpsOne-Regular.ttf", config.gui_font_size
    )

    player_sprite_sheet = pygame.image.load(
        "images/character_sprite.svg"
    ).convert_alpha()

    FRAME_COUNT = 8
    FRAME_WIDTH = player_sprite_sheet.get_width() // FRAME_COUNT
    FRAME_HEIGHT = player_sprite_sheet.get_height()

    frames = []
    for i in range(FRAME_COUNT):
        frame_surface = pygame.Surface(
            (FRAME_WIDTH, FRAME_HEIGHT), pygame.SRCALPHA
        )
        frame_surface.blit(
            player_sprite_sheet,
            (0, 0),
            (i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT),
        )
        frame_surface = pygame.transform.scale(
            frame_surface, (config.tile_size, config.tile_size)
        )
        frames.append(frame_surface)

    current_frame = 0
    animation_timer = 0
    ANIMATION_SPEED = 150

    zombie_image = pygame.image.load("images/zombie.svg").convert_alpha()
    zombie_image = pygame.transform.scale(
        zombie_image, (config.tile_size, config.tile_size)
    )

    bullet_image = pygame.image.load("images/bullet.svg").convert_alpha()

    land_image = pygame.image.load("images/land.svg").convert_alpha()
    background = tile_background(
        land_image, config.window_width, config.window_height
    )

    crosshair_image = pygame.image.load("images/crosshair.svg").convert_alpha()
    crosshair_image = pygame.transform.scale2x(crosshair_image)
    pygame.mouse.set_visible(False)

    shot_sound = pygame.mixer.Sound("sounds/shot.wav")
    impact_sound = pygame.mixer.Sound("sounds/impact.wav")
    zombie_sound = pygame.mixer.Sound("sounds/zombie.wav")

    footsteps_sound = pygame.mixer.Sound("sounds/footsteps.wav")

    pygame.mixer.music.load("sounds/theme.wav")
    pygame.mixer.music.play(-1)

    was_moving = False

    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.MOUSEMOTION:
                    mouse_pos = pygame.Vector2(event.pos)
                case pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        is_left_mouse = True
                case pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        is_left_mouse = False
                case SPAWN_ENEMY_EVENT:
                    if mob_hp == -1:
                        zombie_sound.play()
                        mob_hp = config.mob_max_hp

        keys = pygame.key.get_pressed()

        move = pygame.Vector2()

        if keys[pygame.K_w]:
            move.y -= 1
        if keys[pygame.K_s]:
            move.y += 1
        if keys[pygame.K_a]:
            move.x -= 1
        if keys[pygame.K_d]:
            move.x += 1

        if move.length_squared() > 0:
            move.normalize_ip()

        player_pos += move * config.speed * dt

        to_mouse = mouse_pos - player_pos

        if to_mouse.length_squared():
            direction = to_mouse.normalize()
        else:
            direction = pygame.Vector2(1, 0)

        angle = -direction.as_polar()[1]

        bullet_pos = player_pos + direction * 32

        if is_left_mouse:
            fire_cooldown -= dt
            if fire_cooldown <= 0:
                shot_sound.play()
                bullets.append(
                    {
                        "pos": pygame.Vector2(bullet_pos),
                        "dir": pygame.Vector2(direction),
                    }
                )
                fire_cooldown = config.fire_interval
        else:
            fire_cooldown = 0.0

        screen_rect = screen.get_rect().inflate(40, 40)
        mob_rect = None
        if mob_hp > 0:
            half = config.tile_size / 2
            mob_rect = pygame.Rect(
                mob_pos.x - half,
                mob_pos.y - half,
                config.tile_size,
                config.tile_size,
            )

        for bullet in bullets[:]:
            bullet["pos"] += bullet["dir"] * config.bullet_speed * dt

            if not screen_rect.collidepoint(bullet["pos"]):
                bullets.remove(bullet)
                continue

            if mob_rect and mob_rect.collidepoint(bullet["pos"]):
                mob_hp = max(mob_hp - config.bullet_damage, 0)
                bullets.remove(bullet)

                impact_sound.play()

                if mob_hp == 0:
                    score += 1
                    pygame.time.set_timer(SPAWN_ENEMY_EVENT, 3000, loops=1)
                    mob_hp = -1

        screen.blit(background, (0, 0))

        is_moving = move.length_squared() > 0

        if is_moving and not was_moving:
            footsteps_sound.play(-1)
        elif not is_moving and was_moving:
            footsteps_sound.stop()

        was_moving = is_moving

        if is_moving:
            animation_timer += dt * 1000
            if animation_timer >= ANIMATION_SPEED:
                animation_timer = 0
                current_frame = (current_frame + 1) % FRAME_COUNT
        else:
            current_frame = 0

        player = frames[current_frame]
        player = pygame.transform.rotate(player, angle - 90)
        player_rect = player.get_rect(center=player_pos)
        screen.blit(player, player_rect)

        for bullet in bullets:
            phi = bullet["dir"].as_polar()[1]
            rotated_bullet = pygame.transform.rotate(bullet_image, -phi - 90)
            bullet_rect = rotated_bullet.get_rect(center=bullet["pos"])
            screen.blit(rotated_bullet, bullet_rect)

        if mob_hp > 0:
            draw_mob(
                screen,
                zombie_image,
                mob_pos,
                player_pos,
                mob_hp,
                config.mob_max_hp,
                config.tile_size,
            )

        score_text = font.render(
            f"Score: {score}", antialias=False, color=config.gui_text_color
        )
        score_rect = score_text.get_rect(left=0, top=0)
        screen.blit(score_text, score_rect)

        crosshair_rect = crosshair_image.get_rect(center=mouse_pos)
        screen.blit(crosshair_image, crosshair_rect)

        pygame.display.flip()

        dt = clock.tick(config.fps) / 1000

    pygame.quit()


if __name__ == "__main__":
    typer.run(main)
