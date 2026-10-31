"""Delivery score breakdown."""

import pygame

from game import config
from game.scenes.base import BaseScene
from game.ui import Button, text


class ResultsScene(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.continue_button = Button((500, 620, 280, 54), "Continue", app.assets.font(24, True), self._continue)

    def _continue(self):
        state = self.app.game_state
        destination = "shop" if state.customer_queue.pending else "day_summary"
        self.app.scenes.switch(destination)

    def handle_event(self, event):
        self.continue_button.handle_event(event)

    def draw(self, surface):
        surface.fill(config.CHARCOAL)
        result = self.app.game_state.last_result
        panel = pygame.Rect(220, 55, 840, 530)
        pygame.draw.rect(surface, config.PARCHMENT, panel, border_radius=14)
        pygame.draw.rect(surface, (176, 139, 88), panel, 5, border_radius=14)
        text(surface, "ORDER DELIVERED", self.app.assets.font(42, True), config.INK, (640, 105), True)
        if not result:
            text(surface, "No result is available.", self.app.assets.font(24), config.INK, (640, 300), True)
        else:
            text(surface, result["rating"].upper(), self.app.assets.font(34, True), config.ORANGE, (640, 165), True)
            rows = [
                ("Order accuracy", result["accuracy"]),
                ("Craftsmanship", result["craftsmanship"]),
                ("Delivery speed", result["speed"]),
                ("Final score", result["total"]),
            ]
            for index, (label, value) in enumerate(rows):
                y = 225 + index * 55
                text(surface, label, self.app.assets.font(22, index == 3), config.INK, (345, y))
                text(surface, f"{value:.0f}/100", self.app.assets.font(22, True), config.INK, (860, y), True)
            text(surface, f"Payment: {result['payout']} gold     Reputation: +{result['reputation_change']}", self.app.assets.font(23, True), config.INK, (640, 465), True)
            text(surface, f"“{result['response']}”", self.app.assets.font(20), config.INK, (640, 525), True)
        self.continue_button.draw(surface)
