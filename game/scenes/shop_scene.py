import pygame
from game import config
from game.scenes.base import BaseScene
from game.ui import Button, draw_workpiece, text


HOTSPOTS = [
    ("customer_counter", "Customer Counter", (420, 110, 450, 155)),
    ("mold", "Mold Station", (260, 225, 325, 250)),
    ("anvil", "Anvil", (725, 240, 300, 250)),
    ("furnace", "Furnace", (850, 0, 430, 390)),
    ("quench", "Quench Tub", (965, 390, 315, 290)),
    ("grindstone", "Grindstone", (0, 405, 360, 250)),
    ("assembly", "Assembly Bench", (380, 460, 525, 250)),
    ("storage", "Material Storage", (110, 20, 300, 310)),
]

HOTSPOT_RECTS = {key: pygame.Rect(rect) for key, _label, rect in HOTSPOTS}
HOTSPOT_LABELS = {key: label for key, label, _rect in HOTSPOTS}
BLACKSMITH_POSITION = (560, 255)
CUSTOMER_POSITION = (578, 57)


def blacksmith_frame_index(animation_time):
    """Rest most of the time, then make one short hammer-lift gesture."""
    phase = animation_time % 3.0
    if phase < 2.175:
        return 0
    if phase < 2.30:
        return 1
    if phase < 2.45:
        return 2
    if phase < 2.60:
        return 3
    if phase < 2.725:
        return 1
    return 0


def customer_frame_index(animation_time):
    """Continuously cycle the customer's restrained three-frame idle."""
    return int(animation_time * 2.0) % 3


class ShopScene(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.background = app.assets.image("workshop", "background.png")
        self.station_bases = app.assets.image("workshop", "station_bases.png")
        self.counter_layer = app.assets.image("workshop", "customer_counter.png")
        self.station_masks = {}
        self.station_outlines = {}
        for key, _label, _rect in HOTSPOTS:
            mask_image = app.assets.image("workshop", "masks", f"{key}.png")
            if mask_image:
                mask = pygame.mask.from_surface(mask_image, 96)
                self.station_masks[key] = mask
                self.station_outlines[key] = mask.outline(2)
        self.blacksmith_frames = [
            app.assets.image("characters", "blacksmith_idle", f"frame_{index:02}.png")
            for index in range(1, 5)
        ]
        self.customer_frames = [
            app.assets.image("characters", "customer_idle", f"frame_{index:02}.png")
            for index in range(1, 4)
        ]
        self.blacksmith_shadow = pygame.Surface((116, 34), pygame.SRCALPHA)
        pygame.draw.ellipse(self.blacksmith_shadow, (20, 16, 13, 24), (0, 3, 116, 28))
        pygame.draw.ellipse(self.blacksmith_shadow, (20, 16, 13, 38), (12, 8, 92, 21))
        pygame.draw.ellipse(self.blacksmith_shadow, (20, 16, 13, 54), (28, 12, 60, 14))
        self.animation_time = 0.0
        self.hovered_station = None
        self.pressed_station = None
        self.menu = Button((25, 650, 165, 44), "Main Menu", app.assets.font(19, True), lambda: app.scenes.switch("menu"))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.scenes.switch("menu")
            return
        if hasattr(event, "pos") and self.menu.rect.collidepoint(event.pos):
            if event.type == pygame.MOUSEMOTION:
                self.hovered_station = None
            self.menu.handle_event(event)
            return
        if event.type == pygame.MOUSEMOTION:
            self.hovered_station = self._station_at(event.pos, silhouette_only=True)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed_station = self._station_at(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            released = self._station_at(event.pos)
            if released and released == self.pressed_station:
                self.app.scenes.switch("station", station=released)
            self.pressed_station = None
        self.menu.handle_event(event)

    def update(self, delta_time):
        self.app.game_state.update(delta_time)
        self.animation_time += delta_time

    def _station_at(self, position, silhouette_only=False):
        if position[1] < 70:
            return None
        for key, _label, _rect in HOTSPOTS:
            rect = HOTSPOT_RECTS[key]
            if not rect.collidepoint(position):
                continue
            mask = self.station_masks.get(key)
            local = (position[0] - rect.x, position[1] - rect.y)
            if mask and 0 <= local[0] < mask.get_size()[0] and 0 <= local[1] < mask.get_size()[1] and mask.get_at(local):
                return key
        if silhouette_only:
            return None
        for key, _label, _rect in HOTSPOTS:
            if HOTSPOT_RECTS[key].collidepoint(position):
                return key
        return None

    def draw(self, surface):
        self._draw_workshop_art(surface)
        self._draw_hover(surface)
        top_bar = pygame.Surface((config.WIDTH, 70), pygame.SRCALPHA)
        top_bar.fill((*config.CHARCOAL, 238))
        surface.blit(top_bar, (0, 0))
        text(surface, "WORKSHOP OVERVIEW", self.app.assets.font(34, True), config.CREAM, (28, 15))
        state = self.app.game_state
        order = state.active_order
        status = "No active order — visit the counter"
        if order:
            material = state.active_workpiece.selected_material or "material not selected"
            status = f"Day {state.current_day}  |  {order.weapon_type.title()}  |  {material.title()}  |  {order.remaining_patience:.0f}s"
        text(surface, status, self.app.assets.font(18), config.ORANGE_HOVER, (925, 34), center=True)
        bottom_bar = pygame.Surface((config.WIDTH, 90), pygame.SRCALPHA)
        bottom_bar.fill((28, 25, 23, 226))
        surface.blit(bottom_bar, (0, 630))
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

    def _draw_workshop_art(self, surface):
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill((74, 66, 56))
            pygame.draw.rect(surface, (95, 88, 75), (45, 70, 1190, 560), border_radius=16)
        if self.station_bases:
            surface.blit(self.station_bases, (0, 0))
        customer_waiting = self.app.game_state.active_customer or self.app.game_state.customer_queue.pending
        customer_frames = [frame for frame in self.customer_frames if frame]
        if customer_waiting and customer_frames:
            index = customer_frame_index(self.animation_time) % len(customer_frames)
            surface.blit(customer_frames[index], CUSTOMER_POSITION)
        if self.counter_layer:
            surface.blit(self.counter_layer, (0, 0))
        blacksmith_frames = [frame for frame in self.blacksmith_frames if frame]
        if blacksmith_frames:
            surface.blit(self.blacksmith_shadow, (582, 449))
            index = blacksmith_frame_index(self.animation_time) % len(blacksmith_frames)
            surface.blit(blacksmith_frames[index], BLACKSMITH_POSITION)

    def _draw_hover(self, surface):
        key = self.hovered_station
        if not key:
            return
        rect = HOTSPOT_RECTS[key]
        points = [(rect.x + x, rect.y + y) for x, y in self.station_outlines.get(key, [])]
        if len(points) > 2:
            pygame.draw.lines(surface, config.ORANGE_HOVER, True, points, 4)
            pygame.draw.lines(surface, config.CREAM, True, points, 1)
        label = HOTSPOT_LABELS[key]
        font = self.app.assets.font(17, True)
        width = font.size(label)[0] + 30
        tooltip = pygame.Rect(0, 0, width, 38)
        tooltip.centerx = rect.centerx
        tooltip.bottom = min(625, max(100, rect.bottom - 6))
        tooltip.clamp_ip(pygame.Rect(8, 76, 1264, 545))
        pygame.draw.rect(surface, (31, 27, 24), tooltip, border_radius=7)
        pygame.draw.rect(surface, config.ORANGE_HOVER, tooltip, 2, border_radius=7)
        text(surface, label, font, config.CREAM, tooltip.center, True)
