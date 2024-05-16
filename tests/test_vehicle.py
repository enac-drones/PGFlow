import pytest
from pgflow.vehicle import Vehicle
import numpy as np


@pytest.fixture
def mock_vehicle():
    return Vehicle()


def test_vehicle_initialization(mock_vehicle: Vehicle):
    assert mock_vehicle.ID.startswith("V")
    assert np.array_equal(mock_vehicle._position, np.zeros(3))
    # Add more assertions for other default attributes


def test_basic_properties(mock_vehicle: Vehicle):
    expected_properties = {
        "ID": mock_vehicle.ID,
        "position": mock_vehicle.position,
        "goal": mock_vehicle.goal,
        "source_strength": mock_vehicle.source_strength,
        "sink_strength": mock_vehicle.sink_strength,
    }
    assert mock_vehicle.basic_properties() == expected_properties


def test_vehicle_position_property(mock_vehicle: Vehicle):
    new_position = np.array([1, 2, 3])
    mock_vehicle.position = new_position
    assert np.array_equal(mock_vehicle.position, new_position)
    vector_to_goal = (mock_vehicle.goal - mock_vehicle.position)[:2]
    vector_to_goal /= np.linalg.norm(vector_to_goal)
    print(mock_vehicle.v_free_stream)
    assert np.array_equal(
        mock_vehicle.v_free_stream, vector_to_goal * 0.5
    )  # Based on the setter logic


def test_set_position(mock_vehicle: Vehicle):
    new_position = np.array([1, 2, 3])
    mock_vehicle.set_initial_position(new_position)
    assert np.array_equal(mock_vehicle.position, new_position)
    assert mock_vehicle.path.shape == (1, 3)  # Check if path is updated correctly
    # More checks can be added depending on the method's functionality


def test_set_goal(mock_vehicle: Vehicle):
    new_goal = np.array([10, 10, 3])
    goal_strength = 5
    mock_vehicle.Set_Goal(new_goal, goal_strength)
    assert np.array_equal(mock_vehicle.goal, new_goal)
    assert mock_vehicle.sink_strength == goal_strength


def test_update_position_pid(mock_vehicle: Vehicle):
    print(mock_vehicle.position)
    mock_flow_vel = np.array([0.1, 0.1])
    mock_vehicle.update_position_pid(mock_flow_vel)
    # Assertions will depend on the expected behavior of update_position_pid
    # For example, you might check if the position has been updated correctly


def test_arrived(mock_vehicle: Vehicle):
    mock_vehicle.set_initial_position([0, 0, 0])
    mock_vehicle.Set_Goal([0, 0.1, 0], 0)  # Set a nearby goal
    assert mock_vehicle.arrived(mock_vehicle.ARRIVAL_DISTANCE)
    mock_vehicle.Set_Goal([10, 10, 0], 0)  # Set a faraway goal
    assert not mock_vehicle.arrived(mock_vehicle.ARRIVAL_DISTANCE)
