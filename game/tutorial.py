"""Guided Day 1 tutorial overlay and progression state machine."""

import pygame

from game import config
from game.items import WeaponStage
from game.ui import text


BACK = pygame.Rect(25, 642, 230, 48)
HOTBAR = pygame.Rect(475, 625, 330, 72)
ORDER_TICKET = pygame.Rect(910, 92, 340, 430)
COUNTER = pygame.Rect(250, 275, 420, 150)

SHOP_TARGETS = {
    "shop_counter": pygame.Rect(455, 105, 370, 88),
    "shop_storage": pygame.Rect(75, 185, 220, 190),
    "shop_furnace": pygame.Rect(950, 180, 245, 190),
    "shop_mold": pygame.Rect(330, 230, 190, 130),
    "shop_anvil": pygame.Rect(690, 270, 205, 145),
    "shop_quench": pygame.Rect(965, 430, 210, 145),
    "shop_grindstone": pygame.Rect(90, 440, 245, 145),
    "shop_assembly": pygame.Rect(425, 455, 360, 130),
    "shop_delivery": pygame.Rect(455, 105, 370, 88),
}

STATION_TARGETS = {
    "furnace_work": [HOTBAR, pygame.Rect(265, 215, 390, 260)],
    "mold_work": [HOTBAR, pygame.Rect(150, 175, 250, 90), pygame.Rect(265, 310, 555, 170)],
    "anvil_work": [HOTBAR, pygame.Rect(220, 280, 485, 180)],
    "quench_work": [HOTBAR, pygame.Rect(200, 185, 500, 355)],
    "grindstone_work": [HOTBAR, pygame.Rect(80, 205, 690, 345)],
    "assembly_work": [HOTBAR, pygame.Rect(70, 140, 700, 430)],
}

MESSAGES = {
    "shop_counter": "Begin at the highlighted Customer Counter.",
    "accept_order": "Click the counter to accept Elin's first order.",
    "order_details": "This ticket shows the material, weapon, handle, guard, and remaining time. Click it to continue.",
    "counter_back": "Return to the workshop overview.",
    "shop_storage": "The order requests iron. Visit the highlighted Storage area.",
    "choose_material": "Click an iron ingot. It will move into Current Work at the bottom.",
    "storage_back": "The iron is ready. Return to the workshop.",
    "shop_furnace": "Next, visit the Furnace to heat the iron.",
    "furnace_work": "Current Work carries your item between stations. Click it, wait for heating, then click the hot metal.",
    "furnace_back": "Heating is complete. Return to the workshop.",
    "shop_mold": "Visit the Mold to form the dagger blank.",
    "mold_work": "Choose the dagger mold, place Current Work, then hold the ladle until full.",
    "mold_back": "The dagger blank is molded. Return to the workshop.",
    "shop_anvil": "Visit the Anvil to shape the blade.",
    "anvil_work": "Place Current Work, then strike every glowing hammer point.",
    "anvil_back": "The blade is shaped. Return to the workshop.",
    "shop_quench": "Visit the Quench Tub to harden the blade.",
    "quench_work": "Place the blade, drag it straight down into the water, and keep holding until complete.",
    "quench_back": "The blade is quenched. Return to the workshop.",
    "shop_grindstone": "Visit the Grindstone to sharpen the edge.",
    "grindstone_work": "Place the blade, crank seven times, then hold and sweep it left and right across the wheel.",
    "grindstone_back": "The edge is sharp. Return to the workshop.",
    "shop_assembly": "Visit the Assembly Bench for the final components.",
    "assembly_work": "Place the blade, then drag the highlighted oak handle and simple guard onto their targets.",
    "assembly_back": "The dagger is assembled. Return to the workshop.",
    "shop_delivery": "Return to the Customer Counter to deliver the finished dagger.",
    "deliver_order": "Click the counter to deliver the dagger to Elin.",
    "results": "Review how accuracy, craftsmanship, and speed produced the final score, then continue.",
    "summary": "This is the end-of-day summary. Finish the tutorial when ready.",
}

WORK_COMPLETION = {
    "furnace_work": WeaponStage.HEATED,
    "mold_work": WeaponStage.MOLDED,
    "anvil_work": WeaponStage.SHAPED,
    "quench_work": WeaponStage.QUENCHED,
    "grindstone_work": WeaponStage.GROUND,
    "assembly_work": WeaponStage.ASSEMBLED,
}

