import configparser
from pathlib import Path

import caep
from pydantic import BaseModel, Field


class Config(BaseModel):
    world_width: int = Field(default=3000, gt=0)
    world_height: int = Field(default=3000, gt=0)

    window_width: int = Field(default=800, gt=0, le=3840)
    window_height: int = Field(default=600, gt=0, le=2160)
    fullscreen: bool = True

    fps: int = Field(default=60, ge=30, le=240)

    speed: int = Field(default=300, gt=0)

    tile_size: int = Field(default=64, gt=0, le=256)

    bullet_speed: int = Field(default=700, gt=0)
    bullet_damage: int = Field(default=25, gt=0)
    fire_interval: float = Field(default=0.12, gt=0)

    mob_max_hp: int = Field(default=100, gt=0)
    mob_speed: int = Field(default=150, gt=0)

    gui_font_size: int = Field(default=24, gt=0, le=200)
    gui_text_color: str = Field(default="#006699")

    @classmethod
    def load_from_ini(cls, path: Path = Path("settings.ini")) -> Config:
        if not path.exists():
            return cls()
        return caep.load(cls, path, section_name="Game")

    def save_to_ini(self, path: Path = Path("settings.ini")) -> None:
        cp = configparser.ConfigParser()
        cp["Game"] = {k: str(v) for k, v in self.model_dump().items()}
        with open(path, "w", encoding="utf-8") as f:
            cp.write(f)

    def parse_cli(self, **overrides) -> Config:
        updates = {k: v for k, v in overrides.items() if v is not None}
        current_data = self.model_dump()
        current_data.update(updates)
        return Config(**current_data)


CONFIG = Config()
