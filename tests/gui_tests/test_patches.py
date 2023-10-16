import pytest
from gui.patches import ObstaclePatch
from gui.entities import Obstacle
from unittest.mock import Mock



@pytest.fixture
def mock_obstacle():
    # Create a mock obstacle with a vertices method that returns dummy vertices
    obstacle = Mock()
    obstacle.vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
    return obstacle


def test_obstacle_patch_initialization(mock_obstacle):
    patch = ObstaclePatch(mock_obstacle, facecolor='blue', edgecolor='red')
    
    assert patch.original_facecolor == (0, 0, 1, 1)  # RGB+Alpha for blue
    assert patch.original_edgecolor == (1, 0, 0, 1)  # RGB+Alpha for red
    assert patch.building == mock_obstacle

def test_obstacle_patch_select_deselect(mock_obstacle):
    patch = ObstaclePatch(mock_obstacle)
    
    patch.select()
    assert patch.get_facecolor() == (1, 0.4, 1, 0.7)
    assert patch.get_edgecolor() == (0, 0, 0, 1)  # RGB+Alpha for black
    
    patch.deselect()
    assert patch.get_facecolor() == patch.original_facecolor
    assert patch.get_edgecolor() == patch.original_edgecolor

# More tests for the other methods and classes can be added similarly...
