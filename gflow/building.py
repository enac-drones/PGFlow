import math

import numpy as np
from numpy.typing import ArrayLike
import pyclipper
import time
from typing import List
from matplotlib.patches import Polygon as Pm
from shapely.geometry import box, Point
from shapely.geometry import Polygon as Ps
from shapely.ops import nearest_points
# from numpy import linalg

"""##Building Code"""

from dataclasses import dataclass, field

@dataclass(slots=True)
class PersonalBuilding:
    """Vehicle with the minimal required information: position, velocity, altitude, state etc"""
    ID:str
    vertices:ArrayLike

#TODO
class RelevantObstacles(dict):
    '''class to inherit from dict but also have additional methods
    such as easily checking if a point lies within any of the buildings
    etc'''
    pass

class Building:
    _id_counter = 0

    def __init__(self, vertices):  
        # Buildings(obstacles) are defined by coordinates of their vertices.
        self._vertices = np.array(vertices)
        self.mplPoly = self.create_mpl_polygon()
        self.shapelyPoly = self.create_shapely_polygon()
        #automatically increment the id
        self.ID = f"B{Building._id_counter}"
        Building._id_counter += 1
        # self.inflate(rad=0.0)
        # self.position = np.array(position)
        self.panels = np.array([])
        self.nop = None  # Number of Panels
        self.K = None  # Coefficient Matrix
        self.K_inv = None
        self.gammas = {}  # Vortex Strenghts
        # self.solution = np.array([])

    @property
    def vertices(self):
        """The getter method returns the value of _vertices."""
        return self._vertices
    
    @vertices.setter
    def vertices(self, new_verts):
        """The setter method updates _vertices and recalculates the polygons."""
        self._vertices = new_verts
        self.mplPoly = self.create_mpl_polygon()
        self.shapelyPoly = self.create_shapely_polygon()


    def inflate(self, safetyfac=1.1, rad=1e-4):
        rad = rad * safetyfac
        scale = 1e6
        pco = pyclipper.PyclipperOffset()
        pco.AddPath(
            (self.vertices[:, :2] * scale).astype(int).tolist(),
            pyclipper.JT_MITER,
            pyclipper.ET_CLOSEDPOLYGON,
        )

        inflated = np.array(pco.Execute(rad * scale)[0]) / scale
        height = self.vertices[0, 2]
        points = np.hstack((inflated, np.ones((inflated.shape[0], 1)) * height))
        # Xavg = np.mean(points[:, 0:1])
        # Yavg = np.mean(points[:, 1:2])
        # angles = np.arctan2(
        #     (Yavg * np.ones(len(points[:, 1])) - points[:, 1]),
        #     (Xavg * np.ones(len(points[:, 0])) - points[:, 0]),
        # )
        # sorted_angles = sorted(zip(angles, points), reverse=True)
        # points_sorted = np.vstack([x for y, x in sorted_angles])
        # self.vertices = points_sorted  
        self.vertices = points


    def get_bounding_box(self):
        min_x, min_y = np.min(self.vertices[:,:2], axis=0)
        max_x, max_y = np.max(self.vertices[:,:2], axis=0)
        return box(min_x, min_y, max_x, max_y)

    def create_mpl_polygon(self):
        return Pm(self.vertices[:, :2])
    
    def create_shapely_polygon(self):
        return Ps(self.vertices[:, :2])
    
    def panelize(self, size):
        # t = time.perf_counter()

        # Divides obstacle edges into smaller line segments, called panels.
        for index, vertex in enumerate(self.vertices):
            xyz1 = self.vertices[index]  # Coordinates of the first vertex
            xyz2 = self.vertices[
                (index + 1) % self.vertices.shape[0]
            ]  # Coordinates of the next vertex
            s = (
                (xyz1[0] - xyz2[0]) ** 2 + (xyz1[1] - xyz2[1]) ** 2
            ) ** 0.5  # Edge Length
            n = math.ceil(
                s / size
            )  # Number of panels given desired panel size, rounded up

            if n == 1:
                self.panels = np.vstack((self.panels, np.linspace(xyz1, xyz2, n)[1:]))
                # raise ValueError('Size too large. Please give a smaller size value.')
            if self.panels.size == 0:
                self.panels = np.linspace(xyz1, xyz2, n)[1:]
            else:
                # Divide the edge into "n" equal segments:
                self.panels = np.vstack((self.panels, np.linspace(xyz1, xyz2, n)[1:]))
        # print("time taken to panelize: ", time.perf_counter()-t)

    def contains_point(self, point:ArrayLike)->bool:
        '''Checks if a point lies within the building.
        Faster with matplotlib than shapely'''
        return self.mplPoly.contains_point(point, radius=0)
    
    def nearest_point_on_perimeter(self, point:ArrayLike)->ArrayLike:
        # Define the point you're checking
        ps = Point(point)
        # Use nearest_points to find the closest point on the polygon's perimeter to the given point
        closest_point, _ = nearest_points(self.shapelyPoly.boundary, ps)
        return np.array([closest_point.x, closest_point.y])


    def calculate_coef_matrix(self):
        '''Calculate the Matrix inverse of the building'''
        t = time.perf_counter()
        # Calculates coefficient matrix.
        self.nop = self.panels.shape[0]  # Number of Panels
        XYZ2 = self.panels  # Coordinates of end point of panel
        XYZ1 = np.roll(self.panels, 1, axis=0)  # Coordinates of the next end point of panel
        
        diff = XYZ1 - XYZ2
        
        # Controlpoints point at 3/4 of panel. #self.pcp  = 0.5*( XYZ1 + XYZ2 )[:,:2]
        self.pcp = XYZ2 + diff * 0.75
        # Vortex point at 1/4 of panel.
        self.vp = XYZ2 + diff * 0.25
        
        self.pb = np.arctan2(diff[:, 1], diff[:, 0]) + np.pi / 2

        # Calculate K matrix
        pcp_diff = self.pcp[:, np.newaxis, :] - self.vp[np.newaxis, :, :]
        pcp_sq_dist = np.sum(pcp_diff ** 2, axis=-1)
        
        cos_pb = np.cos(self.pb)
        sin_pb = np.sin(self.pb)
        
        self.K = (1 / (2 * np.pi)) * (
            pcp_diff[..., 1] * cos_pb[:, np.newaxis]
            - pcp_diff[..., 0] * sin_pb[:, np.newaxis]
        ) / pcp_sq_dist

        # Inverse of coefficient matrix: (Needed for solution of panel method eqn.)
        self.K_inv = np.linalg.inv(self.K)
        t1 = time.perf_counter() - t 
        print(f"time taken to inverse is {t1}")




