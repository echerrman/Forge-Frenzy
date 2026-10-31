"""End-of-day summary and progression."""

import pygame

from game import config
from game.scenes.base import BaseScene
from game.ui import Button, text


class DaySummaryScene(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.continue_button = Button((470, 610, 340, 58), "Begin Next Day", app.assets.font(24, True), self._next_day)

    def _next_day(self):
        try:
            self.app.game_state.advance_day()
            self.app.scenes.switch("shop")
        except ValueError:
            self.app.scenes.switch("shop")

    def handle_event(self, event):
        self.continue_button.handle_event(event)

    def draw(self, surface):
        surface.fill(config.CHARCOAL)
        state = self.app.game_state
        records = state.day_records()
        gold = sum(record["payout"] for record in records)
        average = sum(record["total"] for record in records) / len(records) if records else 0
        panel = pygame.Rect(280, 80, 720, 470)
        pygame.draw.rect(surface, config.PARCHMENT, panel, border_radius=14)
        pygame.draw.rect(surface, (176, 139, 88), panel, 5, border_radius=14)
        text(surface, f"DAY {state.current_day} COMPLETE", self.app.assets.font(42, True), config.INK, (640, 135), True)
        rows = [
            ("Orders completed", str(len(records))),
            ("Gold earned", str(gold)),
            ("Average satisfaction", f"{average:.0f}/100"),
            ("Total gold", str(state.player.gold)),
            ("Reputation", str(state.player.reputation)),
        ]
        for index, (label, value) in enumerate(rows):
            y = 220 + index * 57
            text(surface, label, self.app.assets.font(23), config.INK, (375, y))
            text(surface, value, self.app.assets.font(23, True), config.INK, (850, y), True)
        self.continue_button.draw(surface)