NEXT_AFTER_BACK = {
    "counter_back": "shop_storage",
    "storage_back": "shop_furnace",
    "furnace_back": "shop_mold",
    "mold_back": "shop_anvil",
    "anvil_back": "shop_quench",
    "quench_back": "shop_grindstone",
    "grindstone_back": "shop_assembly",
    "assembly_back": "shop_delivery",
}


class TutorialManager:
    def __init__(self, assets):
        self.assets = assets
        self.active = False
        self.step = None

    def start(self):
        self.active = True
        self.step = "shop_counter"

    def stop(self):
        self.active = False
        self.step = None

    def targets(self):
        if not self.active:
            return []
        if self.step in SHOP_TARGETS:
            return [SHOP_TARGETS[self.step]]
        if self.step in STATION_TARGETS:
            return STATION_TARGETS[self.step]
        if self.step in NEXT_AFTER_BACK or self.step in ("storage_back",):
            return [BACK]
        return {
            "accept_order": [COUNTER],
            "order_details": [ORDER_TICKET],
            "choose_material": [pygame.Rect(145, 245, 260, 210)],
            "deliver_order": [COUNTER],
            "results": [pygame.Rect(500, 620, 280, 54)],
            "summary": [pygame.Rect(470, 610, 340, 58)],
        }.get(self.step, [])

    def allow_event(self, event):
        if not self.active:
            return True
        if event.type == pygame.KEYDOWN:
            return False
        if not hasattr(event, "pos"):
            return True
        inside = any(rect.inflate(12, 12).collidepoint(event.pos) for rect in self.targets())
        if self.step == "order_details" and event.type == pygame.MOUSEBUTTONUP and inside:
            self.step = "counter_back"
            return False
        if event.type == pygame.MOUSEBUTTONUP:
            return True
        return inside

    def update(self, scene_name, state):
        if not self.active:
            return
        workpiece = state.active_workpiece
        if self.step == "shop_counter" and scene_name == "station":
            self.step = "accept_order"
        elif self.step == "accept_order" and state.active_customer:
            self.step = "order_details"
        elif self.step in NEXT_AFTER_BACK and scene_name == "shop":
            self.step = NEXT_AFTER_BACK[self.step]
        elif self.step == "shop_storage" and scene_name == "station":
            self.step = "choose_material"
        elif self.step == "choose_material" and workpiece and workpiece.selected_material == "iron":
            self.step = "storage_back"
        elif self.step == "storage_back" and scene_name == "shop":
            self.step = "shop_furnace"
        elif self.step and self.step.startswith("shop_") and self.step not in ("shop_counter", "shop_storage", "shop_delivery") and scene_name == "station":
            self.step = self.step.removeprefix("shop_") + "_work"
        elif self.step in WORK_COMPLETION and workpiece and workpiece.stage == WORK_COMPLETION[self.step]:
            self.step = self.step.removesuffix("_work") + "_back"
        elif self.step == "shop_delivery" and scene_name == "station":
            self.step = "deliver_order"
        elif self.step == "deliver_order" and scene_name == "results":
            self.step = "results"
        elif self.step == "results" and scene_name == "day_summary":
            self.step = "summary"

    def draw(self, surface):
        if not self.active:
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((16, 17, 18, 185))
        for target in self.targets():
            hole = target.inflate(12, 12)
            pygame.draw.rect(overlay, (0, 0, 0, 0), hole, border_radius=10)
        surface.blit(overlay, (0, 0))
        for target in self.targets():
            pygame.draw.rect(surface, config.ORANGE_HOVER, target.inflate(12, 12), 5, border_radius=10)

        banner = pygame.Rect(270, 8, 740, 82)
        pygame.draw.rect(surface, config.PARCHMENT, banner, border_radius=10)
        pygame.draw.rect(surface, config.ORANGE, banner, 4, border_radius=10)
        text(surface, "TUTORIAL", self.assets.font(16, True), config.ORANGE, (banner.x + 18, banner.y + 12))
        self._draw_wrapped(surface, MESSAGES.get(self.step, "Follow the highlighted step."), banner)

    def _draw_wrapped(self, surface, message, banner):
        font = self.assets.font(17, True)
        words = message.split()
        lines, current = [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if font.size(candidate)[0] > banner.width - 150:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        for index, line in enumerate(lines[:2]):
            text(surface, line, font, config.INK, (banner.x + 120, banner.y + 18 + index * 25))
