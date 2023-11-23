import math

import numpy as np
import pyclipper
import time
from typing import List
from matplotlib.patches import Polygon

# from numpy import linalg

"""##Building Code"""


class Building:
    _id_counter = 0

    def __init__(
        self, vertices
    ):  # Buildings(obstacles) are defined by coordinates of their vertices.
        self.vertices = np.array(vertices)
        #automatically increment the id
        self.ID = f"B{Building._id_counter}"
        Building._id_counter += 1
        self.inflate(rad=0.0)
        # self.position = np.array(position)
        self.panels = np.array([])
        self.nop = None  # Number of Panels
        self.K = None  # Coefficient Matrix
        self.K_inv = None
        self.gammas = {}  # Vortex Strenghts
        # self.solution = np.array([])

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

    def panelize(self, size):
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

    def panelize_optimized(self, size):
        n_vertices = self.vertices.shape[0]
        # Calculate the edge lengths
        edge_lengths = np.linalg.norm(self.vertices - np.roll(self.vertices, -1, axis=0), axis=1)
        
        # Calculate the number of panels for each edge
        n_panels = np.ceil(edge_lengths / size).astype(int)
        
        # Initialize an empty array to store the panels
        total_panels = np.sum(n_panels)
        self.panels = np.zeros((total_panels, self.vertices.shape[1]))
        
        idx = 0
        for i in range(n_vertices):
            xyz1 = self.vertices[i]
            xyz2 = self.vertices[(i + 1) % n_vertices]
            panels_for_this_edge = np.linspace(xyz1, xyz2, n_panels[i]+1)[1:]
            
            self.panels[idx:idx + n_panels[i]] = panels_for_this_edge
            idx += n_panels[i]


    def contains_point(self, point):
        # Checks if a point lies within the building.
        p = Polygon(self.vertices[:, :2])
        return p.contains_point(point, radius=0)


    def calculate_coef_matrix(self):
        '''Calculate the Matrix inverse of the building'''
        t = time.time()
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
        t1 = time.time() - t 
        print(f"time taken to inverse is {t1}")


    

    def gamma_calc(self, vehicle, othervehicles):
        """Calculate the unknown vortex strengths of the building panels

        Args:
            vehicle (Vehicle): _description_
            othervehicles (list[Vehicle]): _description_
        """
        # Initialize arrays
        vel_sink = np.zeros((self.nop, 2))
        vel_source = np.zeros((self.nop, 2))
        vel_source_imag = np.zeros((self.nop, 2))
        RHS = np.zeros((self.nop, 1))

        # Pre-calculate repeated terms
        sink_diff = self.pcp[:,:2] - vehicle.goal[:2]
        sink_sq_dist = np.sum(sink_diff ** 2, axis=-1)
        imag_diff = self.pcp[:,:2] - vehicle.position[:2]
        imag_sq_dist = np.sum(imag_diff ** 2, axis=-1)

        # Velocity calculations for sink and imag_source
        vel_sink = -vehicle.sink_strength * sink_diff / (2 * np.pi * sink_sq_dist)[:, np.newaxis]
        vel_source_imag = vehicle.imag_source_strength * imag_diff / (2 * np.pi * imag_sq_dist)[:, np.newaxis]
        # Velocity calculations for source
        for othervehicle in othervehicles:
            source_diff = self.pcp[:,:2] - othervehicle.position[:2]
            source_sq_dist = np.sum(source_diff ** 2, axis=-1)
            vel_source += othervehicle.source_strength * source_diff / (2 * np.pi * source_sq_dist)[:, np.newaxis]

        # RHS calculation
        cos_pb = np.cos(self.pb)
        sin_pb = np.sin(self.pb)
        RHS[:, 0] = (
            - vehicle.V_inf[0] * cos_pb
            - vehicle.V_inf[1] * sin_pb
            - np.sum(vel_sink * np.array([cos_pb, sin_pb]).T, axis=1)
            - np.sum(vel_source * np.array([cos_pb, sin_pb]).T, axis=1)
            - np.sum(vel_source_imag * np.array([cos_pb, sin_pb]).T, axis=1)
        )


        # Solve for gammas
        self.gammas[vehicle.ID] = np.matmul(self.K_inv, RHS)



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
