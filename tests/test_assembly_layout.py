from game.customers import scripted_customers
from game.scenes.station_scene import ASSEMBLY_COMPONENT_CARDS


def test_assembly_component_locations_are_fixed_and_cover_scripted_orders():
    locations = {(kind, value): rect.topleft for kind, value, rect in ASSEMBLY_COMPONENT_CARDS}

    assert locations == {
        ("handle", "oak"): (95, 170),
        ("handle", "leather"): (95, 230),
        ("handle", "walnut"): (95, 290),
        ("guard", "simple"): (95, 380),
        ("guard", "cross"): (95, 440),
        ("guard", "curved"): (95, 500),
    }

    customers = scripted_customers(1) + scripted_customers(2)
    for customer in customers:
        for kind, value in customer.order.required_components.items():
            assert (kind, value) in locations
