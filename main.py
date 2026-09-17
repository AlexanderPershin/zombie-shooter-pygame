import pygame

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
BG_COLOR = "#006699"
SPEED = 300

GUN_WIDTH = 50
GUN_HEIGHT = 16


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

    dt = 0

    running = True

    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.MOUSEMOTION:
                    mouse_pos = pygame.Vector2(event.pos)

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

        screen.fill(BG_COLOR)

        pygame.draw.circle(screen, "#009900", player_pos, 50)

        screen.blit(rotated_gun, gun_rect)

        if to_mouse.length_squared() > 2500:
            pygame.draw.line(
                screen,
                (255, 0, 0),
                muzzle_pos,
                mouse_pos,
                3,
            )

        pygame.display.flip()

        dt = clock.tick(FPS) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()
