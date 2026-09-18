import pygame

FRAME_COUNT = 8


class Animation:
    def __init__(
        self,
        frames: list[pygame.Surface],
        frame_duration_ms: int,
        loop: bool = True,
    ):
        self.frames = frames
        self.frame_duration = frame_duration_ms / 1000.0
        self.loop = loop
        self.current_frame = 0
        self.timer = 0.0
        self.finished = False

    def update(self, dt: float) -> pygame.Surface:
        if self.finished:
            return self.frames[-1] if self.frames else None

        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer = 0.0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
        return self.frames[self.current_frame]

    def reset(self):
        self.current_frame = 0
        self.timer = 0.0
        self.finished = False
