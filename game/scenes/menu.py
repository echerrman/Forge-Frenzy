import math
import pygame
from game import config
from game.scenes.base import BaseScene
from game.ui import Button, text


class MainMenuScene(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        font = app.assets.font(29, True)
        self.buttons = [
            Button((505, 350, 270, 55), "Start Workday", font, app.start_or_resume_workday),
            Button((505, 420, 270, 55), "Instructions", font, lambda: app.scenes.switch("instructions")),
            Button((505, 490, 270, 55), "Options", font, lambda: app.scenes.switch("options")),
            Button((505, 560, 270, 55), "Quit", font, app.request_quit, config.RED),
        ]
        self.elapsed = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.request_quit()
        for button in self.buttons:
            button.handle_event(event)

    def update(self, delta_time):
        self.elapsed += delta_time

    def draw(self, surface):
        surface.fill(config.CHARCOAL)
        glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(glow, (232, 101, 32, 40), (640, 255), 125 + int(math.sin(self.elapsed * 2) * 8))
        surface.blit(glow, (0, 0))
        pygame.draw.polygon(surface, config.METAL, [(515, 285), (765, 285), (725, 325), (555, 325)])
        pygame.draw.rect(surface, config.WOOD, (603, 318, 74, 44), border_radius=8)
        text(surface, "FORGE FRENZY", self.app.assets.font(64, True), config.CREAM, (640, 125), True)
        text(surface, "Forged to Order", self.app.assets.font(27), config.ORANGE_HOVER, (640, 186), True)
        text(surface, "A medieval blacksmith workshop", self.app.assets.font(18), config.METAL, (640, 665), True)
        for button in self.buttons:
            button.draw(surface)


class InstructionsScene(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.back = Button((50, 625, 190, 52), "Back", app.assets.font(25, True), lambda: app.scenes.switch("menu"))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.scenes.switch("menu")
        self.back.handle_event(event)

    def draw(self, surface):
        surface.fill(config.CHARCOAL)
        panel = pygame.Rect(165, 80, 950, 500)
        pygame.draw.rect(surface, config.PARCHMENT, panel, border_radius=12)
        pygame.draw.rect(surface, (176, 139, 88), panel, 5, border_radius=12)
        text(surface, "APPRENTICE HANDBOOK", self.app.assets.font(42, True), config.INK, (640, 130), True)
        lines = [
            "Use the mouse to operate the workshop.",
            "1. Accept Elin's dagger order at the Customer Counter.",
            "2. Click the iron ingots in Storage to fill Current Work.",
            "3. Complete Furnace, Mold, Anvil, Quench, Grindstone, and Assembly.",
            "4. Click the hotbar item to place it in each station.",
            "5. Return to the counter to deliver, score, and begin another day.",
        ]
        for index, line in enumerate(lines):
            text(surface, line, self.app.assets.font(23), config.INK, (225, 205 + index * 55))
        self.back.draw(surface)


class OptionsScene(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        font = app.assets.font(24, True)
        self.buttons = [
            Button((455, 240, 370, 58), "Fullscreen", font, lambda: app.set_display_mode("fullscreen")),
            Button((455, 325, 370, 58), "Windowed Fullscreen", font, lambda: app.set_display_mode("borderless")),
            Button((455, 410, 370, 58), "Windowed", font, lambda: app.set_display_mode("windowed")),
            Button((515, 555, 250, 54), "Back", font, lambda: app.scenes.switch("menu")),
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.scenes.switch("menu")
        for button in self.buttons:
            button.handle_event(event)

    def draw(self, surface):
        surface.fill(config.CHARCOAL)
        text(surface, "DISPLAY OPTIONS", self.app.assets.font(46, True), config.CREAM, (640, 105), True)
        text(surface, f"Current mode: {self.app.display_mode.replace('borderless', 'windowed fullscreen').title()}", self.app.assets.font(21), config.ORANGE_HOVER, (640, 175), True)
        for button in self.buttons:
            button.draw(surface)
