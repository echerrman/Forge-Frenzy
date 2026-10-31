import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest
from game.app import GameApp
from game.scenes.shop_scene import (
    HOTSPOT_RECTS,
    blacksmith_frame_index,
    customer_frame_index,
)
from game.scenes.station_scene import AREA_INFO


def test_app_can_visit_every_work_area():
    app = GameApp()
    assert app.scenes.active_name == "menu"
    app.scenes.switch("shop")
    for station in AREA_INFO:
        app.scenes.switch("station", station=station)
        assert app.scenes.active_scene.station == station
        app.scenes.draw(app.screen)
    pygame.quit()


def test_display_modes_can_be_applied_and_return_to_windowed():
    app = GameApp()
    for mode in ("fullscreen", "windowed"):
        app.set_display_mode(mode)
    assert app.display_mode == "windowed"
    assert app.viewport.width > 0 and app.viewport.height > 0
    with pytest.raises(ValueError):
        app.set_display_mode("borderless")
    pygame.quit()


def test_shop_art_loads_and_station_silhouettes_are_interactive():
    app = GameApp()
    app.scenes.switch("shop")
    shop = app.scenes.active_scene

    assert shop.background.get_size() == (1280, 720)
    assert shop.station_bases.get_size() == (1280, 720)
    assert shop.counter_layer.get_size() == (1280, 720)
    assert len([frame for frame in shop.blacksmith_frames if frame]) == 4
    assert len([frame for frame in shop.customer_frames if frame]) == 3
    for frames in (shop.blacksmith_frames, shop.customer_frames):
        anchors = []
        for frame in frames:
            mask = pygame.mask.from_surface(frame, 32)
            foot_y = int(frame.get_height() * 0.70)
            points = [
                (x, y)
                for y in range(foot_y, frame.get_height())
                for x in range(frame.get_width())
                if mask.get_at((x, y))
            ]
            xs = [point[0] for point in points]
            anchors.append(((min(xs) + max(xs)) / 2, max(point[1] for point in points)))
        assert max(anchor[0] for anchor in anchors) - min(anchor[0] for anchor in anchors) <= 0.5
        assert len({anchor[1] for anchor in anchors}) == 1
    assert shop.blacksmith_shadow.get_size() == (116, 34)
    assert shop.station_masks["furnace"].get_size() == (430, 390)
    assert shop.station_masks["furnace"].get_at((30, 170))

    mask = shop.station_masks["assembly"]
    local_point = next(
        (x, y)
        for y in range(mask.get_size()[1])
        for x in range(mask.get_size()[0])
        if mask.get_at((x, y))
    )
    assembly_rect = HOTSPOT_RECTS["assembly"]
    position = (assembly_rect.x + local_point[0], assembly_rect.y + local_point[1])
    shop.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=position, rel=(0, 0), buttons=(0, 0, 0)))
    assert shop.hovered_station == "assembly"

    before = shop.animation_time
    shop.update(0.25)
    shop.draw(app.canvas)
    assert shop.animation_time == before + 0.25
    pygame.quit()


def test_shop_idle_timing_uses_faster_hammer_cycle_and_continuous_customer_loop():
    assert blacksmith_frame_index(0.0) == 0
    assert blacksmith_frame_index(2.25) == 1
    assert blacksmith_frame_index(2.40) == 2
    assert blacksmith_frame_index(2.50) == 3
    assert blacksmith_frame_index(3.0) == 0
    assert customer_frame_index(0.0) == 0
    assert customer_frame_index(0.5) == 1
    assert customer_frame_index(1.0) == 2
    assert customer_frame_index(1.5) == 0
