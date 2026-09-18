import typer

from config import Config
from game import Game

CONFIG = Config.load_from_ini()


def main(
    world_width: int | None = typer.Option(None, "--world-width"),
    world_height: int | None = typer.Option(None, "--world-height"),
    window_width: int | None = typer.Option(None, "--window-width"),
    window_height: int | None = typer.Option(None, "--window-height"),
    fullscreen: bool = typer.Option(False, "--fullscreen"),
    fps: int | None = typer.Option(None, "--fps"),
    speed: int | None = typer.Option(None, "--speed"),
    tile_size: int | None = typer.Option(None, "--tile-size"),
    bullet_speed: int | None = typer.Option(None, "--bullet-speed"),
    bullet_damage: int | None = typer.Option(None, "--bullet-damage"),
    fire_interval: int | None = typer.Option(None, "--fire-interval"),
    mob_max_hp: int | None = typer.Option(None, "--mob-max-hp"),
    mob_speed: int | None = typer.Option(None, "--mob-speed"),
    gui_font_size: int | None = typer.Option(None, "--gui-font-size"),
    gui_text_color: str | None = typer.Option(None, "--gui-text-color"),
):
    config = CONFIG.parse_cli(
        world_width=world_width,
        world_height=world_height,
        window_width=window_width,
        window_height=window_height,
        fullscreen=fullscreen,
        fps=fps,
        speed=speed,
        tile_size=tile_size,
        bullet_speed=bullet_speed,
        bullet_damage=bullet_damage,
        fire_interval=fire_interval,
        mob_max_hp=mob_max_hp,
        mob_speed=mob_speed,
        gui_font_size=gui_font_size,
        gui_text_color=gui_text_color,
    )

    run_game(config)


def run_game(config: Config):
    with Game(config) as game:
        game.run()


if __name__ == "__main__":
    typer.run(main)
