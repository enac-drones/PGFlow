import numpy as np
from gui.utils import distance_between_points


def test_distance_between_points():
    # Test with integers
    p1, p2 = [0, 0], [3, 4]
    assert distance_between_points(p1, p2) == 5.0

    # Test with floats
    p1, p2 = [0.0, 0.0], [0.0, 5.0]
    assert distance_between_points(p1, p2) == 5.0

    # Test with numpy arrays
    p1, p2 = np.array([0, 0]), np.array([3, 4])
    assert distance_between_points(p1, p2) == 5.0

    # Test with zero distance
    p1, p2 = [2.3, 4.5], [2.3, 4.5]
    assert distance_between_points(p1, p2) == 0.0

    # Additional tests can be added based on edge cases or other requirements
