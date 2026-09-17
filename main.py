import pygame

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
BG_COLOR = "#006699"
SPEED = 300

GUN_WIDTH = 50
GUN_HEIGHT = 16

BULLET_SPEED = 700
BULLET_RADIUS = 5
FIRE_INTERVAL = 0.12

MOB_SIZE = 60
MOB_MAX_HP = 100
BULLET_DAMAGE = 25

SPAWN_ENEMY_EVENT = pygame.event.custom_type()


def create_gun():
    gun = pygame.Surface((GUN_WIDTH, GUN_HEIGHT), pygame.SRCALPHA)

    pygame.draw.rect(
        gun,
        "#cfd4d9",
        (0, 2, GUN_WIDTH, GUN_HEIGHT - 4),
        border_radius=3,
    )

    pygame.draw.rect(
        gun,
        "#43464b",
        (GUN_WIDTH - 8, 0, 6, 3),
    )

    return gun


def draw_mob(screen, pos, hp, max_hp):
    half = MOB_SIZE / 2
    mob_rect = pygame.Rect(pos.x - half, pos.y - half, MOB_SIZE, MOB_SIZE)
    pygame.draw.rect(screen, "#cc4444", mob_rect)

    bar_width = MOB_SIZE
    bar_height = 6
    bar_x = pos.x - half
    bar_y = pos.y - half - 10

    pygame.draw.rect(screen, "#330000", (bar_x, bar_y, bar_width, bar_height))
    if hp > 0:
        fill_width = int(bar_width * hp / max_hp)
        pygame.draw.rect(
            screen, "#00cc00", (bar_x, bar_y, fill_width, bar_height)
        )


def main():
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.display.set_caption("Mouse events")

    clock = pygame.time.Clock()

    player_pos = pygame.Vector2(screen.get_rect().center)

    mouse_pos = pygame.Vector2()

    gun_source = create_gun()

    bullets = []
    fire_cooldown = 0.0

    mob_pos = pygame.Vector2(WINDOW_WIDTH * 0.75, WINDOW_HEIGHT // 2)
    mob_hp = MOB_MAX_HP

    dt = 0

    running = True

    is_left_mouse = False

    is_lazer = False
    lazer_colors = ["red", "green", "blue"]
    lazer_index = 0

    score = 0

    font = pygame.font.SysFont(None, 48)

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
                    if event.button == 2:
                        is_lazer = not is_lazer
                    if event.button == 4:
                        lazer_index -= 1
                        if lazer_index == -1:
                            lazer_index = len(lazer_colors) - 1
                    if event.button == 5:
                        lazer_index += 1
                        if lazer_index == len(lazer_colors):
                            lazer_index = 0
                case pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        is_left_mouse = False
                case SPAWN_ENEMY_EVENT:
                    if mob_hp == -1:
                        mob_hp = MOB_MAX_HP

        lazer_color = lazer_colors[lazer_index]

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

        rotated_gun = pygame.transform.rotate(gun_source, angle)
        gun_center = player_pos + direction * (GUN_WIDTH / 2)
        gun_rect = rotated_gun.get_rect(center=gun_center)
        muzzle_pos = player_pos + direction * GUN_WIDTH

        if is_left_mouse:
            fire_cooldown -= dt
            if fire_cooldown <= 0:
                bullets.append(
                    {
                        "pos": pygame.Vector2(muzzle_pos),
                        "dir": pygame.Vector2(direction),
                    }
                )
                fire_cooldown = FIRE_INTERVAL
        else:
            fire_cooldown = 0.0

        screen_rect = screen.get_rect().inflate(40, 40)
        mob_rect = None
        if mob_hp > 0:
            half = MOB_SIZE / 2
            mob_rect = pygame.Rect(
                mob_pos.x - half, mob_pos.y - half, MOB_SIZE, MOB_SIZE
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

        screen.fill(BG_COLOR)

        pygame.draw.circle(screen, "#009900", player_pos, 50)

        screen.blit(rotated_gun, gun_rect)

        for bullet in bullets:
            pygame.draw.circle(screen, "#fa5252", bullet["pos"], BULLET_RADIUS)

        if mob_hp > 0:
            draw_mob(screen, mob_pos, mob_hp, MOB_MAX_HP)

        if is_lazer and to_mouse.length_squared() > 2500:
            pygame.draw.line(
                screen,
                lazer_color,
                muzzle_pos,
                mouse_pos,
                3,
            )

        score_text = font.render(
            f"Score: {score}", antialias=False, color="white"
        )
        score_rect = score_text.get_rect(left=0, top=0)
        screen.blit(score_text, score_rect)

        pygame.display.flip()

        dt = clock.tick(FPS) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()
