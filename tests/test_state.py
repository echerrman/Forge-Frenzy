import pytest

from game.state import GameState


def test_accept_order_and_select_material_create_one_persistent_workpiece():
    state = GameState()
    state.start_day()
    customer = state.accept_next_order()
    workpiece = state.active_workpiece
    assert workpiece.weapon_type == customer.order.weapon_type

    before = state.player.inventory["iron"]
    state.select_material("iron")
    assert state.active_workpiece is workpiece
    assert workpiece.selected_material == "iron"
    assert state.player.inventory["iron"] == before - 1
    with pytest.raises(ValueError):
        state.accept_next_order()


def test_changing_material_returns_previous_inventory_item():
    state = GameState()
    state.start_day()
    state.accept_next_order()
    iron_before = state.player.inventory["iron"]
    steel_before = state.player.inventory["steel"]
    state.select_material("iron")
    state.select_material("steel")
    assert state.player.inventory["iron"] == iron_before
    assert state.player.inventory["steel"] == steel_before - 1


def test_failed_late_material_change_does_not_corrupt_inventory():
    state = GameState()
    state.start_day()
    state.accept_next_order()
    state.select_material("iron")
    state.active_workpiece.complete_station("furnace", 80)
    inventory_before = state.player.inventory.copy()
    with pytest.raises(ValueError):
        state.select_material("steel")
    assert state.player.inventory == inventory_before


def test_day_progression_loads_second_script():
    state = GameState()
    state.start_day()
    state.advance_day()
    assert state.current_day == 2
    assert len(state.customer_queue.pending) >= 2
    assert state.customer_queue.pending[0].order.weapon_type == "sword"
