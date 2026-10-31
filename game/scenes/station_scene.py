"""Interactive work screens for the complete sample-order workflow."""

import math
import pygame

from game import config
from game.scenes.base import BaseScene
from game.stations import create_controller
from game.ui import Button, draw_order_ticket, draw_progress, draw_workpiece, text


AREA_INFO = {
    "customer_counter": ("Customer Counter", "Click the counter to accept or deliver the current order."),
    "storage": ("Material Storage", "Click an actual metal ingot in a storage bin."),
    "furnace": ("Furnace", "Click the hotbar metal to insert it; click the heated metal when ready."),
    "mold": ("Weapon Mold", "Choose the matching mold, insert the metal, then hold the ladle until full."),
    "anvil": ("Anvil", "Place the blade, then click every glowing hammer point."),
    "quench": ("Quench Tub", "Place the blade, drag it into the water, and hold until quenched."),
    "grindstone": ("Grindstone", "Place the blade, crank the wheel to full speed, then sweep the edge left and right."),
    "assembly": ("Assembly Bench", "Place the blade, then drag the requested handle and guard onto it."),
}

HOTBAR = pygame.Rect(475, 625, 330, 72)
WORK_RECT = pygame.Rect(45, 135, 825, 450)
FURNACE_RECT = pygame.Rect(265, 215, 390, 260)
MOLD_RECT = pygame.Rect(265, 310, 360, 170)
ANVIL_RECT = pygame.Rect(220, 315, 485, 145)
QUENCH_WATER = pygame.Rect(230, 340, 440, 170)
QUENCH_BLADE = pygame.Rect(330, 210, 260, 65)
QUENCH_TRACK_X = QUENCH_WATER.centerx
QUENCH_TOP_Y = QUENCH_BLADE.centery
QUENCH_SUBMERGED_Y = 405
GRIND_WHEEL_CENTER = (500, 375)
GRIND_WHEEL_RADIUS = 135
GRIND_CRANK = pygame.Rect(105, 255, 135, 175)
GRIND_BLADE_Y = 255
GRIND_MIN_X = 355
GRIND_MAX_X = 650
ASSEMBLY_BLADE = pygame.Rect(300, 270, 390, 130)
ASSEMBLY_COMPONENT_CARDS = (
    ("handle", "oak", pygame.Rect(95, 170, 145, 50)),
    ("handle", "leather", pygame.Rect(95, 230, 145, 50)),
    ("handle", "walnut", pygame.Rect(95, 290, 145, 50)),
    ("guard", "simple", pygame.Rect(95, 380, 145, 50)),
    ("guard", "cross", pygame.Rect(95, 440, 145, 50)),
    ("guard", "curved", pygame.Rect(95, 500, 145, 50)),
)

ANVIL_TARGETS = [(310, 330), (390, 350), (470, 330), (550, 350), (630, 330)]


