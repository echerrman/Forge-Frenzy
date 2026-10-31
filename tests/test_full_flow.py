import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.app import GameApp
from game.items import WeaponStage
from game.scenes.station_scene import ANVIL_TARGETS


def click(scene, position):
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=position))
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=position))


def test_initial_order_can_be_completed_through_mouse_workflow():
    app = GameApp()
    app.start_or_resume_workday()

    app.scenes.switch("station", station="customer_counter")
    click(app.scenes.active_scene, (400, 330))
    assert app.game_state.active_order.weapon_type == "dagger"

    app.scenes.switch("station", station="storage")
    click(app.scenes.active_scene, (220, 330))
    item = app.game_state.active_workpiece
    assert item.selected_material == "iron"

    app.scenes.switch("station", station="furnace")
    click(app.scenes.active_scene, (620, 655))
    app.scenes.update(3.1)
    click(app.scenes.active_scene, (450, 300))

    app.scenes.switch("station", station="mold")
    click(app.scenes.active_scene, (220, 210))
    click(app.scenes.active_scene, (620, 655))
    scene = app.scenes.active_scene
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(720, 370)))
    scene.update(3.0)
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(720, 370)))

    app.scenes.switch("station", station="anvil")
    click(app.scenes.active_scene, (620, 655))
    for target in ANVIL_TARGETS:
        click(app.scenes.active_scene, target)

    app.scenes.switch("station", station="quench")
    click(app.scenes.active_scene, (620, 655))
    scene = app.scenes.active_scene
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(460, 240)))
    scene.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(800, 600), rel=(340, 360), buttons=(1, 0, 0)))
    assert scene.drag_position == (450, 405)
    scene.update(3.0)
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(800, 600)))
    assert scene.drag_position == (450, 242)

    app.scenes.switch("station", station="grindstone")
    click(app.scenes.active_scene, (620, 655))
    scene = app.scenes.active_scene
    for _ in range(7):
        click(scene, (170, 335))
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(470, 255)))
    for x in (650, 355, 650, 355):
        scene.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(x, 255), rel=(0, 0), buttons=(1, 0, 0)))
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(355, 255)))

    app.scenes.switch("station", station="assembly")
    click(app.scenes.active_scene, (620, 655))
    scene = app.scenes.active_scene
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 200)))
    scene.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(630, 365), rel=(480, 165), buttons=(1, 0, 0)))
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(630, 365)))
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 390)))
    scene.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(460, 350), rel=(310, -40), buttons=(1, 0, 0)))
    scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(460, 350)))
    assert item.stage == WeaponStage.ASSEMBLED

    app.scenes.switch("station", station="customer_counter")
    click(app.scenes.active_scene, (400, 330))
    assert app.scenes.active_name == "results"
    assert app.game_state.player.gold > 0

    click(app.scenes.active_scene, (620, 645))
    assert app.scenes.active_name == "day_summary"
    click(app.scenes.active_scene, (620, 640))
    assert app.game_state.current_day == 2
    assert app.scenes.active_name == "shop"
    pygame.quit()
