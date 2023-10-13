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
    
    def update_arrow_position(self, new_start:tuple, new_end:tuple):
        new_x_start, new_y_start = new_start
        new_x_end, new_y_end = new_end

        dx = new_x_end - new_x_start
        dy = new_y_end - new_y_start
        
        self.arrow.set_data(x=new_x_start, y=new_y_start, dx=dx, dy=dy)


class Marker:
    '''Create an icon or marker patch to plot'''
    def __init__(self, position:ArrayLike, style:str) -> None:
        self.position = np.array(position)
        self.style = style
        self.marker:Line2D = None

    def create_marker(self)->Line2D:
        self.marker = plt.plot(*self.position, self.style)[0]
        return self.marker
    
    def update_position(self, new_position:tuple):
        self.position = new_position
        self.marker.set_xdata([self.position[0]])
        self.marker.set_ydata([self.position[1]])

class DronePath:
    '''Graphical representation of the Drone including start and end markers and an arrow connecting the two'''
    def __init__(self, drone:Drone, ax:plt.Axes) -> None:
        self.drone = drone
        self.marker_start:Marker = None
        self.marker_end:Marker = None
        
        self.arrow:Arrow = None
        self.ax = ax

    def create_patches(self)->tuple:
        # plot the arrow 
        self.marker_start = Marker(self.drone.position[:2], 'b*') # Initial position in blue
        
        self.marker_end = Marker(self.drone.goal[:2], 'r*')  # Goal position in red
                
        # Add an arrow with a line using the 'arrow' function
        self.arrow = Arrow(self.drone.position[:2],self.drone.goal[:2], self.ax)

        # self.patches = (self.marker_start, self.marker_end, self.arrow)
        return (self.marker_start.create_marker(), self.marker_end.create_marker(), self.arrow.create_arrow())
    
    def patches(self):
        return self.marker_start.marker, self.marker_end.marker, self.arrow.arrow
    
    def update(self):
        self.marker_start.update_position(self.drone.position[:2])
        self.marker_end.update_position(self.drone.goal[:2])
        self.arrow.update_arrow_position(self.drone.position[:2],self.drone.goal[:2])
    

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