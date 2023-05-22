import math

import numpy as np
import pyclipper

# from numpy import linalg

"""##Building Code"""


class Building:
    def __init__(
        self, vertices, position=None
    ):  # Buildings(obstacles) are defined by coordinates of their vertices.
        self.vertices = np.array(vertices)
        # print(f"the vertices are {self.vertices} shape of the vertices is {self.vertices.shape}")
        # print('\n These are the vertices...')
        self.inflate(rad=0.0)
        # print(f"points after inflation are {self.vertices}")
        self.position = np.array(position)
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
        Xavg = np.mean(points[:, 0:1])
        Yavg = np.mean(points[:, 1:2])
        angles = np.arctan2(
            (Yavg * np.ones(len(points[:, 1])) - points[:, 1]),
            (Xavg * np.ones(len(points[:, 0])) - points[:, 0]),
        )
        sorted_angles = sorted(zip(angles, points), reverse=True)
        points_sorted = np.vstack([x for y, x in sorted_angles])
        self.vertices = points_sorted

    def panelize(self, size):
        # Divides obstacle edges into smaller line segments, called panels.
        for index, vertice in enumerate(self.vertices):
            xyz1 = self.vertices[index]  # Coordinates of the first vertice
            xyz2 = self.vertices[
                (index + 1) % self.vertices.shape[0]
            ]  # Coordinates of the next vertice
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

    def calculate_coef_matrix(self, method="Vortex"):
        # Calculates coefficient matrix.
        if method == "Vortex":
            self.nop = self.panels.shape[0]  # Number of Panels
            self.pcp = np.zeros((self.nop, 2))  # Controlpoints: at 3/4 of panel
            self.vp = np.zeros((self.nop, 2))  # Vortex point: at 1/4 of panel
            self.pl = np.zeros((self.nop, 1))  # Panel Length
            self.pb = np.zeros(
                (self.nop, 1)
            )  # Panel Orientation; measured from horizontal axis, ccw (+)tive, in radians

            XYZ2 = self.panels  # Coordinates of end point of panel
            XYZ1 = np.roll(
                self.panels, 1, axis=0
            )  # Coordinates of the next end point of panel

            self.pcp = (
                XYZ2 + (XYZ1 - XYZ2) * 0.75
            )  # Controlpoints point at 3/4 of panel. #self.pcp  = 0.5*( XYZ1 + XYZ2 )[:,:2]
            self.vp = XYZ2 + (XYZ1 - XYZ2) * 0.25  # Vortex point at 1/4 of panel.
            self.pb = (
                np.arctan2((XYZ2[:, 1] - XYZ1[:, 1]), (XYZ2[:, 0] - XYZ1[:, 0]))
                + np.pi / 2
            )
            self.K = np.zeros((self.nop, self.nop))
            for m in range(self.nop):
                for n in range(self.nop):
                    self.K[m, n] = (
                        1
                        / (2 * np.pi)
                        * (
                            (self.pcp[m][1] - self.vp[n][1]) * np.cos(self.pb[m])
                            - (self.pcp[m][0] - self.vp[n][0]) * np.sin(self.pb[m])
                        )
                        / (
                            (self.pcp[m][0] - self.vp[n][0]) ** 2
                            + (self.pcp[m][1] - self.vp[n][1]) ** 2
                        )
                    )
            # Inverse of coefficient matrix: (Needed for solution of panel method eqn.)
            self.K_inv = np.linalg.inv(self.K)
        elif method == "Source":
            pass

    def gamma_calc(self, vehicle, othervehicles, arenamap, method="Vortex"):
        # Calculates unknown vortex strengths by solving panel method eq.

        vel_sink = np.zeros((self.nop, 2))
        vel_source = np.zeros((self.nop, 2))
        vel_source_imag = np.zeros((self.nop, 2))
        # vel_source_imag1 = np.zeros((self.nop, 2))
        # vel_source_imag2 = np.zeros((self.nop, 2))
        # vel_source_imag3 = np.zeros((self.nop, 2))
        RHS = np.zeros((self.nop, 1))

        if method == "Vortex":
            vel_sink[:, 0] = (
                -vehicle.sink_strength * (self.pcp[:, 0] - vehicle.goal[0])
            ) / (
                2
                * np.pi
                * (
                    (self.pcp[:, 0] - vehicle.goal[0]) ** 2
                    + (self.pcp[:, 1] - vehicle.goal[1]) ** 2
                )
            )
            vel_sink[:, 1] = (
                -vehicle.sink_strength * (self.pcp[:, 1] - vehicle.goal[1])
            ) / (
                2
                * np.pi
                * (
                    (self.pcp[:, 0] - vehicle.goal[0]) ** 2
                    + (self.pcp[:, 1] - vehicle.goal[1]) ** 2
                )
            )

            vel_source_imag[:, 0] = (
                vehicle.imag_source_strength * (self.pcp[:, 0] - vehicle.position[0])
            ) / (
                2
                * np.pi
                * (
                    (self.pcp[:, 0] - vehicle.position[0]) ** 2
                    + (self.pcp[:, 1] - vehicle.position[1]) ** 2
                )
            )
            vel_source_imag[:, 1] = (
                vehicle.imag_source_strength * (self.pcp[:, 1] - vehicle.position[1])
            ) / (
                2
                * np.pi
                * (
                    (self.pcp[:, 0] - vehicle.position[0]) ** 2
                    + (self.pcp[:, 1] - vehicle.position[1]) ** 2
                )
            )

            for i, othervehicle in enumerate(othervehicles):
                vel_source[:, 0] += (
                    othervehicle.source_strength
                    * (self.pcp[:, 0] - othervehicle.position[0])
                ) / (
                    2
                    * np.pi
                    * (
                        (self.pcp[:, 0] - othervehicle.position[0]) ** 2
                        + (self.pcp[:, 1] - othervehicle.position[1]) ** 2
                    )
                )
                vel_source[:, 1] += (
                    othervehicle.source_strength
                    * (self.pcp[:, 1] - othervehicle.position[1])
                ) / (
                    2
                    * np.pi
                    * (
                        (self.pcp[:, 0] - othervehicle.position[0]) ** 2
                        + (self.pcp[:, 1] - othervehicle.position[1]) ** 2
                    )
                )

            RHS[:, 0] = (
                -vehicle.V_inf[0] * np.cos(self.pb[:])
                - vehicle.V_inf[1] * np.sin(self.pb[:])
                - vel_sink[:, 0] * np.cos(self.pb[:])
                - vel_sink[:, 1] * np.sin(self.pb[:])
                - vel_source[:, 0] * np.cos(self.pb[:])
                - vel_source[:, 1] * np.sin(self.pb[:])
                - vel_source_imag[:, 0] * np.cos(self.pb[:])
                - vel_source_imag[:, 1] * np.sin(self.pb[:])
            )

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
        """return a rotation matrix to rotate a vector clockwise by theta"""
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
