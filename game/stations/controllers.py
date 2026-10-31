"""Persistent, penalty-free controllers for the initial sample workflow."""

from game.stations.base import StationController


class FurnaceController(StationController):
    name = "furnace"
    duration = 3.0

    def toggle(self):
        if not self.workpiece or self.workpiece.location == "hotbar":
            return self.place()
        if self.workpiece.location != self.name:
            self.feedback = "The workpiece is in another station."
            return False
        if self.progress >= 1.0:
            self.complete()
            self.workpiece.temperature = 900.0
            return True
        self.return_to_hotbar()
        return True

    def update(self, delta_time):
        if self.workpiece and self.workpiece.location == self.name and not self.completed:
            self.progress += delta_time / self.duration
            self.workpiece.temperature = 20.0 + 880.0 * self.progress
            self.feedback = "Ready — click the heated metal to return it." if self.progress >= 1 else "Heating..."


class MoldController(StationController):
    name = "mold"
    duration = 2.5

    def select_mold(self, mold):
        if not self.workpiece:
            self.feedback = "No active workpiece."
            return
        if mold != self.workpiece.weapon_type:
            self.feedback = f"Choose the {self.workpiece.weapon_type} mold for this order."
            return
        self.workpiece.selected_mold = mold
        self.feedback = f"{mold.title()} mold selected. Click the hotbar item next."

    def place(self):
        if not self.workpiece or self.workpiece.selected_mold != self.workpiece.weapon_type:
            self.feedback = "Select the matching mold first."
            return False
        return super().place()

    def pour(self, delta_time):
        if not self.workpiece or self.workpiece.location != self.name or self.completed:
            self.feedback = "Place the heated workpiece into the mold first."
            return
        self.progress += delta_time / self.duration
        self.feedback = "Keep holding to pour..."
        if self.progress >= 1.0:
            self.complete()


class AnvilController(StationController):
    name = "anvil"
    target_count = 5

    @property
    def hits(self):
        if not self.workpiece:
            return set()
        return set(self.workpiece.station_data.setdefault(self.name, {}).get("hits", []))

    def hit(self, index):
        if not self.workpiece or self.workpiece.location != self.name or self.completed:
            self.feedback = "Place the molded blade on the anvil first."
            return
        hits = self.hits
        hits.add(index)
        self.workpiece.station_data[self.name]["hits"] = sorted(hits)
        self.progress = len(hits) / self.target_count
        self.feedback = f"Hammer points: {len(hits)}/{self.target_count}"
        if len(hits) >= self.target_count:
            self.complete()


class QuenchController(StationController):
    name = "quench"
    duration = 2.5

    def hold_in_water(self, delta_time):
        if not self.workpiece or self.workpiece.location != self.name or self.completed:
            self.feedback = "Place the shaped blade at the quench station first."
            return
        self.progress += delta_time / self.duration
        self.feedback = "Hold the blade under water..."
        if self.progress >= 1.0:
            self.workpiece.temperature = 40.0
            self.complete()

    def release_early(self):
        if not self.completed and self.progress > 0:
            self.progress = 0.0
            self.feedback = "Blade lifted out — hold it underwater continuously."


class GrindController(StationController):
    name = "grindstone"
    target_count = 6

    @property
    def hits(self):
        if not self.workpiece:
            return set()
        return set(self.workpiece.station_data.setdefault(self.name, {}).get("hits", []))

    def sharpen(self, index):
        if not self.workpiece or self.workpiece.location != self.name or self.completed:
            self.feedback = "Place the quenched blade at the grindstone first."
            return
        hits = self.hits
        hits.add(index)
        self.workpiece.station_data[self.name]["hits"] = sorted(hits)
        self.progress = len(hits) / self.target_count
        self.feedback = f"Edge markers: {len(hits)}/{self.target_count}"
        if len(hits) >= self.target_count:
            self.complete()


class AssemblyController(StationController):
    name = "assembly"

    def drop_component(self, kind, value):
        if not self.workpiece or self.workpiece.location != self.name or self.completed:
            self.feedback = "Place the ground blade on the assembly bench first."
            return
        required = self.order.required_components.get(kind)
        if value != required:
            self.feedback = f"That does not fit this order. Use the {required} {kind}."
            return
        self.workpiece.selected_components[kind] = value
        self.feedback = f"{value.title()} {kind} attached."
        self.progress = len(self.workpiece.selected_components) / len(self.order.required_components)
        if all(self.workpiece.selected_components.get(key) == expected for key, expected in self.order.required_components.items()):
            self.complete()


CONTROLLERS = {
    "furnace": FurnaceController,
    "mold": MoldController,
    "anvil": AnvilController,
    "quench": QuenchController,
    "grindstone": GrindController,
    "assembly": AssemblyController,
}


def create_controller(name, workpiece, order=None):
    controller = CONTROLLERS.get(name)
    return controller(workpiece, order) if controller else None
