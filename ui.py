import pygame

from player import Player


class ScoreText(pygame.sprite.Sprite):
    def __init__(
        self,
        font: pygame.Font,
        color: str,
        topleft: tuple = (10, 10),
    ):
        super().__init__()

        self.font = font
        self.color = color
        self.topleft = topleft
        self.score = 0

        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=self.topleft)

    def _render(self) -> None:
        self.image = self.font.render(
            f"Score: {self.score}",
            antialias=False,
            color=self.color,
        )
        self.rect = self.image.get_rect(topleft=self.topleft)

    def update(self, dt: float, *args, score=0, **kwargs):
        self.score = score
        self._render()


class HealthBar(pygame.sprite.Sprite):
    HEALTH_BAR_WIDTH = 200
    HEALTH_BAR_HEIGHT = 20
    HEALTH_TEXT_OFFSET = 25

    def __init__(
        self,
        font: str,
        color: str,
        pos: pygame.Vector2,
    ):
        super().__init__()

        self.font = font
        self.color = color

        self.image = pygame.Surface(
            (
                self.HEALTH_BAR_WIDTH,
                self.HEALTH_TEXT_OFFSET + self.HEALTH_BAR_HEIGHT,
            ),
            pygame.SRCALPHA,
        )
        self.rect = self.image.get_rect(
            topleft=(pos[0], pos[1] - self.HEALTH_TEXT_OFFSET)
        )

        self._hp = None
        self._max_hp = None

    def _render(self) -> None:
        self.image.fill("#ffffff00")

        pygame.draw.rect(
            self.image,
            "#330000",
            (
                0,
                self.HEALTH_TEXT_OFFSET,
                self.HEALTH_BAR_WIDTH,
                self.HEALTH_BAR_HEIGHT,
            ),
        )

        ratio = self._hp / self._max_hp if self._max_hp else 0
        filled_part = int(self.HEALTH_BAR_WIDTH * ratio)
        pygame.draw.rect(
            self.image,
            "#00cc00",
            (0, self.HEALTH_TEXT_OFFSET, filled_part, self.HEALTH_BAR_HEIGHT),
        )

        hp_text = self.font.render(f"HP: {self._hp}", False, self.color)

        self.image.blit(hp_text, (0, 0))

    def update(
        self,
        dt: float,
        *args,
        player: Player,
        **kwargs,
    ):
        if player.hp == self._hp and player.max_hp == self._max_hp:
            return
        self._hp = player.hp
        self._max_hp = player.max_hp
        self._render()


class GunInfo(pygame.sprite.Sprite):
    def __init__(
        self,
        font: pygame.Font,
        color: str,
        size: int,
        text_pos: tuple,
        icon_pos: tuple,
    ):
        super().__init__()

        self.font = font
        self.color = color
        self.size = size

        self.text_pos = pygame.Vector2(text_pos)
        self.icon_pos = pygame.Vector2(icon_pos)

        self.gun = None

        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))

    def _render(self):
        text_surf = self.font.render(str(self.gun), self.size, self.color)
        icon = self.gun.side_image

        min_x = min(self.text_pos.x, self.icon_pos.x)
        min_y = min(self.text_pos.y, self.icon_pos.y)

        max_x = max(
            self.text_pos.x + text_surf.get_width(),
            self.icon_pos.x + icon.get_width(),
        )
        max_y = max(
            self.text_pos.y + text_surf.get_height(),
            self.icon_pos.y + icon.get_height(),
        )

        width, height = int(max_x - min_x), int(max_y - min_y)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

        self.image.blit(
            text_surf,
            (self.text_pos.x - min_x, self.text_pos.y - min_y),
        )

        self.image.blit(
            icon,
            (self.icon_pos.x - min_x, self.icon_pos.y - min_y),
        )

        self.rect = self.image.get_rect(topleft=(min_x, min_y))

    def update(
        self,
        dt: float,
        *args,
        player: Player,
        **kwargs,
    ):
        self.gun = player.gun
        self._render()


class Minimap(pygame.sprite.Sprite):
    MINIMAP_SIZE = 200
    MINIMAP_MARGIN = 10

    def __init__(
        self,
        screen_width: int,
        world_width: int,
        world_height: int,
    ):
        super().__init__()

        self.world_width = world_width
        self.world_height = world_height

        self.scale = self.MINIMAP_SIZE / world_width

        self.minimap_width = self.world_width * self.scale
        self.minimap_height = self.world_height * self.scale

        self.image = pygame.Surface(
            (self.minimap_width, self.minimap_height), pygame.SRCALPHA
        )

        self.rect = self.image.get_rect(
            topleft=(
                screen_width - self.minimap_width - self.MINIMAP_MARGIN,
                self.MINIMAP_MARGIN,
            )
        )

    def _to_map(self, pos: pygame.Vector2) -> tuple[int, int]:
        return int(pos.x * self.scale), int(pos.y * self.scale)

    def update(
        self,
        dt: float,
        *args,
        player: Player,
        enemies: pygame.sprite.Group,
        items: pygame.sprite.Group,
        **kwargs,
    ) -> None:
        self.image.fill("#00000000")

        pygame.draw.rect(
            self.image,
            "#006699aa",
            (0, 0, self.minimap_width, self.minimap_height),
            0,
            10,
        )
        pygame.draw.rect(
            self.image,
            "#006699cc",
            (0, 0, self.minimap_width, self.minimap_height),
            5,
            10,
        )

        for item in items:
            pygame.draw.circle(self.image, "white", self._to_map(item.pos), 3)

        for mob in enemies:
            pygame.draw.circle(self.image, "#fa5252", self._to_map(mob.pos), 3)

        pygame.draw.circle(self.image, "#25F525", self._to_map(player.pos), 4)


class Ui(pygame.sprite.Sprite):
    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        hp_pos: pygame.Vector2,
        font: pygame.font.Font,
        color: str,
        size: int,
        world_width: int,
        world_height: int,
    ):
        super().__init__()

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.image = pygame.Surface(
            (screen_width, screen_height), pygame.SRCALPHA
        )
        self.rect = self.image.get_rect(topleft=(0, 0))

        self.sprites = pygame.sprite.Group(
            ScoreText(font, color, topleft=(10, 10)),
            HealthBar(font, color, hp_pos),
            GunInfo(
                font,
                color,
                size,
                text_pos=(screen_width - 300, hp_pos.y),
                icon_pos=(screen_width - 200, hp_pos.y - 100),
            ),
            Minimap(screen_width, world_width, world_height),
        )

    def update(
        self,
        dt: float,
        *args,
        player: Player,
        enemies: pygame.sprite.Group,
        items: pygame.sprite.Group,
        score: int = 0,
        **kwargs,
    ) -> None:
        self.sprites.update(
            dt,
            player=player,
            enemies=enemies,
            items=items,
            score=score,
        )

        self.image.fill("#00000000")

        self.sprites.draw(self.image)
