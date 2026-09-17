import pygame

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
BG_COLOR = "#006699"

SPEED = 300


def main():
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.display.set_caption("Keyboard events")

    player_pos = pygame.Vector2(screen.get_rect().center)

    clock = pygame.Clock()

    dt = 0

    running = True

    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False

        screen.fill(BG_COLOR)

        pygame.draw.circle(screen, "#009900", player_pos, 50)

        keys = pygame.key.get_pressed()

        direction = pygame.Vector2(0, 0)

        if keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_s]:
            direction.y += 1
        if keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_d]:
            direction.x += 1

        if direction.length_squared() > 0:
            direction.normalize_ip()

        player_pos += direction * SPEED * dt

        pygame.display.flip()

        dt = clock.tick(FPS) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()