class RegularPolygon:
    """Class to generate regular polygons bounded by the unit circle with the first point lying at (0,1)"""

    def __init__(self, sides=4, centre=(0, 0), rotation=0, radius=1) -> None:
        self.n = sides
        # define the radius of the circle within which the regular polygon lies:
        self.radius = radius
        # angle by which to rotate the shape (degrees for ease of use)
        self.rotation_angle = np.radians(rotation)
        # how much to translate the shape so its centre lies where the user wishes
        self.centre = np.array(centre)
        # self.points = self.final_coords()

    def rotation_matrix2D(self, theta):
        """return a rotation matrix to rotate a vector clockwise by theta radians"""
        # define cos(i*alpha) and sin(i*alpha)
        c, s = np.cos(theta), np.sin(theta)
        # create rotation matrix using previous definitions
        R = np.array(((c, s), (-s, c)))
        return R

    def translate(self, points, v):
        """translate all points in np array points by a 2D vector v"""
        translated = points + np.array(v)
        return translated

    def rotate(self, points, theta):
        """rotates all points by an angle theta (radians) clockwise"""
        # create the rotation matrix
        R_theta = self.rotation_matrix2D(theta)
        # rotate each point in points element wise using list comprehension
        rotated = [np.matmul(R_theta, point) for point in points]
        return rotated

    def regular_coords(self):
        """Create a an array of coordinates of a regular polygon with n sides"""
        # define an empty list to hold point co-ordinates:
        p_list = []
        # define the first point at (0,1)
        P0 = np.array((0, self.radius))
        for i in range(self.n):
            alpha_i = i * 2 * np.pi / self.n
            # generate the rotation matrix to obtain i^th coordinate
            Ri = self.rotation_matrix2D(alpha_i)
            # Ri*P0 will generate the i^th coordinate
            Pi = np.matmul(Ri, P0)
            # add newest point to list of points
            p_list.append(Pi)
        return p_list

    def points(self):
        """return final coordinates after expansion, rotation and translation"""
        # first rotate the polygon so that it is still centred on 0
        rotated = self.rotate(self.regular_coords(), self.rotation_angle)
        # then translate the points by the centre vector
        translated = self.translate(rotated, self.centre)
        # add third dimension for compatibility with Building class. The 1.2 is a height at which the drones see the buildings
        #FIXME remove magic number
        final = np.c_[translated, 1.2 * np.ones(self.n)]
        return final


# if __name__ == "__main__":
#     a= RegularPolygon(3,rotation=0,radius=1)
#     c = a.points()
#     print(c)
#     d = a.points()
#     print(f"d = {d}")
#     print(d.shape)
#     b = Building(d)
