import pygame

from config import Config
from scenes.scene import AbstractScene
from scenes.scene_manager import SceneManager


class MainMenuScene(AbstractScene):
    def __init__(
        self,
        manager: SceneManager,
        config: Config,
        font: pygame.Font,
        image: pygame.Surface,
    ):
        self.manager = manager
        self.config = config
        self.font = font
        self.image = pygame.transform.scale(
            image,
            (self.config.window_width, self.config.window_width / 1.7),
        )

        self.game_in_progress = False

        self.title = self.font.render("Zombie shooter", True, "#009900")
        self.title_rect = self.title.get_rect(
            center=(
                self.config.window_width // 2,
                self.config.window_height // 2 - 40,
            )
        )
        self.continue_btn = self.font.render(
            "Continue [Esc]", True, "#ffffff", "#006699"
        )
        self.continue_rect = self.continue_btn.get_rect(
            center=(
                self.config.window_width // 2,
                self.config.window_height // 2,
            )
        )

        self.enter = self.font.render(
            "Start [Enter]", True, "#ffffff", "#006699"
        )
        self.enter_rect = self.enter.get_rect(
            center=(
                self.config.window_width // 2,
                self.config.window_height // 2 + 40,
            )
        )

        self.quit = self.font.render("Quit [Q]", True, "#ffffff", "#fa5252")
        self.quit_rect = self.quit.get_rect(
            center=(
                self.config.window_width // 2,
                self.config.window_height // 2 + 80,
            )
        )

    def handle_event(self, event: pygame.Event) -> None:
        match event.type:
            case pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.manager.switch("game", do_reset=True)
                elif event.key == pygame.K_ESCAPE and self.game_in_progress:
                    self.manager.switch("game", do_reset=False)
                elif event.key == pygame.K_q:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            case pygame.MOUSEBUTTONDOWN:
                if (
                    event.button == 1
                    and self.continue_rect.collidepoint(event.pos)
                    and self.game_in_progress
                ):
                    self.manager.switch("game", do_reset=False)
                elif event.button == 1 and self.enter_rect.collidepoint(
                    event.pos
                ):
                    self.manager.switch("game", do_reset=True)
                elif event.button == 1 and self.quit_rect.collidepoint(
                    event.pos
                ):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

    def on_enter(
        self, *args, game_in_progress: bool = False, **kwargs
    ) -> None:
        self.game_in_progress = game_in_progress

        pygame.mixer.music.stop()
        pygame.mixer.music.load("sounds/menu_theme.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        pygame.mouse.set_visible(True)

    def draw(self, surf: pygame.Surface) -> None:
        surf.fill("lightskyblue")

        surf.blit(
            self.image, self.image.get_rect(center=surf.get_rect().center)
        )

        surf.blit(self.title, self.title_rect)

        if self.game_in_progress:
            surf.blit(self.continue_btn, self.continue_rect)

        surf.blit(self.enter, self.enter_rect)

        surf.blit(self.quit, self.quit_rect)
