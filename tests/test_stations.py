from game.state import GameState
from game.stations.controllers import (
    AnvilController,
    AssemblyController,
    FurnaceController,
    GrindController,
    MoldController,
    QuenchController,
)


def prepared_state():
    state = GameState()
    state.start_day()
    state.accept_next_order()
    state.select_material("iron")
    return state


def test_complete_initial_dagger_through_all_station_controllers():
    state = prepared_state()
    item, order = state.active_workpiece, state.active_order

    furnace = FurnaceController(item, order)
    assert furnace.toggle()
    furnace.update(3.0)
    furnace.toggle()

    mold = MoldController(item, order)
    mold.select_mold("dagger")
    assert mold.place()
    mold.pour(3.0)

    anvil = AnvilController(item, order)
    assert anvil.place()
    for index in range(anvil.target_count):
        anvil.hit(index)

    quench = QuenchController(item, order)
    assert quench.place()
    quench.hold_in_water(3.0)

    grind = GrindController(item, order)
    assert grind.place()
    for _ in range(grind.required_cranks):
        grind.crank()
    grind.sharpen_sweep(grind.required_sweep_distance)

    assembly = AssemblyController(item, order)
    assert assembly.place()
    assembly.drop_component("handle", "oak")
    assembly.drop_component("guard", "simple")

    assert item.can_deliver
    assert set(item.station_scores) == {"furnace", "mold", "anvil", "quench", "grindstone", "assembly"}
    assert all(score == 100 for score in item.station_scores.values())


def test_quench_requires_one_continuous_hold():
    state = prepared_state()
    item = state.active_workpiece
    item.complete_station("furnace", 100)
    item.complete_station("mold", 100)
    item.complete_station("anvil", 100)
    quench = QuenchController(item, state.active_order)
    quench.place()
    quench.hold_in_water(1.0)
    assert quench.progress > 0
    quench.release_early()
    assert quench.progress == 0


def test_grindstone_spin_resets_on_reentry_but_sharpening_persists():
    state = prepared_state()
    item = state.active_workpiece
    for station in ("furnace", "mold", "anvil", "quench"):
        item.complete_station(station, 100)
    grind = GrindController(item, state.active_order)
    grind.place()
    for _ in range(grind.required_cranks):
        grind.crank()
    grind.sharpen_sweep(300)
    saved_progress = grind.progress

    returned = GrindController(item, state.active_order)
    assert not returned.spinning
    assert returned.progress == saved_progress
