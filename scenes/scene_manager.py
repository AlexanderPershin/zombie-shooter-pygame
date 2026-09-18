import pygame

from scenes.scene import AbstractScene


class SceneManager:
    def __init__(self, sound: pygame.mixer.Sound):
        self.current: AbstractScene = None
        self.scenes: dict[str, AbstractScene] = {}
        self.sound = sound

    def register(self, name: str, scene_obj: AbstractScene) -> None:
        self.scenes[name] = scene_obj

    def switch(self, name: str, *args, **kwargs) -> None:
        if name not in self.scenes:
            raise ValueError(f"Scene '{name}' not found")

        self.sound.play()

        self.current = self.scenes[name]

        self.current.on_enter(*args, **kwargs)

    def handle_event(self, event: pygame.Event) -> None:
        if self.current:
            self.current.handle_event(event)

    def update(self, *args, **kwargs) -> None:
        if self.current:
            self.current.update(*args, **kwargs)

    def draw(self, surf: pygame.Surface) -> None:
        if self.current:
            self.current.draw(surf)
