import pygame

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
BG_COLOR = "#006699"

SPEED = 5


def main():
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.display.set_caption("Keyboard events")

    player_x, player_y = screen.get_rect().center

    keys_pressed = set()

    clock = pygame.Clock()

    running = True

    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    keys_pressed.add(event.key)
                case pygame.KEYUP:
                    keys_pressed.discard(event.key)

        screen.fill(BG_COLOR)

        dx, dy = 0, 0
        if pygame.K_a in keys_pressed:
            dx -= 1
        if pygame.K_d in keys_pressed:
            dx += 1
        if pygame.K_w in keys_pressed:
            dy -= 1
        if pygame.K_s in keys_pressed:
            dy += 1

        player_x += dx * SPEED
        player_y += dy * SPEED

        pygame.draw.circle(
            screen, "#009900", (int(player_x), int(player_y)), 50
        )

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
