"""Pygame application ownership and central loop."""

import pygame
from game import config
from game.assets import AssetManager
from game.scene_manager import SceneManager
from game.state import GameState
from game.scenes.menu import InstructionsScene, MainMenuScene
from game.scenes.menu import OptionsScene
from game.scenes.results_scene import ResultsScene
from game.scenes.day_summary import DaySummaryScene
from game.scenes.shop_scene import ShopScene
from game.scenes.station_scene import StationScene


class GameApp:
    def __init__(self):
        pygame.init()
        self.display_mode = "windowed"
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        self.canvas = pygame.Surface((config.WIDTH, config.HEIGHT))
        self.viewport = pygame.Rect(0, 0, config.WIDTH, config.HEIGHT)
        pygame.display.set_caption(config.TITLE)
        self.clock = pygame.time.Clock()
        self.assets = AssetManager()
        self.game_state = GameState()
        self.scenes = SceneManager()
        self.running = False
        self.scenes.register("menu", lambda: MainMenuScene(self))
        self.scenes.register("instructions", lambda: InstructionsScene(self))
        self.scenes.register("options", lambda: OptionsScene(self))
        self.scenes.register("shop", lambda: ShopScene(self))
        self.scenes.register("station", lambda: StationScene(self))
        self.scenes.register("results", lambda: ResultsScene(self))
        self.scenes.register("day_summary", lambda: DaySummaryScene(self))
        self.scenes.switch("menu")

    def start_or_resume_workday(self):
        self.game_state.start_day()
        self.scenes.switch("shop")

    def request_quit(self):
        self.running = False

    def set_display_mode(self, mode):
        if mode not in ("windowed", "fullscreen"):
            raise ValueError("Unknown display mode")
        desktop = pygame.display.get_desktop_sizes()[0]
        if mode == "windowed":
            size, flags = (config.WIDTH, config.HEIGHT), 0
        else:
            size, flags = desktop, pygame.FULLSCREEN
        try:
            self.screen = pygame.display.set_mode(size, flags)
            self.display_mode = mode
        except pygame.error:
            self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
            self.display_mode = "windowed"
        self._calculate_viewport()

    def _calculate_viewport(self):
        width, height = self.screen.get_size()
        scale = min(width / config.WIDTH, height / config.HEIGHT)
        scaled = (round(config.WIDTH * scale), round(config.HEIGHT * scale))
        self.viewport = pygame.Rect((width - scaled[0]) // 2, (height - scaled[1]) // 2, *scaled)

    def _logical_event(self, event):
        if not hasattr(event, "pos"):
            return event
        x = (event.pos[0] - self.viewport.x) * config.WIDTH / self.viewport.width
        y = (event.pos[1] - self.viewport.y) * config.HEIGHT / self.viewport.height
        values = event.dict.copy()
        values["pos"] = (round(x), round(y))
        if "rel" in values:
            values["rel"] = (
                round(values["rel"][0] * config.WIDTH / self.viewport.width),
                round(values["rel"][1] * config.HEIGHT / self.viewport.height),
            )
        return pygame.event.Event(event.type, values)

    def _present(self):
        self.screen.fill((0, 0, 0))
        if self.viewport.size == self.canvas.get_size():
            self.screen.blit(self.canvas, self.viewport)
        else:
            self.screen.blit(pygame.transform.smoothscale(self.canvas, self.viewport.size), self.viewport)
        pygame.display.flip()

    def run(self):
        self.running = True
        while self.running:
            delta_time = min(self.clock.tick(config.FPS) / 1000.0, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.request_quit()
                else:
                    self.scenes.handle_event(self._logical_event(event))
            self.scenes.update(delta_time)
            self.scenes.draw(self.canvas)
            self._present()
        pygame.quit()
