import math
import random

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull

from .building import Building

"""##Arena Code"""


class ArenaMap:
    def __init__(
        self,
        buildings=None,
        building_hulls=None,
        generate="manual",
        number_of_vehicles=1,
    ):
        self.panels = None
        self.wind = [0, 0]
        self.windT = 0
        self.buildings = []
        if building_hulls is not None:
            generate = "auto"
            for key in building_hulls.keys():
                posList = building_hulls[key]["pos"]
                points = [
                    (pos[0], pos[1]) for pos in posList
                ]  # Turn into 3D here if needed !!!!
                hull = ConvexHull(points)
                self.buildings.append(
                    Building([[points[i][0], points[i][1], 3.0] for i in hull.vertices])
                )
                print(f"Adding {key} into list...")

            print(
                "--------------- Here are the Buildings -------------", self.buildings
            )
        if generate == "manual":
            # Give error if the buildings are not defined !
            self.buildings = buildings

        elif generate == "random":
            self.buildings = []
            self.buildings.append(self.AddRandomBuilding())
            number = version  # Number of buildings to be generated FIX THIS LATER
            while len(self.buildings) < number:
                temp_building = self.AddRandomBuilding()
                for i in range(len(self.buildings)):
                    x = self.buildings[i].position[0]
                    y = self.buildings[i].position[1]
                    r = self.buildings[i].position[2]
                    d = (
                        (x - temp_building.position[0]) ** 2
                        + (y - temp_building.position[1]) ** 2
                    ) ** 0.5
                    if d < r * 2 + temp_building.position[2]:
                        break
                    if i == len(self.buildings) - 1:
                        self.buildings.append(temp_building)

        # this adds a sort of safety radius? Set to 0.2 previously, I will set it to 0 so it matches the exact buildings specified.
        self.Inflate(
            radius=0.2
        )  # BUG Does weird clippings sometimes, eg when inflating a triangle #FIXME
        self.Panelize(size=0.01)
        self.Calculate_Coef_Matrix(method="Vortex")

    def Inflate(self, visualize=False, radius=1e-4):
        # Inflates buildings with given radius
        if visualize:
            self.Visualize2D(buildingno="All", show=False)
        for building in self.buildings:
            building.inflate(rad=radius)
        if visualize:
            self.Visualize2D(buildingno="All")
        # self.buildings[index].vertices[:,:2] = self.buildings[index].inflated

    def Panelize(self, size):
        # Divides building edges into smaller line segments, called panels.
        for building in self.buildings:
            building.panelize(size)

    def Calculate_Coef_Matrix(self, method="Vortex"):
        # !!Assumption: Seperate building interractions are neglected. Each building has its own coef_matrix
        for building in self.buildings:
            building.calculate_coef_matrix(method=method)

    def Visualize2D(self, buildingno="All", points="buildings", show=True):
        plt.grid(color="k", linestyle="-.", linewidth=0.5)
        # minx = -5 # min(min(building.vertices[:,0].tolist()),minx)
        # maxx = 5 # max(max(building.vertices[:,0].tolist()),maxx)
        # miny = -5 # min(min(building.vertices[:,1].tolist()),miny)
        # maxy = 5 # max(max(building.vertices[:,1].tolist()),maxy)
        # plt.xlim([minx, maxx])
        # plt.ylim([miny, maxy])
        if buildingno == "All":
            if points == "buildings":
                for building in self.buildings:
                    # plt.scatter(  np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) )
                    plt.plot(
                        np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
                        np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
                        "b",
                    )
                    plt.fill(
                        np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
                        np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
                        "b",
                    )
            elif points == "panels":
                for building in self.buildings:
                    plt.scatter(building.panels[:, 0], building.panels[:, 1])
                    plt.plot(building.panels[:, 0], building.panels[:, 1])
                    controlpoints = building.pcp
                    plt.scatter(controlpoints[:, 0], controlpoints[:, 1], marker="*")
            if show:
                plt.show()
        else:
            if points == "buildings":
                building = self.buildings[buildingno]
                plt.scatter(
                    np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
                    np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
                )
                plt.plot(
                    np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
                    np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
                )
            elif points == "panels":
                building = self.buildings[buildingno]
                controlpoints = building.pcp
                plt.scatter(building.panels[:, 0], building.panels[:, 1])
                plt.scatter(controlpoints[:, 0], controlpoints[:, 1], marker="*")
                plt.plot(
                    np.vstack((building.panels[:], building.panels[0]))[:, 0],
                    np.vstack((building.panels[:], building.panels[0]))[:, 1],
                    markersize=0,
                )
            if show:
                plt.show()

    def Visualize3D(self, buildingno="All", show="buildings"):
        pass

    def ScaleIntoMap(self, shape=np.array(((-1, -1), (1, 1)))):
        pass

    def AddCircularBuilding(
        self, x_offset, y_offset, no_of_pts, size, height=1, angle=0
    ):
        # n = 6  # number of points
        circle_list = []
        # offset_x = -3
        # offset_y = 3
        # size = 1
        # height = 1
        for i in range(no_of_pts):
            delta_rad = -2 * math.pi / no_of_pts * i
            circle_list.append(
                [
                    round(math.cos(delta_rad) * size + x_offset, 3),
                    round(math.sin(delta_rad) * size + y_offset, 3),
                    height,
                ]
            )
        print("Building(" + str(circle_list) + ")")

    def Wind(self, wind_str=0, wind_aoa=0, info="unknown"):
        self.wind[0] = wind_str * np.cos(wind_aoa)
        self.wind[1] = wind_str * np.sin(wind_aoa)
        if info == "known":
            self.windT = 1
        elif info == "unknown":
            self.windT = 0

    def AddRandomBuilding(self):
        center_x = round(random.uniform(-3, 3), 3)  # nosec
        center_y = round(random.uniform(-3, 3), 3)  # nosec
        # radius = round(random.uniform(0.25, 1),3)
        radius = round(random.uniform(0.25, 1.5), 3)  # nosec
        position = np.array([center_x, center_y, radius])
        n = random.randint(3, 10)  # number of vertices
        height = round(random.uniform(1.25, 2), 3)
        circle_list = []
        theta = np.sort(
            np.random.rand(n) * 2 * np.pi
        )  # Generate n random numbers btw 0-2pi and sort: small to large
        for j in range(n):
            circle_list.append(
                [
                    round(math.cos(theta[j]) * radius + center_x, 3),
                    round(math.sin(theta[j]) * radius + center_y, 3),
                    height,
                ]
            )
        return Building(circle_list, position)
