from abc import ABC, abstractmethod

import pygame


class AbstractScene(ABC):
    @abstractmethod
    def handle_event(self, event: pygame.Event) -> None:
        pass

    def update(self, dt: float, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        pass

    def on_enter(self, *args, **kwargs) -> None:
        pass
