import pytest

from game.scoring import ScoreEngine
from game.state import GameState
from game.stations.controllers import AnvilController, AssemblyController, FurnaceController, GrindController, MoldController, QuenchController


def completed_state():
    state = GameState()
    state.start_day()
    state.accept_next_order()
    state.select_material("iron")
    item, order = state.active_workpiece, state.active_order
    furnace = FurnaceController(item, order); furnace.place(); furnace.update(3); furnace.toggle()
    mold = MoldController(item, order); mold.select_mold("dagger"); mold.place(); mold.pour(3)
    anvil = AnvilController(item, order); anvil.place(); [anvil.hit(i) for i in range(5)]
    quench = QuenchController(item, order); quench.place(); quench.hold_in_water(3)
    grind = GrindController(item, order); grind.place(); [grind.crank() for _ in range(grind.required_cranks)]; grind.sharpen_sweep(grind.required_sweep_distance)
    assembly = AssemblyController(item, order); assembly.place(); assembly.drop_component("handle", "oak"); assembly.drop_component("guard", "simple")
    return state


def test_score_is_bounded_and_uses_configured_breakdown():
    state = completed_state()
    result = ScoreEngine().calculate(state.active_order, state.active_workpiece)
    assert 0 <= result.total <= 100
    assert result.accuracy == 100
    assert result.craftsmanship == 100
    assert result.payout <= state.active_order.base_payment


def test_delivery_pays_once_and_clears_active_order():
    state = completed_state()
    result = state.deliver_active_order()
    assert state.player.gold == result["payout"]
    assert state.active_order is None
    assert state.active_workpiece is None
    gold = state.player.gold
    with pytest.raises(ValueError):
        state.deliver_active_order()
    assert state.player.gold == gold


def test_invalid_scoring_weights_are_rejected():
    with pytest.raises(ValueError):
        ScoreEngine(0.5, 0.5, 0.5)
