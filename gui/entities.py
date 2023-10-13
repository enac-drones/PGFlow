from gui.mixins import ClickableMixin
from matplotlib.patches import Polygon
from numpy.typing import ArrayLike
from typing import List
import numpy as np

class Entity:
    """Class containing all necessary information about an Entity, such as ID and position"""
    def __init__(self, ID, position = None):
        self.ID = ID
        self.position = np.array(position)

    def move(self, new_position):
        self.position = new_position    

    def distance_to_point(self, point):
        p = np.array(point)
        return np.linalg.norm(self.position - p)




class Drone(Entity, ClickableMixin):
    '''Class containing all necessary information about a Drone Entity, not including its graphics'''
    def __init__(self, ID, position, goal):
        super().__init__(ID, position)
        self.goal = goal

    def is_near_goal(self, point, threshold=0.2):
        return np.linalg.norm(np.array(point) - self.goal[:2]) < threshold

    def move_end(self, new_position):
        self.goal = new_position


    def move_whole_drone(self, delta):
        self.position[:2] += delta
        self.goal[:2] += delta
    
    def click_near_arrow(self, p0, p1, event, threshold=0.2):
        click_position = np.array([event.xdata, event.ydata])
        p0 = np.array(p0)
        p1 = np.array(p1)
        dist_start = np.linalg.norm(click_position - p0)
        dist_end = np.linalg.norm(click_position - p1)
        arrow_length = np.linalg.norm(p1-p0)
        
        # Using Heron's formula to compute area of triangle formed by start, end, and click points
        s = (dist_start + dist_end + arrow_length) / 2
        triangle_area = np.sqrt(s * (s - dist_start) * (s - dist_end) * (s - arrow_length))
        
        # Distance from click to the line segment
        distance_to_line = 2 * triangle_area / arrow_length

        # Calculate projection of click point onto the arrow line segment
        dot_product = np.dot(p1 - p0, click_position - p0) / arrow_length**2
        projected_point = p0 + dot_product * (p1 - p0)

        # Check if the projected point lies between start and end
        is_within_segment = np.all(np.minimum(p0, p1) <= projected_point) and np.all(projected_point <= np.maximum(p0, p1))
        
        if distance_to_line < threshold and is_within_segment:
            return True

        return False
    


