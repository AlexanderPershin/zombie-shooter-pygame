import pygame

from player import Player


class Ui(pygame.sprite.Sprite):
    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        hp_pos: pygame.Vector2,
        font: pygame.font.Font,
        color: str,
        size: int,
    ):
        super().__init__()

        self.screen_windth = screen_width
        self.screen_height = screen_height

        self.image = pygame.Surface(
            (screen_width, screen_height), pygame.SRCALPHA
        )
        self.rect = self.image.get_rect(topleft=(0, 0))

        self.hp_pos = hp_pos

        self.score = 0

        self.font = font
        self.color = color
        self.size = size

    def update(
        self,
        dt: float,
        *args,
        player: Player,
        score: int,
        **kwargs,
    ) -> None:
        self.score = score

        self.image.fill((0, 0, 0, 0))

        self._draw(player)

    def _draw_health_bar(self, player: Player):
        bar_width = 200
        bar_height = 20

        pygame.draw.rect(
            self.image,
            "#330000",
            (self.hp_pos.x, self.hp_pos.y, bar_width, bar_height),
        )

        fill = int(bar_width * player.hp / player.max_hp)
        pygame.draw.rect(
            self.image,
            "#00cc00",
            (self.hp_pos.x, self.hp_pos.y, fill, bar_height),
        )

        hp_text = self.font.render(f"HP: {player.hp}", False, self.color)
        self.image.blit(hp_text, (self.hp_pos.x, self.hp_pos.y - 25))

    def _draw(self, player: Player):
        score_text = self.font.render(
            f"Score: {self.score}",
            antialias=False,
            color=self.color,
        )
        self.image.blit(score_text, score_text.get_rect(left=10, top=10))

        self._draw_health_bar(player)

        gun_info = self.font.render(
            str(player.gun),
            self.size,
            self.color,
        )
        self.image.blit(gun_info, (self.screen_windth - 300, self.hp_pos.y))

        self.image.blit(
            player.gun.side_image,
            (self.screen_windth - 200, self.hp_pos.y - 100),
        )
