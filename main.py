import pygame

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
BG_COLOR = "#006699"
SPEED = 300

TILE_SIZE = 64

BULLET_SPEED = 700
BULLET_RADIUS = 5
FIRE_INTERVAL = 0.12

MOB_MAX_HP = 100
BULLET_DAMAGE = 25

SPAWN_ENEMY_EVENT = pygame.event.custom_type()


def draw_mob(screen, image, pos, player_pos, hp, max_hp):
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

    half = TILE_SIZE / 2
    bar_width = TILE_SIZE
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


def main():
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.display.set_caption("Images")

    clock = pygame.time.Clock()

    player_pos = pygame.Vector2(screen.get_rect().center)

    mouse_pos = pygame.Vector2()

    bullets = []
    fire_cooldown = 0.0

    mob_pos = pygame.Vector2(WINDOW_WIDTH * 0.75, WINDOW_HEIGHT // 2)
    mob_hp = MOB_MAX_HP

    dt = 0

    running = True

    is_left_mouse = False

    score = 0

    font = pygame.font.Font("fonts/BlackOpsOne-Regular.ttf", 24)

    player_image = pygame.image.load("images/character.svg").convert_alpha()
    player_image = pygame.transform.scale(player_image, (TILE_SIZE, TILE_SIZE))

    zombie_image = pygame.image.load("images/zombie.svg").convert_alpha()
    zombie_image = pygame.transform.scale(zombie_image, (TILE_SIZE, TILE_SIZE))

    bullet_image = pygame.image.load("images/bullet.svg").convert_alpha()

    land_image = pygame.image.load("images/land.svg").convert_alpha()
    background = tile_background(land_image, WINDOW_WIDTH, WINDOW_HEIGHT)

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
                        mob_hp = MOB_MAX_HP

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

        if move.length_squared():
            move.normalize_ip()

        player_pos += move * SPEED * dt

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
                bullets.append(
                    {
                        "pos": pygame.Vector2(bullet_pos),
                        "dir": pygame.Vector2(direction),
                    }
                )
                fire_cooldown = FIRE_INTERVAL
        else:
            fire_cooldown = 0.0

        screen_rect = screen.get_rect().inflate(40, 40)
        mob_rect = None
        if mob_hp > 0:
            half = TILE_SIZE / 2
            mob_rect = pygame.Rect(
                mob_pos.x - half, mob_pos.y - half, TILE_SIZE, TILE_SIZE
            )

        for bullet in bullets[:]:
            bullet["pos"] += bullet["dir"] * BULLET_SPEED * dt

            if not screen_rect.collidepoint(bullet["pos"]):
                bullets.remove(bullet)
                continue

            if mob_rect and mob_rect.collidepoint(bullet["pos"]):
                mob_hp = max(mob_hp - BULLET_DAMAGE, 0)
                bullets.remove(bullet)
                if mob_hp == 0:
                    score += 1
                    pygame.time.set_timer(
                        pygame.Event(
                            SPAWN_ENEMY_EVENT,
                            {"message": "You cannot kill me!"},
                        ),
                        3000,
                        loops=1,
                    )
                    mob_hp = -1

        screen.blit(background, (0, 0))

        player = pygame.transform.rotate(player_image, angle - 90)
        player_rect = player_image.get_rect(center=player_pos)

        screen.blit(player, player_rect)

        for bullet in bullets:
            phi = bullet["dir"].as_polar()[1]
            rotated_bullet = pygame.transform.rotate(bullet_image, -phi - 90)
            bullet_rect = rotated_bullet.get_rect(center=bullet["pos"])
            screen.blit(rotated_bullet, bullet_rect)

        if mob_hp > 0:
            draw_mob(
                screen, zombie_image, mob_pos, player_pos, mob_hp, MOB_MAX_HP
            )

        score_text = font.render(
            f"Score: {score}", antialias=False, color="#006699"
        )
        score_rect = score_text.get_rect(left=0, top=0)
        screen.blit(score_text, score_rect)

        pygame.display.flip()

        dt = clock.tick(FPS) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()
