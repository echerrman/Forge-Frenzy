"""Central persistent gameplay state."""

from dataclasses import dataclass, field

from game.customers import CustomerQueue, scripted_customers
from game.items import WeaponItem
from game.scoring import ScoreEngine


@dataclass
class PlayerProfile:
    gold: int = 0
    reputation: int = 0
    inventory: dict[str, int] = field(default_factory=lambda: {
        "iron": 4,
        "steel": 3,
        "oak": 3,
        "leather": 2,
        "walnut": 2,
        "simple": 3,
        "cross": 2,
        "curved": 2,
    })
    progression: dict[str, int] = field(default_factory=lambda: {"highest_day": 1})
    active_workpiece: WeaponItem | None = None


@dataclass
class GameState:
    current_day: int = 1
    player: PlayerProfile = field(default_factory=PlayerProfile)
    customer_queue: CustomerQueue = field(default_factory=CustomerQueue)
    score_history: list[dict] = field(default_factory=list)
    workday_started: bool = False
    last_result: dict | None = None

    @property
    def active_customer(self):
        return self.customer_queue.active_customer

    @property
    def active_order(self):
        return self.active_customer.order if self.active_customer else None

    @property
    def active_workpiece(self):
        return self.player.active_workpiece

    def start_day(self) -> None:
        if self.workday_started:
            return
        self.customer_queue = CustomerQueue(scripted_customers(self.current_day))
        self.player.active_workpiece = None
        self.workday_started = True

    def accept_next_order(self):
        if self.player.active_workpiece is not None:
            raise ValueError("Finish the active workpiece before accepting another order")
        customer = self.customer_queue.accept_next()
        self.player.active_workpiece = WeaponItem(customer.order.weapon_type)
        return customer

    def select_material(self, material: str) -> None:
        material = material.lower()
        if self.player.active_workpiece is None:
            raise ValueError("Accept an order before selecting material")
        if material not in ("iron", "steel"):
            raise ValueError("Unsupported material")
        if self.player.inventory.get(material, 0) <= 0:
            raise ValueError(f"No {material} remains in inventory")
        previous = self.player.active_workpiece.selected_material
        if previous == material:
            return
        self.player.active_workpiece.select_material(material)
        if previous:
            self.player.inventory[previous] += 1
        self.player.inventory[material] -= 1

    def update(self, delta_time: float) -> None:
        if self.workday_started:
            self.customer_queue.update(delta_time)

    def advance_day(self) -> None:
        if self.active_customer is not None or self.active_workpiece is not None:
            raise ValueError("Cannot advance while an order is active")
        self.current_day += 1
        self.player.progression["highest_day"] = max(self.player.progression["highest_day"], self.current_day)
        self.workday_started = False
        self.start_day()

    def deliver_active_order(self) -> dict:
        order = self.active_order
        workpiece = self.active_workpiece
        if order is None or workpiece is None:
            raise ValueError("No active order to deliver")
        if not workpiece.can_deliver:
            raise ValueError("Finish assembling the weapon before delivery")
        result = ScoreEngine().calculate(order, workpiece)
        workpiece.mark_delivered()
        customer = self.customer_queue.complete_active()
        customer.satisfaction = result.total
        customer.response = self._customer_response(result.total)
        self.player.gold += result.payout
        self.player.reputation += result.reputation_change
        record = result.to_dict() | {
            "day": self.current_day,
            "customer": customer.name,
            "weapon": workpiece.weapon_type,
            "response": customer.response,
        }
        self.score_history.append(record)
        self.last_result = record
        self.player.active_workpiece = None
        return record

    @staticmethod
    def _customer_response(score: float) -> str:
        if score >= 90:
            return "This is finer than I imagined. Thank you!"
        if score >= 75:
            return "Excellent work. This will serve me well."
        if score >= 60:
            return "A sturdy piece. I am satisfied."
        return "It is rough, but it will do."

    def day_records(self) -> list[dict]:
        return [record for record in self.score_history if record["day"] == self.current_day]
