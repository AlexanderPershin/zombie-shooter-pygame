import pygame

from config import Config
from scenes.scene import AbstractScene
from scenes.scene_manager import SceneManager


class GameOverScene(AbstractScene):
    def __init__(
        self,
        manager: SceneManager,
        config: Config,
        font: pygame.Font,
    ):
        self.manager = manager
        self.config = config
        self.font = font

        self.final_score = 0
        self.reached_level = 1

    def handle_event(self, event: pygame.Event) -> None:
        match event.type:
            case pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.manager.switch("game", do_reset=True)
                elif event.key == pygame.K_ESCAPE:
                    self.manager.switch("menu")

    def on_enter(
        self, *args, final_score: int = 0, reached_level: int = 0, **kwargs
    ) -> None:
        pygame.mixer.music.stop()
        pygame.mixer.music.load("sounds/defeat.wav")
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play()
        pygame.mouse.set_visible(True)

        self.final_score = final_score
        self.reached_level = reached_level

    def draw(self, surf: pygame.Surface) -> None:
        surf.fill("lightsalmon")

        title = self.font.render("GAME OVER", True, "#fa5252")
        score = self.font.render(
            f"Final Score: {self.final_score}", True, "white"
        )
        level = self.font.render(
            f"Reached Level: {self.reached_level}", True, "white"
        )
        hint = self.font.render("ENTER — Retry    ESC — Menu", True, "#aaaaaa")

        surf.blit(
            title,
            title.get_rect(
                center=(
                    self.config.window_width // 2,
                    self.config.window_height // 2 - 80,
                )
            ),
        )
        surf.blit(
            score,
            score.get_rect(
                center=(
                    self.config.window_width // 2,
                    self.config.window_height // 2 - 10,
                )
            ),
        )
        surf.blit(
            level,
            score.get_rect(
                center=(
                    self.config.window_width // 2,
                    self.config.window_height // 2 + 30,
                )
            ),
        )
        surf.blit(
            hint,
            hint.get_rect(
                center=(
                    self.config.window_width // 2,
                    self.config.window_height // 2 + 80,
                )
            ),
        )
