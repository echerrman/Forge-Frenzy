"""Configurable order scoring and reward calculations."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ScoreResult:
    accuracy: float
    craftsmanship: float
    speed: float
    total: float
    rating: str
    payout: int
    reputation_change: int

    def to_dict(self) -> dict:
        return asdict(self)


class ScoreEngine:
    def __init__(self, accuracy_weight=0.4, craftsmanship_weight=0.4, speed_weight=0.2):
        if abs(accuracy_weight + craftsmanship_weight + speed_weight - 1.0) > 1e-9:
            raise ValueError("Scoring weights must total 1.0")
        self.accuracy_weight = accuracy_weight
        self.craftsmanship_weight = craftsmanship_weight
        self.speed_weight = speed_weight

    def calculate(self, order, workpiece) -> ScoreResult:
        accuracy = self._clamp(order.accuracy_for(workpiece))
        scores = list(workpiece.station_scores.values())
        craftsmanship = self._clamp(sum(scores) / len(scores) if scores else 0.0)
        speed = self._clamp(100.0 * order.remaining_patience / order.initial_patience) if order.initial_patience else 0.0
        total = self._clamp(
            accuracy * self.accuracy_weight
            + craftsmanship * self.craftsmanship_weight
            + speed * self.speed_weight
        )
        if total >= 90:
            rating, reputation = "Masterwork", 5
        elif total >= 75:
            rating, reputation = "Excellent", 3
        elif total >= 60:
            rating, reputation = "Good", 2
        else:
            rating, reputation = "Rough", 1
        payout = max(1, round(order.base_payment * total / 100.0))
        return ScoreResult(accuracy, craftsmanship, speed, total, rating, payout, reputation)

    @staticmethod
    def _clamp(value):
        return max(0.0, min(100.0, float(value)))
