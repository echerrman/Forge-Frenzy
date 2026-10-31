import pygame
from game import config
from game.scenes.base import BaseScene
from game.ui import Button, draw_workpiece, text


HOTSPOTS = [
    ("customer_counter", "Customer Counter", (455, 105, 370, 88)),
    ("storage", "Storage", (75, 185, 220, 190)),
    ("furnace", "Furnace", (950, 180, 245, 190)),
    ("mold", "Mold", (330, 230, 190, 130)),
    ("anvil", "Anvil", (690, 270, 205, 145)),
    ("quench", "Quench Tub", (965, 430, 210, 145)),
    ("grindstone", "Grindstone", (90, 440, 245, 145)),
    ("assembly", "Assembly Bench", (425, 455, 360, 130)),
]


class ShopScene(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.buttons = []
        for key, label, rect in HOTSPOTS:
            self.buttons.append(Button(rect, label, app.assets.font(18, True), lambda area=key: app.scenes.switch("station", station=area), (178, 139, 87)))
        self.menu = Button((25, 650, 165, 44), "Main Menu", app.assets.font(19, True), lambda: app.scenes.switch("menu"))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.scenes.switch("menu")
        for button in self.buttons:
            button.handle_event(event)
        self.menu.handle_event(event)

    def update(self, delta_time):
        self.app.game_state.update(delta_time)

    def draw(self, surface):
        surface.fill((74, 66, 56))
        pygame.draw.rect(surface, (95, 88, 75), (45, 70, 1190, 560), border_radius=16)
        for row in range(7):
            y = 75 + row * 78
            pygame.draw.line(surface, (113, 103, 87), (50, y), (1230, y), 3)
        pygame.draw.rect(surface, config.CHARCOAL, (0, 0, 1280, 70))
        text(surface, "WORKSHOP OVERVIEW", self.app.assets.font(34, True), config.CREAM, (28, 15))
        state = self.app.game_state
        order = state.active_order
        status = "No active order — visit the counter"
        if order:
            material = state.active_workpiece.selected_material or "material not selected"
            status = f"Day {state.current_day}  |  {order.weapon_type.title()}  |  {material.title()}  |  {order.remaining_patience:.0f}s"
        text(surface, status, self.app.assets.font(18), config.ORANGE_HOVER, (925, 34), center=True)
        for button in self.buttons:
            button.draw(surface)
        hotbar = pygame.Rect(465, 635, 350, 68)
        pygame.draw.rect(surface, (22, 21, 21), hotbar, border_radius=9)
        pygame.draw.rect(surface, config.ORANGE, hotbar, 3, border_radius=9)
        text(surface, "CURRENT WORK", self.app.assets.font(13, True), config.CREAM, (hotbar.x + 10, hotbar.y + 6))
        if state.active_workpiece and state.active_workpiece.location == "hotbar":
            draw_workpiece(surface, (hotbar.centerx + 35, hotbar.centery + 8), state.active_workpiece, 0.62)
        elif state.active_workpiece:
            text(surface, f"In {state.active_workpiece.location.title()}", self.app.assets.font(18), config.METAL, hotbar.center, True)
        else:
            text(surface, "Empty", self.app.assets.font(18), config.METAL, hotbar.center, True)
        text(surface, f"Gold: {state.player.gold}   Reputation: {state.player.reputation}", self.app.assets.font(17, True), config.CREAM, (1130, 670), True)
        self.menu.draw(surface)
