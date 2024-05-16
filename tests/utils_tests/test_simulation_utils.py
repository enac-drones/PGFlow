import pytest
from pgflow.vehicle import Vehicle, PersonalVehicle
from pgflow.cases import Case, Cases
from pgflow.utils import simulation_utils as su
from pgflow.arena import ArenaMap
import numpy as np


# Sample Fixtures
@pytest.fixture
def sample_vehicle():
    # Add your initialization parameters if any
    test_vehicle = Vehicle()
    test_vehicle.goal = np.array([1, 1, 0])
    return test_vehicle


@pytest.fixture
def sample_case():
    case = Cases.get_case(file_name="cases.json", case_name="default")
    return case


# Actual Tests
def test_set_new_attribute(sample_case):
    su.set_new_attribute(sample_case, "new_attr", 10)
    assert not hasattr(sample_case.vehicle_list[0], "new_attr")

    su.set_new_attribute(sample_case, "sink_strength", 5)
    assert sample_case.vehicle_list[0].sink_strength == 5


# ... [other tests for valid_vehicle_list, step_simulation, etc.]


def test_run_simulation(sample_case):
    result = su.run_simulation(sample_case, t=2)
    # Adjust the expected outcome based on your specific logic
    assert result
