"""Reusable Pygame interface controls."""

import pygame
from game import config


def text(surface, value, font, color, position, center=False):
    image = font.render(value, True, color)
    rect = image.get_rect(center=position) if center else image.get_rect(topleft=position)
    surface.blit(image, rect)
    return rect


class Button:
    def __init__(self, rect, label, font, action, color=config.ORANGE):
        self.rect = pygame.Rect(rect)
        self.label, self.font, self.action, self.color = label, font, action, color
        self.pressed = False
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            activate = self.pressed and self.rect.collidepoint(event.pos)
            self.pressed = False
            if activate:
                self.action()

    def draw(self, surface):
        hover = self.hovered
        color = config.ORANGE_HOVER if hover else self.color
        if self.pressed:
            color = tuple(max(0, channel - 30) for channel in color)
        pygame.draw.rect(surface, (20, 18, 18), self.rect.move(0, 5), border_radius=8)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, config.CREAM, self.rect, 2, border_radius=8)
        text(surface, self.label, self.font, config.INK, self.rect.center, center=True)


def draw_order_ticket(surface, rect, assets, state):
    """Draw the active or next order without coupling models to Pygame."""
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, config.PARCHMENT, rect, border_radius=8)
    pygame.draw.rect(surface, (176, 139, 88), rect, 4, border_radius=8)
    active = state.active_customer
    waiting = state.customer_queue.pending[0] if state.customer_queue.pending else None
    customer = active or waiting
    text(surface, "ORDER TICKET", assets.font(25, True), config.INK, (rect.centerx, rect.y + 38), True)
    if customer is None:
        text(surface, "No customer waiting", assets.font(18), config.INK, (rect.centerx, rect.y + 105), True)
        return
    order = customer.order
    status = "ACTIVE" if active else "WAITING"
    lines = [
        f"{customer.name} — {customer.category.value.title()}",
        f"{order.material.title()} {order.weapon_type.title()}",
        f"Handle: {order.required_components['handle'].title()}",
        f"Guard: {order.required_components['guard'].title()}",
        f"Patience: {order.remaining_patience:.0f}s",
        f"Status: {status}",
    ]
    for index, line in enumerate(lines):
        text(surface, line, assets.font(17, index == 1), config.INK, (rect.x + 24, rect.y + 78 + index * 36))


def draw_progress(surface, rect, progress, label, assets):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, (28, 27, 27), rect, border_radius=8)
    inner = rect.inflate(-6, -6)
    fill = inner.copy()
    fill.width = round(inner.width * max(0.0, min(1.0, progress)))
    pygame.draw.rect(surface, config.ORANGE, fill, border_radius=6)
    pygame.draw.rect(surface, config.METAL, rect, 2, border_radius=8)
    text(surface, f"{label}: {progress * 100:.0f}%", assets.font(16, True), config.CREAM, rect.center, True)


def draw_workpiece(surface, center, workpiece, scale=1.0):
    """Procedural workpiece art shared by the hotbar and station work areas."""
    if workpiece is None:
        return
    x, y = center
    metal = (105, 110, 112) if workpiece.selected_material == "iron" else (174, 184, 190)
    if workpiece.stage.value == "raw":
        points = [(x - 70 * scale, y - 22 * scale), (x + 60 * scale, y - 22 * scale),
                  (x + 75 * scale, y + 20 * scale), (x - 85 * scale, y + 20 * scale)]
        pygame.draw.polygon(surface, metal, points)
        pygame.draw.polygon(surface, config.CREAM, points, max(1, round(2 * scale)))
        return
    length = 145 * scale if workpiece.weapon_type == "dagger" else 220 * scale
    blade = [(x - length / 2, y - 17 * scale), (x + length / 2 - 25 * scale, y - 17 * scale),
             (x + length / 2, y), (x + length / 2 - 25 * scale, y + 17 * scale), (x - length / 2, y + 17 * scale)]
    pygame.draw.polygon(surface, metal, blade)
    pygame.draw.polygon(surface, config.CREAM, blade, max(1, round(2 * scale)))
    if workpiece.stage.value in ("assembled", "delivered"):
        pygame.draw.rect(surface, (170, 128, 70), (x - length / 2 - 65 * scale, y - 13 * scale, 70 * scale, 26 * scale), border_radius=5)
        pygame.draw.rect(surface, (198, 166, 92), (x - length / 2 - 8 * scale, y - 35 * scale, 13 * scale, 70 * scale), border_radius=3)
