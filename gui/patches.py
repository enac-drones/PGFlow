from numpy.typing import ArrayLike

import numpy as np
from matplotlib.patches import FancyArrow, Polygon
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt

from gui.mixins import ClickableMixin
from gui.entities import Drone

class Arrow:
    '''Class to create a FancyArrow object'''
    def __init__(self, start:ArrayLike, end:ArrayLike, ax:plt.Axes) -> None:
        self.start = np.array(start)
        self.end = np.array(end)
        self.arrow = None
        self.ax = ax
    
    def create_arrow(self)->FancyArrow:
        ds = self.end - self.start
        self.arrow = self.ax.arrow(
            *self.start, ds[0], ds[1], length_includes_head = True, head_width=0.2, head_length=0.2, fc='k', ec='k',linestyle = '-')
        return self.arrow
    
class Marker:
    '''Create an icon or marker patch to plot'''
    def __init__(self, position:ArrayLike, style:str) -> None:
        self.position = np.array(position)
        self.style = style
        self.marker:Line2D = None

    def create_marker(self)->Line2D:
        self.marker = plt.plot(*self.position, self.style)[0]
        return self.marker

class DronePath:
    '''Graphical representation of the Drone including start and end markers and an arrow connecting the two'''
    def __init__(self, drone:Drone, ax:plt.Axes) -> None:
        self.drone = drone
        self.patches = None
        self.marker_start = None
        self.marker_end = None
        self.arrow = None
        self.ax = ax

    def create_patches(self)->tuple:
        # plot the arrow 
        marker_start_obj = Marker(self.drone.position[:2], 'b*')
        self.marker_start = marker_start_obj.create_marker() # Initial position in blue
        
        marker_end_obj = Marker(self.drone.goal[:2], 'r*')
        self.marker_end = marker_end_obj.create_marker()  # Goal position in red
        
        # Add an arrow with a line using the 'arrow' function
        arrow_obj = Arrow(self.drone.position[:2],self.drone.goal[:2], self.ax)
        self.arrow = arrow_obj.create_arrow()

        self.patches = (self.marker_start, self.marker_end, self.arrow)
        return self.patches
    

class ObstaclePatch(Polygon, ClickableMixin):
    # ... other methods ...
    def __init__(self, xy: ArrayLike, *, closed: bool = ..., **kwargs) -> None:
        super().__init__(xy, closed=closed, **kwargs)
        self.vertices = self.get_xy()

    def closest_vertex(self, point):
        """Find the closest vertex to a given point."""
        closest_vertex_index, closest_vertex = min(
            enumerate(self.vertices),
            key=lambda x: np.linalg.norm(np.array(point) - x[1][:2])
        )
        return closest_vertex_index, closest_vertex

    def is_vertex_close(self, vertex, point, threshold=0.2):
        """Check if a vertex is close to a given point."""
        return np.linalg.norm(np.array(point) - vertex[:2]) < threshold

    def move_vertex(self, vertex_index, new_position):
        last_vertex_index = len(self.vertices) - 1
        if vertex_index == 0 or vertex_index == last_vertex_index:
            self.vertices[0] = new_position
            self.vertices[-1] = new_position
        else:
            self.vertices[vertex_index] = new_position

    def move_building(self, delta):
        for vertex in self.vertices:
            vertex += delta