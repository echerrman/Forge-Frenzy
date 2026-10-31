"""Shared station eligibility and placement behavior."""


class StationController:
    name = "station"

    def __init__(self, workpiece, order=None):
        self.workpiece = workpiece
        self.order = order
        self.feedback = ""

    @property
    def progress(self):
        return self.workpiece.station_progress.get(self.name, 0.0) if self.workpiece else 0.0

    @progress.setter
    def progress(self, value):
        self.workpiece.station_progress[self.name] = max(0.0, min(1.0, value))

    @property
    def completed(self):
        return bool(self.workpiece and self.name in self.workpiece.station_scores)

    def can_place(self):
        if self.workpiece is None:
            return False, "Accept an order and choose material first."
        if self.completed:
            return False, "This station is already complete."
        if self.workpiece.location != "hotbar":
            return False, "Return the workpiece to the hotbar first."
        if self.workpiece.next_station != self.name:
            expected = self.workpiece.next_station or "delivery"
            return False, f"Not ready. Next step: {expected.title()}."
        return True, ""

    def place(self):
        valid, message = self.can_place()
        if not valid:
            self.feedback = message
            return False
        self.workpiece.location = self.name
        self.feedback = "Workpiece moved into the station."
        return True

    def return_to_hotbar(self):
        if self.workpiece and self.workpiece.location == self.name:
            self.workpiece.location = "hotbar"
            self.feedback = "Workpiece returned to the hotbar."

    def complete(self):
        self.workpiece.complete_station(self.name, 100.0)
        self.feedback = f"{self.name.title()} complete!"
