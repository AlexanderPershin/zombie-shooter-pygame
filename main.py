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

    clock = pygame.Clock()

    running = True

    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        player_x -= SPEED
                    elif event.key == pygame.K_d:
                        player_x += SPEED
                    elif event.key == pygame.K_w:
                        player_y -= SPEED
                    elif event.key == pygame.K_s:
                        player_y += SPEED

        screen.fill(BG_COLOR)

        pygame.draw.circle(
            screen, "#009900", (int(player_x), int(player_y)), 50
        )

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