class StationScene(BaseScene):
    def __init__(self, app):
        super().__init__(app)
        self.station = "furnace"
        self.controller = None
        self.feedback = ""
        self.holding_pour = False
        self.dragging_quench = False
        self.drag_position = (QUENCH_TRACK_X, QUENCH_TOP_Y)
        self.dragging_grind = False
        self.grind_position = (470, GRIND_BLADE_Y)
        self.drag_component = None
        self.back = Button((25, 642, 230, 48), "Back to Workshop", app.assets.font(20, True), lambda: app.scenes.switch("shop"))

    def on_enter(self, **kwargs):
        requested = kwargs.get("station", "furnace")
        self.station = requested if requested in AREA_INFO else "furnace"
        self.controller = create_controller(self.station, self.app.game_state.active_workpiece, self.app.game_state.active_order)
        self.feedback = ""
        if self.controller and self.controller.completed:
            self.feedback = "Station complete — the workpiece is back in Current Work."
        self.holding_pour = False
        self.dragging_quench = False
        self.dragging_grind = False
        self.grind_position = (470, GRIND_BLADE_Y)
        self.drag_component = None

    def _refresh_controller(self):
        self.controller = create_controller(self.station, self.app.game_state.active_workpiece, self.app.game_state.active_order)

    def _accept_or_deliver(self):
        state = self.app.game_state
        try:
            if state.active_workpiece and state.active_workpiece.can_deliver:
                state.deliver_active_order()
                self.app.scenes.switch("results")
            elif state.active_customer:
                self.feedback = "Finish the weapon before delivery."
            else:
                customer = state.accept_next_order()
                self.feedback = f"Accepted {customer.name}'s {customer.order.weapon_type} order."
                self._refresh_controller()
        except ValueError as error:
            self.feedback = str(error)

    def _select_material(self, material):
        try:
            self.app.game_state.select_material(material)
            self.feedback = f"{material.title()} moved into the current-work hotbar."
            self._refresh_controller()
        except ValueError as error:
            self.feedback = str(error)

    def _hotbar_clicked(self):
        if not self.controller:
            self.feedback = "This area does not accept a workpiece."
            return
        if self.station == "furnace":
            self.controller.toggle()
        else:
            self.controller.place()
        self.feedback = self.controller.feedback

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.scenes.switch("shop")
            return
        self.back.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if HOTBAR.collidepoint(pos):
                self._hotbar_clicked()
                return
            if self.station == "customer_counter" and pygame.Rect(250, 275, 420, 150).collidepoint(pos):
                self._accept_or_deliver()
            elif self.station == "storage":
                if pygame.Rect(145, 245, 260, 210).collidepoint(pos):
                    self._select_material("iron")
                elif pygame.Rect(500, 245, 260, 210).collidepoint(pos):
                    self._select_material("steel")
            elif self.station == "furnace" and FURNACE_RECT.collidepoint(pos):
                self.controller.toggle()
                self.feedback = self.controller.feedback
            elif self.station == "mold":
                if pygame.Rect(150, 175, 250, 90).collidepoint(pos):
                    self.controller.select_mold("dagger")
                elif pygame.Rect(515, 175, 250, 90).collidepoint(pos):
                    self.controller.select_mold("sword")
                elif pygame.Rect(675, 325, 145, 115).collidepoint(pos):
                    self.holding_pour = True
                self.feedback = self.controller.feedback
            elif self.station == "anvil":
                for index, target in enumerate(ANVIL_TARGETS):
                    if pygame.Vector2(pos).distance_to(target) <= 28:
                        self.controller.hit(index)
                        self.feedback = self.controller.feedback
                        break
            elif self.station == "quench" and QUENCH_BLADE.collidepoint(pos):
                workpiece = self.app.game_state.active_workpiece
                if workpiece and workpiece.location == "quench":
                    self.dragging_quench = True
                    self.drag_position = (QUENCH_TRACK_X, max(QUENCH_TOP_Y, min(QUENCH_SUBMERGED_Y, pos[1])))
            elif self.station == "grindstone":
                if GRIND_CRANK.collidepoint(pos):
                    self.controller.crank()
                    self.feedback = self.controller.feedback
                else:
                    blade_rect = pygame.Rect(0, 0, 300, 70)
                    blade_rect.center = self.grind_position
                    workpiece = self.app.game_state.active_workpiece
                    if workpiece and workpiece.location == "grindstone" and blade_rect.collidepoint(pos):
                        self.dragging_grind = True
            elif self.station == "assembly":
                for kind, value, rect in self._component_cards():
                    if rect.collidepoint(pos):
                        self.drag_component = (kind, value)
                        self.drag_position = pos
                        break

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_quench:
                y = max(QUENCH_TOP_Y, min(QUENCH_SUBMERGED_Y, event.pos[1]))
                self.drag_position = (QUENCH_TRACK_X, y)
            elif self.dragging_grind:
                old_x = self.grind_position[0]
                new_x = max(GRIND_MIN_X, min(GRIND_MAX_X, event.pos[0]))
                self.grind_position = (new_x, GRIND_BLADE_Y)
                self.controller.sharpen_sweep(new_x - old_x)
                self.feedback = self.controller.feedback
                if self.controller.completed:
                    self.dragging_grind = False
            elif self.drag_component:
                self.drag_position = event.pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.holding_pour = False
            self.dragging_grind = False
            if self.dragging_quench:
                if not (self.controller and self.controller.completed):
                    self.controller.release_early()
                    self.feedback = self.controller.feedback
                self.dragging_quench = False
                self.drag_position = (QUENCH_TRACK_X, QUENCH_TOP_Y)
            if self.drag_component:
                kind, value = self.drag_component
                target = self._assembly_target(kind)
                if target.collidepoint(event.pos):
                    self.controller.drop_component(kind, value)
                    self.feedback = self.controller.feedback
                else:
                    self.feedback = "Drag the component onto its highlighted target."
                self.drag_component = None

    def update(self, delta_time):
        self.app.game_state.update(delta_time)
        if not self.controller:
            return
        if self.station == "furnace":
            self.controller.update(delta_time)
        elif self.station == "mold" and self.holding_pour:
            self.controller.pour(delta_time)
        elif self.station == "quench" and self.dragging_quench and self.drag_position[1] >= QUENCH_SUBMERGED_Y:
            self.controller.hold_in_water(delta_time)
        elif self.station == "grindstone":
            self.controller.update(delta_time)
        if self.controller.feedback:
            self.feedback = self.controller.feedback

    def draw(self, surface):
        title, instruction = AREA_INFO[self.station]
        surface.fill(config.CHARCOAL)
        pygame.draw.rect(surface, config.PANEL, WORK_RECT, border_radius=14)
        pygame.draw.rect(surface, (84, 73, 63), WORK_RECT, 3, border_radius=14)
        text(surface, title.upper(), self.app.assets.font(38, True), config.CREAM, (455, 42), True)
        text(surface, instruction, self.app.assets.font(17), config.ORANGE_HOVER, (455, 92), True)
        draw_order_ticket(surface, (910, 92, 340, 430), self.app.assets, self.app.game_state)
        self._draw_station(surface)
        self._draw_hotbar(surface)
        feedback = self.feedback or "Follow the instructions above."
        text(surface, feedback, self.app.assets.font(16), config.ORANGE_HOVER, (1080, 592), True)
        self.back.draw(surface)

    def _draw_hotbar(self, surface):
        pygame.draw.rect(surface, (22, 21, 21), HOTBAR, border_radius=10)
        pygame.draw.rect(surface, config.ORANGE, HOTBAR, 3, border_radius=10)
        text(surface, "CURRENT WORK", self.app.assets.font(14, True), config.CREAM, (HOTBAR.x + 12, HOTBAR.y + 7))
        workpiece = self.app.game_state.active_workpiece
        if not workpiece:
            text(surface, "Empty", self.app.assets.font(19), config.METAL, HOTBAR.center, True)
        elif workpiece.location == "hotbar":
            draw_workpiece(surface, (HOTBAR.centerx + 35, HOTBAR.centery + 10), workpiece, 0.65)
        else:
            text(surface, f"In {workpiece.location.title()}", self.app.assets.font(18), config.METAL, (HOTBAR.centerx + 25, HOTBAR.centery + 10), True)

    def _draw_station(self, surface):
        method = getattr(self, f"_draw_{self.station}")
        method(surface)
        if self.controller:
            draw_progress(surface, (920, 535, 320, 28), self.controller.progress, "Station progress", self.app.assets)

    def _draw_customer_counter(self, surface):
        counter = pygame.Rect(250, 275, 420, 150)
        pygame.draw.rect(surface, config.WOOD, counter, border_radius=10)
        pygame.draw.rect(surface, (177, 123, 66), (counter.x, counter.y, counter.w, 28), border_radius=10)
        state = self.app.game_state
        if state.active_workpiece and state.active_workpiece.can_deliver:
            label = "CLICK COUNTER TO DELIVER"
        elif state.active_customer:
            label = "ORDER IN PROGRESS"
        elif state.customer_queue.pending:
            label = "CLICK COUNTER TO ACCEPT"
        else:
            label = "NO CUSTOMERS WAITING"
        text(surface, label, self.app.assets.font(24, True), config.CREAM, counter.center, True)

    def _draw_storage(self, surface):
        for label, material, rect, color in (
            ("IRON INGOTS", "iron", pygame.Rect(145, 245, 260, 210), (105, 110, 112)),
            ("STEEL INGOTS", "steel", pygame.Rect(500, 245, 260, 210), (174, 184, 190)),
        ):
            pygame.draw.rect(surface, config.WOOD, rect, border_radius=10)
            pygame.draw.rect(surface, (64, 42, 28), rect, 8, border_radius=10)
            text(surface, label, self.app.assets.font(22, True), config.CREAM, (rect.centerx, rect.y + 30), True)
            for row in range(2):
                for col in range(3):
                    x, y = rect.x + 40 + col * 65, rect.y + 80 + row * 55
                    pygame.draw.polygon(surface, color, [(x, y), (x + 50, y), (x + 43, y + 28), (x - 7, y + 28)])
            count = self.app.game_state.player.inventory[material]
            text(surface, f"Available: {count}", self.app.assets.font(17), config.CREAM, (rect.centerx, rect.bottom - 22), True)

    def _draw_furnace(self, surface):
        pygame.draw.rect(surface, (68, 58, 52), FURNACE_RECT, border_radius=25)
        pygame.draw.rect(surface, (115, 104, 88), FURNACE_RECT, 14, border_radius=25)
        pygame.draw.circle(surface, (184, 66, 29), FURNACE_RECT.center, 105)
        pygame.draw.circle(surface, config.ORANGE_HOVER, FURNACE_RECT.center, 70)
        workpiece = self.app.game_state.active_workpiece
        if workpiece and workpiece.location == "furnace":
            draw_workpiece(surface, FURNACE_RECT.center, workpiece, 0.9)
            remaining = max(0.0, self.controller.duration * (1 - self.controller.progress))
            text(surface, "READY — CLICK METAL" if remaining == 0 else f"Heating: {remaining:.1f}s", self.app.assets.font(22, True), config.CREAM, (FURNACE_RECT.centerx, FURNACE_RECT.bottom + 35), True)

    def _draw_mold(self, surface):
        for label, rect in (("DAGGER MOLD", pygame.Rect(150, 175, 250, 90)), ("SWORD MOLD", pygame.Rect(515, 175, 250, 90))):
            selected = self.app.game_state.active_workpiece and self.app.game_state.active_workpiece.selected_mold == label.split()[0].lower()
            pygame.draw.rect(surface, config.ORANGE if selected else (105, 94, 78), rect, border_radius=12)
            text(surface, label, self.app.assets.font(20, True), config.CREAM, rect.center, True)
        pygame.draw.rect(surface, (95, 83, 69), MOLD_RECT, border_radius=30)
        pygame.draw.rect(surface, config.METAL, MOLD_RECT, 7, border_radius=30)
        workpiece = self.app.game_state.active_workpiece
        if workpiece and workpiece.location == "mold":
            draw_workpiece(surface, MOLD_RECT.center, workpiece, 0.85)
        ladle = pygame.Rect(675, 325, 145, 115)
        pygame.draw.circle(surface, config.METAL, (ladle.x + 50, ladle.y + 58), 38)
        pygame.draw.line(surface, config.WOOD, (ladle.x + 80, ladle.y + 35), (ladle.right, ladle.y), 14)
        text(surface, "HOLD TO POUR", self.app.assets.font(16, True), config.CREAM, (ladle.centerx, ladle.bottom + 22), True)

    def _draw_anvil(self, surface):
        pygame.draw.polygon(surface, config.METAL, [(ANVIL_RECT.x, ANVIL_RECT.y), (ANVIL_RECT.right, ANVIL_RECT.y), (ANVIL_RECT.right - 70, ANVIL_RECT.bottom), (ANVIL_RECT.x + 80, ANVIL_RECT.bottom)])
        workpiece = self.app.game_state.active_workpiece
        if workpiece and workpiece.location == "anvil":
            draw_workpiece(surface, (465, 325), workpiece, 1.25)
        hits = self.controller.hits if self.controller else set()
        for index, point in enumerate(ANVIL_TARGETS):
            color = (87, 177, 96) if index in hits else config.ORANGE_HOVER
            pygame.draw.circle(surface, color, point, 20)
            pygame.draw.circle(surface, config.CREAM, point, 20, 3)

    def _draw_quench(self, surface):
        pygame.draw.rect(surface, config.WOOD, QUENCH_WATER.inflate(30, 30), border_radius=28)
        pygame.draw.rect(surface, (61, 132, 165), QUENCH_WATER, border_radius=20)
        pygame.draw.line(surface, (133, 205, 218), (QUENCH_WATER.x + 20, QUENCH_WATER.y + 35), (QUENCH_WATER.right - 20, QUENCH_WATER.y + 35), 4)
        pygame.draw.line(surface, (107, 91, 74), (QUENCH_TRACK_X, QUENCH_TOP_Y), (QUENCH_TRACK_X, QUENCH_SUBMERGED_Y), 3)
        workpiece = self.app.game_state.active_workpiece
        if workpiece and workpiece.location == "quench":
            position = self.drag_position if self.dragging_quench else (QUENCH_TRACK_X, QUENCH_TOP_Y)
            draw_workpiece(surface, position, workpiece, 1.0)
        text(surface, "DRAG STRAIGHT DOWN AND KEEP HOLDING", self.app.assets.font(17, True), config.CREAM, (450, 545), True)

    def _draw_grindstone(self, surface):
        pygame.draw.rect(surface, config.WOOD, GRIND_CRANK, border_radius=12)
        pygame.draw.rect(surface, (67, 43, 27), GRIND_CRANK, 7, border_radius=12)
        text(surface, "CRANK", self.app.assets.font(18, True), config.CREAM, (GRIND_CRANK.centerx, GRIND_CRANK.y + 25), True)
        crank_center = (GRIND_CRANK.centerx, GRIND_CRANK.centery + 15)
        pygame.draw.circle(surface, config.METAL, crank_center, 34, 7)
        pygame.draw.line(surface, config.METAL, crank_center, (crank_center[0] + 42, crank_center[1] - 35), 8)
        for index in range(self.controller.required_cranks):
            color = config.ORANGE if index < self.controller.crank_clicks else (80, 72, 65)
            pygame.draw.circle(surface, color, (GRIND_CRANK.x + 18 + index * 16, GRIND_CRANK.bottom - 24), 6)

        pygame.draw.circle(surface, (112, 115, 111), GRIND_WHEEL_CENTER, GRIND_WHEEL_RADIUS)
        pygame.draw.circle(surface, (176, 179, 173), GRIND_WHEEL_CENTER, GRIND_WHEEL_RADIUS, 7)
        angle = math.radians(self.controller.wheel_angle)
        for offset in (0, math.pi / 2):
            dx = math.cos(angle + offset) * (GRIND_WHEEL_RADIUS - 16)
            dy = math.sin(angle + offset) * (GRIND_WHEEL_RADIUS - 16)
            pygame.draw.line(surface, (78, 80, 78), (GRIND_WHEEL_CENTER[0] - dx, GRIND_WHEEL_CENTER[1] - dy), (GRIND_WHEEL_CENTER[0] + dx, GRIND_WHEEL_CENTER[1] + dy), 5)
        pygame.draw.circle(surface, config.PANEL, GRIND_WHEEL_CENTER, 28)
        workpiece = self.app.game_state.active_workpiece
        if workpiece and workpiece.location == "grindstone":
            draw_workpiece(surface, self.grind_position, workpiece, 1.2)
        if self.dragging_grind and self.controller.spinning:
            spark_x = max(GRIND_WHEEL_CENTER[0] - 90, min(GRIND_WHEEL_CENTER[0] + 90, self.grind_position[0]))
            for dx, dy in ((-24, -32), (-10, -42), (12, -38), (28, -25)):
                pygame.draw.line(surface, config.ORANGE_HOVER, (spark_x, 290), (spark_x + dx, 290 + dy), 3)
        if self.controller.spinning:
            prompt = "HOLD THE BLADE AND SWEEP LEFT / RIGHT"
        else:
            prompt = f"CLICK THE CRANK {self.controller.required_cranks - self.controller.crank_clicks} MORE TIMES"
        text(surface, prompt, self.app.assets.font(17, True), config.CREAM, (500, 545), True)

    def _component_cards(self):
        return [(kind, value, rect.copy()) for kind, value, rect in ASSEMBLY_COMPONENT_CARDS]

    def _assembly_target(self, kind):
        return pygame.Rect(570, 330, 140, 90) if kind == "handle" else pygame.Rect(410, 300, 120, 120)

    def _draw_assembly(self, surface):
        text(surface, "HANDLES", self.app.assets.font(14, True), config.CREAM, (167, 154), True)
        text(surface, "GUARDS", self.app.assets.font(14, True), config.CREAM, (167, 364), True)
        order = self.app.game_state.active_order
        required = order.required_components if order else {}
        for kind, value, rect in self._component_cards():
            pygame.draw.rect(surface, config.WOOD if kind == "handle" else config.METAL, rect, border_radius=9)
            if required.get(kind) == value:
                pygame.draw.rect(surface, config.ORANGE, rect, 3, border_radius=9)
            text(surface, value.title(), self.app.assets.font(17, True), config.CREAM, rect.center, True)
        workpiece = self.app.game_state.active_workpiece
        if workpiece and workpiece.location == "assembly":
            draw_workpiece(surface, ASSEMBLY_BLADE.center, workpiece, 1.25)
        for kind in ("handle", "guard"):
            rect = self._assembly_target(kind)
            attached = workpiece and kind in workpiece.selected_components
            pygame.draw.rect(surface, (87, 177, 96) if attached else config.ORANGE, rect, 4, border_radius=9)
            text(surface, f"{kind.title()} target", self.app.assets.font(15, True), config.CREAM, (rect.centerx, rect.bottom + 18), True)
        if self.drag_component:
            kind, value = self.drag_component
            card = pygame.Rect(0, 0, 130, 55)
            card.center = self.drag_position
            pygame.draw.rect(surface, config.WOOD if kind == "handle" else config.METAL, card, border_radius=8)
            text(surface, value.title(), self.app.assets.font(16, True), config.CREAM, card.center, True)
