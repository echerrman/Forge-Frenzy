"""Customer, order, and patience queue models."""

from dataclasses import dataclass, field
from enum import Enum


class CustomerCategory(str, Enum):
    VILLAGER = "villager"
    GUARD = "guard"
    MERCHANT = "merchant"
    ADVENTURER = "adventurer"


class OrderStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


@dataclass
class Order:
    order_id: str
    weapon_type: str
    material: str
    required_components: dict[str, str]
    initial_patience: float
    base_payment: int
    remaining_patience: float | None = None
    status: OrderStatus = OrderStatus.PENDING

    def __post_init__(self) -> None:
        self.material = self.material.lower()
        self.weapon_type = self.weapon_type.lower()
        if self.remaining_patience is None:
            self.remaining_patience = float(self.initial_patience)

    def update_patience(self, delta_time: float) -> None:
        if self.status != OrderStatus.ACTIVE or delta_time <= 0:
            return
        self.remaining_patience = max(0.0, self.remaining_patience - delta_time)
        if self.remaining_patience == 0:
            self.status = OrderStatus.EXPIRED

    def accuracy_for(self, workpiece) -> float:
        """Return simple material/type/component agreement as a percentage."""
        checks = [
            workpiece.weapon_type.lower() == self.weapon_type,
            workpiece.selected_material == self.material,
        ]
        checks.extend(workpiece.selected_components.get(key) == value for key, value in self.required_components.items())
        return 100.0 * sum(checks) / len(checks)


@dataclass
class Customer:
    customer_id: str
    name: str
    category: CustomerCategory
    order: Order
    satisfaction: float = 0.0
    response: str = "Waiting at the counter."

    @property
    def patience(self) -> float:
        return self.order.remaining_patience


@dataclass
class CustomerQueue:
    pending: list[Customer] = field(default_factory=list)
    active_customer: Customer | None = None
    completed: list[Customer] = field(default_factory=list)

    def add(self, customer: Customer) -> None:
        self.pending.append(customer)

    def accept_next(self) -> Customer:
        if self.active_customer is not None:
            raise ValueError("An order is already active")
        if not self.pending:
            raise ValueError("No customers are waiting")
        self.active_customer = self.pending.pop(0)
        self.active_customer.order.status = OrderStatus.ACTIVE
        self.active_customer.response = "Order accepted. I will be waiting."
        return self.active_customer

    def update(self, delta_time: float) -> None:
        if self.active_customer is not None:
            self.active_customer.order.update_patience(delta_time)

    def complete_active(self) -> Customer:
        if self.active_customer is None:
            raise ValueError("No active customer")
        customer = self.active_customer
        customer.order.status = OrderStatus.COMPLETED
        self.completed.append(customer)
        self.active_customer = None
        return customer


def scripted_customers(day: int) -> list[Customer]:
    """Deterministic introductory orders; later systems may replace this source."""
    if day <= 1:
        return [Customer(
            "day1-elin", "Elin", CustomerCategory.VILLAGER,
            Order("day1-dagger", "dagger", "iron", {"handle": "oak", "guard": "simple"}, 300.0, 45),
        )]
    return [
        Customer(
            f"day{day}-bren", "Bren", CustomerCategory.GUARD,
            Order(f"day{day}-sword", "sword", "steel", {"handle": "leather", "guard": "cross"}, 240.0, 90),
        ),
        Customer(
            f"day{day}-mara", "Mara", CustomerCategory.MERCHANT,
            Order(f"day{day}-dagger", "dagger", "iron", {"handle": "walnut", "guard": "curved"}, 210.0, 60),
        ),
    ]
