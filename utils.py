import random

import pygame


def get_movement_direction(keys: pygame.key.ScancodeWrapper) -> pygame.Vector2:
    move = pygame.Vector2()

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        move.y -= 1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        move.y += 1
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        move.x -= 1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        move.x += 1

    if move.length_squared() > 0:
        move.normalize_ip()

    return move


def aim_direction(
    from_pos: pygame.Vector2, to_pos: pygame.Vector2
) -> pygame.Vector2:
    to_target = to_pos - from_pos
    if to_target.length_squared():
        return to_target.normalize()
    return pygame.Vector2(1, 0)


def direction_to_angle(direction: pygame.Vector2) -> float:
    return -direction.as_polar()[1]


def load_sprite_frames(
    sprite_sheet: pygame.Surface, frame_count: int, tile_size: int
) -> list[pygame.Surface]:
    frame_width = sprite_sheet.get_width() // frame_count
    frame_height = sprite_sheet.get_height()
    frames = []

    for i in range(frame_count):
        frame_surface = pygame.Surface(
            (frame_width, frame_height), pygame.SRCALPHA
        )
        frame_surface.blit(
            sprite_sheet,
            (0, 0),
            (i * frame_width, 0, frame_width, frame_height),
        )
        frames.append(
            pygame.transform.scale(
                frame_surface, (tile_size * 2, tile_size * 2)
            )
        )

    return frames


def tile_background(
    land_images: list[pygame.Surface], width: int, height: int
) -> pygame.Surface:
    bg_surface = pygame.Surface((width, height))
    tile_w = land_images[0].get_width()
    tile_h = land_images[0].get_height()

    for y in range(0, height, tile_h):
        for x in range(0, width, tile_w):
            cur_image = random.choice(land_images)
            bg_surface.blit(cur_image, (x, y))

    return bg_surface


def generate_mobs_positions(
    step: int,
    width: int,
    height: int,
    margin: int,
) -> list[pygame.Vector2]:
    mobs_positions: list[pygame.Vector2] = []

    for x in range(0, width, step):
        top_pos = pygame.Vector2(x, 0 - margin)
        bottom_pos = pygame.Vector2(x, height + margin)
        mobs_positions.append(top_pos)
        mobs_positions.append(bottom_pos)

    for y in range(0, height, step):
        left_pos = pygame.Vector2(0 - margin, y)
        right_pos = pygame.Vector2(width + margin, y)
        mobs_positions.append(left_pos)
        mobs_positions.append(right_pos)

    return mobs_positions
