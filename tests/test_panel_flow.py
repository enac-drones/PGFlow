import pytest
import numpy as np
from pgflow.panel_flow import PanelFlow
from pgflow.building import Building
from pgflow.vehicle import Vehicle, PersonalVehicle

# code shows two different ways to test, with and without pytest fixtures
# tests are deprected as the functions have been vectorised for performance


class MockVehicle:
    """initialising a barebones version of the vehicle class"""

    def __init__(self, position, source_strength):
        self.position = position
        self.source_strength = source_strength


@pytest.fixture
def vehicle_at_origin():
    return MockVehicle(np.array([0.0, 0.0, 0.0]), 1.0)


@pytest.fixture
def vehicle_at_coords_1_1_1():
    return MockVehicle(np.array([1.0, 1.0, 1.0]), 1.0)


@pytest.fixture
def vehicle_at_coords_2_2_2():
    return MockVehicle(np.array([2.0, 2.0, 2.0]), 1.0)


from unittest.mock import MagicMock


def test_calculate_unknown_vortex_strengths():
    vehicle = Vehicle()
    buildings = [
        Building([[i, 0, 1], [i + 1, 0, 1], [0.5 + i, 0.5, 1]]) for i in range(2)
    ]
    for b in buildings:
        b.panelize(size=0.01)
        b.calculate_coef_matrix()
    vehicle.relevant_obstacles = buildings

    vehicle.personal_vehicle_dict = {
        vehicle.ID: PersonalVehicle(**vehicle.basic_properties())
    }
    panel_flow = PanelFlow(vehicle)

    panel_flow.calculate_unknown_vortex_strengths(vehicle)

    # Add assertions to check if the method behaves as expected
    # For example, check if the gamma_calc method was called for each relevant building
