import pytest

from game.items import WeaponItem, WeaponStage


def test_weapon_enforces_stage_order_and_requires_material():
    weapon = WeaponItem("dagger")
    assert weapon.stage == WeaponStage.RAW
    assert weapon.next_station == "furnace"
    with pytest.raises(ValueError):
        weapon.complete_station("furnace", 80)
    with pytest.raises(ValueError):
        weapon.complete_station("anvil", 80)

    weapon.select_material("iron")
    weapon.complete_station("furnace", 105)
    assert weapon.stage == WeaponStage.HEATED
    assert weapon.station_scores["furnace"] == 100
    with pytest.raises(ValueError):
        weapon.complete_station("furnace", 50)


def test_weapon_cannot_deliver_before_assembly():
    weapon = WeaponItem("sword")
    with pytest.raises(ValueError):
        weapon.mark_delivered()
