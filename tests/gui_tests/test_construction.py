import pytest
from gui.construction import BuildingCreator
from gui.entities import Obstacle
from gui.patches import ObstaclePatch
import matplotlib.pyplot as plt

def test_create_building_returns_obstacle_patch():
    ax = plt.subplot()
    building_creator = BuildingCreator(ax)
    
    obstacle = Obstacle([(0, 0), (1, 0), (1, 1)])
    patch = building_creator.create_building(obstacle)
    
    assert isinstance(patch, ObstaclePatch), "The returned object is not an instance of ObstaclePatch"

def test_create_building_sets_expected_properties():
    ax = plt.subplot()
    building_creator = BuildingCreator(ax)
    
    obstacle = Obstacle([(0, 0), (1, 0), (1, 1)])
    patch = building_creator.create_building(obstacle)
    
    assert patch.get_edgecolor() == (0, 0, 0, 1)
    assert patch.get_facecolor() == (0, 0, 1, 0.5)
    assert patch.get_linewidth() == 2.0
    # Add checks for other properties as necessary
