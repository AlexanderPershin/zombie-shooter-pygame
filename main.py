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

    dt = 0

    running = True

    is_left_mouse = False

    is_lazer = False
    lazer_colors = ["red", "green", "blue"]
    lazer_index = 0

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

        # if pygame.mouse.get_pressed()[0]:
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

        for bullet in bullets[:]:
            bullet["pos"] += bullet["dir"] * BULLET_SPEED * dt

            if not screen_rect.collidepoint(bullet["pos"]):
                bullets.remove(bullet)
                continue

        screen.fill(BG_COLOR)

        pygame.draw.circle(screen, "#009900", player_pos, 50)

        screen.blit(rotated_gun, gun_rect)

        for bullet in bullets:
            pygame.draw.circle(screen, "#fa5252", bullet["pos"], BULLET_RADIUS)

        if is_lazer and to_mouse.length_squared() > 2500:
            pygame.draw.line(
                screen,
                lazer_color,
                muzzle_pos,
                mouse_pos,
                3,
            )

        pygame.display.flip()

        dt = clock.tick(FPS) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()
