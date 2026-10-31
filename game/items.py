"""Persistent weapon workpieces and their production state machine."""

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class WeaponStage(str, Enum):
    RAW = "raw"
    HEATED = "heated"
    MOLDED = "molded"
    SHAPED = "shaped"
    QUENCHED = "quenched"
    GROUND = "ground"
    ASSEMBLED = "assembled"
    DELIVERED = "delivered"


STATION_TRANSITIONS = {
    "furnace": (WeaponStage.RAW, WeaponStage.HEATED),
    "mold": (WeaponStage.HEATED, WeaponStage.MOLDED),
    "anvil": (WeaponStage.MOLDED, WeaponStage.SHAPED),
    "quench": (WeaponStage.SHAPED, WeaponStage.QUENCHED),
    "grindstone": (WeaponStage.QUENCHED, WeaponStage.GROUND),
    "assembly": (WeaponStage.GROUND, WeaponStage.ASSEMBLED),
}


@dataclass
class WeaponItem:
    """One workpiece that survives every scene transition."""

    weapon_type: str
    item_id: str = field(default_factory=lambda: uuid4().hex)
    selected_material: str | None = None
    stage: WeaponStage = WeaponStage.RAW
    temperature: float = 20.0
    station_scores: dict[str, float] = field(default_factory=dict)
    selected_components: dict[str, str] = field(default_factory=dict)
    selected_mold: str | None = None
    final_status: str = "in_progress"
    location: str = "hotbar"
    station_progress: dict[str, float] = field(default_factory=dict)
    station_data: dict[str, dict] = field(default_factory=dict)

    @property
    def next_station(self) -> str | None:
        for station, (required, _) in STATION_TRANSITIONS.items():
            if self.stage == required:
                return station
        return None

    @property
    def can_deliver(self) -> bool:
        return self.stage == WeaponStage.ASSEMBLED

    def select_material(self, material: str) -> None:
        if self.stage != WeaponStage.RAW:
            raise ValueError("Material cannot be changed after crafting begins")
        self.selected_material = material.lower()

    def complete_station(self, station: str, quality: float) -> None:
        """Advance exactly once when the requested station is eligible."""
        if station not in STATION_TRANSITIONS:
            raise ValueError(f"Unknown station: {station}")
        if station in self.station_scores:
            raise ValueError(f"{station} has already been completed")
        required, result = STATION_TRANSITIONS[station]
        if self.stage != required:
            raise ValueError(f"{station} requires stage {required.value}")
        if station == "furnace" and self.selected_material is None:
            raise ValueError("Select a material before heating")
        self.station_scores[station] = max(0.0, min(100.0, float(quality)))
        self.stage = result
        self.location = "hotbar"
        self.station_progress[station] = 1.0

    def mark_delivered(self) -> None:
        if not self.can_deliver:
            raise ValueError("Weapon must be assembled before delivery")
        self.stage = WeaponStage.DELIVERED
        self.final_status = "delivered"
