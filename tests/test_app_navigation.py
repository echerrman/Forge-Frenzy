import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
from game.app import GameApp
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
    for mode in ("borderless", "fullscreen", "windowed"):
        app.set_display_mode(mode)
    assert app.display_mode == "windowed"
    assert app.viewport.width > 0 and app.viewport.height > 0
    pygame.quit()
