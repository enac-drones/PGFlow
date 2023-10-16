import pytest
import numpy as np

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


# def test_induced_source_velocity2D(vehicle_at_origin,vehicle_at_coords_1_1_1, vehicle_at_coords_2_2_2):
#     from src.panel_flow import induced_source_velocity2D

#     # Test that induced velocity is in the opposite direction
#     v = induced_source_velocity2D(vehicle_at_origin, vehicle_at_coords_1_1_1)
#     assert v[0] < 0 and v[1] < 0

#     # Test that magnitude of induced velocity decreases with distance
#     vehicle3 = MockVehicle(np.array([2., 2.,2.]), 1.)
#     v_new = induced_source_velocity2D(vehicle_at_origin, vehicle_at_coords_2_2_2)
#     assert np.linalg.norm(v_new) < np.linalg.norm(v)

#     # BUG maybe this should be implemented, but realistically it will never happen
#     # although, never say never?

#     # Test that induced velocity is zero when the vehicles are at the same position
#     # vehicle4 = TestVehicle(np.array([0., 0.]), 1.)
#     # v_zero = induced_source_velocity2D(vehicle1, vehicle4)
#     # assert np.all(v_zero == np.array([0., 0.]))

# def test_induced_source_velocity3D():
#     from src.panel_flow import induced_source_velocity3D

#     vehicle1 = MockVehicle(np.array([0., 0., 0.]), 1.)
#     vehicle2 = MockVehicle(np.array([1., 1., 1.]), 1.)

#     # Test that induced velocity is in the opposite direction
#     v = induced_source_velocity3D(vehicle1, vehicle2)
#     assert v[0] < 0 and v[1] < 0 and v[2] < 0

#     # Test that magnitude of induced velocity decreases with distance
#     vehicle3 = MockVehicle(np.array([2., 2., 2.]), 1.)
#     v_new = induced_source_velocity3D(vehicle1, vehicle3)
#     assert np.linalg.norm(v_new) < np.linalg.norm(v)
