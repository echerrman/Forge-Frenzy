import pytest

from game.customers import CustomerCategory, CustomerQueue, OrderStatus, scripted_customers
from game.items import WeaponItem


def test_scripted_orders_have_required_day_variation():
    first = scripted_customers(1)
    assert len(first) == 1
    assert first[0].category == CustomerCategory.VILLAGER
    assert first[0].order.weapon_type == "dagger"
    assert first[0].order.material == "iron"

    second = scripted_customers(2)
    assert len(second) >= 2
    assert second[0].order.weapon_type == "sword"
    assert second[0].order.material == "steel"


def test_queue_accepts_once_and_updates_only_active_patience():
    customers = scripted_customers(2)
    queue = CustomerQueue(customers.copy())
    starting = queue.pending[0].patience
    queue.update(5.0)
    assert queue.pending[0].patience == starting

    active = queue.accept_next()
    assert active.order.status == OrderStatus.ACTIVE
    queue.update(5.0)
    assert active.patience == starting - 5.0
    with pytest.raises(ValueError):
        queue.accept_next()


def test_order_accuracy_checks_material_type_and_components():
    order = scripted_customers(1)[0].order
    weapon = WeaponItem("dagger", selected_material="iron")
    weapon.selected_components = {"handle": "oak", "guard": "simple"}
    assert order.accuracy_for(weapon) == 100
    weapon.selected_material = "steel"
    assert order.accuracy_for(weapon) == 75
