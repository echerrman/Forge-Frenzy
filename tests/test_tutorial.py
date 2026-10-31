import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.app import GameApp
from game.scenes.station_scene import ANVIL_TARGETS


def advance(app, delta_time=0.0):
    app.scenes.update(delta_time)
    app.tutorial.update(app.scenes.active_name, app.game_state)


def dispatch(app, event):
    if app.tutorial.allow_event(event):
        app.scenes.handle_event(event)
    advance(app)


def click(app, position):
    dispatch(app, pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=position))
    dispatch(app, pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=position))


def back(app):
    click(app, (120, 665))


def visit(app, position):
    click(app, position)
    assert app.scenes.active_name == "station"


def test_tutorial_guides_complete_day_one_and_returns_to_clean_menu():
    app = GameApp()
    app.start_tutorial()
    assert app.tutorial.step == "shop_counter"
    assert not app.tutorial.allow_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 300)))

    visit(app, (600, 150))
    assert app.tutorial.step == "accept_order"
    click(app, (400, 330))
    assert app.tutorial.step == "order_details"
    click(app, (1050, 250))
    assert app.tutorial.step == "counter_back"
    back(app)

    visit(app, (180, 280))
    assert app.tutorial.step == "choose_material"
    click(app, (220, 330))
    assert app.tutorial.step == "storage_back"
    back(app)

    visit(app, (1050, 260))
    click(app, (620, 655))
    advance(app, 3.1)
    click(app, (450, 300))
    assert app.tutorial.step == "furnace_back"
    back(app)

    visit(app, (400, 280))
    click(app, (220, 210))
    click(app, (620, 655))
    dispatch(app, pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(720, 370)))
    advance(app, 3.0)
    dispatch(app, pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(720, 370)))
    assert app.tutorial.step == "mold_back"
    back(app)

    visit(app, (780, 330))
    click(app, (620, 655))
    for target in ANVIL_TARGETS:
        click(app, target)
    assert app.tutorial.step == "anvil_back"
    back(app)

    visit(app, (1050, 480))
    click(app, (620, 655))
    dispatch(app, pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(450, 242)))
    dispatch(app, pygame.event.Event(pygame.MOUSEMOTION, pos=(450, 405), rel=(0, 163), buttons=(1, 0, 0)))
    advance(app, 3.0)
    dispatch(app, pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(450, 405)))
    assert app.tutorial.step == "quench_back"
    back(app)

    visit(app, (180, 500))
    click(app, (620, 655))
    for _ in range(7):
        click(app, (170, 335))
    dispatch(app, pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(470, 255)))
    for x in (650, 355, 650, 355):
        dispatch(app, pygame.event.Event(pygame.MOUSEMOTION, pos=(x, 255), rel=(0, 0), buttons=(1, 0, 0)))
    dispatch(app, pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(355, 255)))
    assert app.tutorial.step == "grindstone_back"
    back(app)

    visit(app, (600, 520))
    click(app, (620, 655))
    dispatch(app, pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 200)))
    dispatch(app, pygame.event.Event(pygame.MOUSEMOTION, pos=(630, 365), rel=(480, 165), buttons=(1, 0, 0)))
    dispatch(app, pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(630, 365)))
    dispatch(app, pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 400)))
    dispatch(app, pygame.event.Event(pygame.MOUSEMOTION, pos=(460, 350), rel=(310, -50), buttons=(1, 0, 0)))
    dispatch(app, pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(460, 350)))
    assert app.tutorial.step == "assembly_back"
    back(app)

    visit(app, (600, 150))
    click(app, (400, 330))
    assert app.scenes.active_name == "results"
    assert app.tutorial.step == "results"
    click(app, (620, 645))
    assert app.scenes.active_name == "day_summary"
    assert app.tutorial.step == "summary"
    click(app, (620, 640))

    assert app.scenes.active_name == "menu"
    assert not app.tutorial.active
    assert not app.game_state.workday_started
    pygame.quit()
