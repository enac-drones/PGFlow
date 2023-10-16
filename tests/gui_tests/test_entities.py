from gui.entities import Entity, Drone, Obstacle
import numpy as np

# test Entity
def test_entity_initialization():
    e = Entity(1, [1, 2])
    assert e.ID == 1
    assert np.array_equal(e.position, np.array([1, 2]))


def test_entity_move():
    e = Entity(1, [1, 2])
    e.move([3, 4])
    assert np.array_equal(e.position, np.array([3, 4]))


def test_entity_distance_to_point():
    e = Entity(1, [0, 0])
    distance = e.distance_to_point([3, 4])
    assert distance == 5  # By Pythagoras theorem


# test Drone


def test_drone_initialization():
    d = Drone(1, [1, 2], [3, 4])
    assert d.ID == 1
    assert np.array_equal(d.position, [1, 2])
    assert np.array_equal(d.goal, [3, 4])


def test_drone_move_end():
    d = Drone(1, [1, 2], [3, 4])
    d.move_end([5, 6])
    assert np.array_equal(d.goal, [5, 6])


def test_drone_move_whole_drone():
    d = Drone(1, [1, 2], [3, 4])
    d.move_whole_drone(np.array([1, 1]))
    assert np.array_equal(d.position, [2, 3])
    assert np.array_equal(d.goal, [4, 5])


def test_drone_is_near_goal():
    d = Drone(1, [1, 2], [3, 4])
    assert d.is_near_goal([3.1, 4.1])
    assert not d.is_near_goal([4, 5])


# test Obstacle


def test_obstacle_initialization():
    o = Obstacle([(0, 0), (1, 0), (1, 1)])
    assert np.array_equal(o.vertices, [(0, 0), (1, 0), (1, 1)])


def test_obstacle_move_vertex():
    o = Obstacle([(0, 0), (1, 0), (1, 1)])
    o.move_vertex(1, (2, 2))
    assert np.array_equal(o.vertices[1], [2, 2])


def test_obstacle_move_building():
    o = Obstacle([np.array([0, 0]), np.array([1, 0]), np.array([1, 1])])
    o.move_building(np.array([1, 1]))
    assert np.array_equal(o.vertices[0], np.array([1, 1]))
    assert np.array_equal(o.vertices[1], np.array([2, 1]))
    assert np.array_equal(o.vertices[2], np.array([2, 2]))
