import pytest
from pgflow.building import PersonalBuilding, Building
import numpy as np


def test_personal_building_creation():
    test_id = "TestID"
    test_vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])

    pb = PersonalBuilding(ID=test_id, vertices=test_vertices)

    assert pb.ID == test_id
    assert np.array_equal(pb.vertices, test_vertices)


def normalize_polygon_vertices(vertices):
    """
    Normalize the order of the vertices of a polygon.
    This function finds the vertex with the smallest x-coordinate (and smallest y-coordinate in case of a tie)
    and reorders the vertices starting from that vertex.
    """
    # Find the index of the vertex with the smallest x-coordinate (and smallest y-coordinate in case of a tie)
    min_index = np.argmin(vertices, axis=0)
    start_index = (
        min_index[0]
        if vertices[min_index[0], 1] <= vertices[min_index[1], 1]
        else min_index[1]
    )

    # Reorder the vertices starting from the vertex with the smallest x (and y) coordinate
    return np.roll(vertices, -start_index, axis=0)


@pytest.fixture
def mock_building():
    vertices = np.array([[0, 0, 0], [2, 0, 0], [2, 2, 0], [0, 2, 0]])
    return Building(vertices)


def test_building_initialization(mock_building):
    expected_vertices = np.array([[0, 0, 0], [2, 0, 0], [2, 2, 0], [0, 2, 0]])
    normalized_expected = normalize_polygon_vertices(expected_vertices)
    normalized_actual = normalize_polygon_vertices(mock_building.vertices)

    assert np.array_equal(normalized_actual, normalized_expected)
    assert mock_building.ID.startswith("B")
    assert mock_building.panels.size == 0
    assert mock_building.nop is None
    assert mock_building.K is None
    assert mock_building.K_inv is None
    assert mock_building.gammas == {}


def test_building_inflate(mock_building):
    original_vertices = np.copy(mock_building.vertices)
    mock_building.inflate(safetyfac=1.1, rad=1e-4)

    assert not np.array_equal(mock_building.vertices, original_vertices)


def test_get_bounding_box(mock_building):
    bbox = mock_building.get_bounding_box()
    assert bbox.bounds == (0, 0, 2, 2)


def test_panelize(mock_building):
    panel_size = 1.0
    mock_building.panelize(size=panel_size)

    assert mock_building.panels.shape[0] > 0


def test_contains_point(mock_building):
    inside_point = (1, 1)
    outside_point = (3, 3)

    assert mock_building.contains_point(inside_point)
    assert not mock_building.contains_point(outside_point)
