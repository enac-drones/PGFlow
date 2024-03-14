# import math
# import random

# import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull
from rtree import index

from gflow.building import Building
from typing import List
from shapely.geometry import box, Point
from numpy.typing import ArrayLike

"""##Arena Code"""


class ArenaMap:
    inflation_radius = 0.2
    size = 0.04#max size of a panel?
    def __init__(
        self,
        buildings:list[Building]= None,
        # building_hulls=None,
        # generate="manual",
        # number_of_vehicles=1,
    ):
        # self.panels = None
        # self.inflation_radius = 0.2
        # self.size = 0.02 #max size of a panel?
        self.wind = [0, 0]
        self.windT = 0
        self.buildings = buildings
        self.rtree_index = index.Index()
        self._create_rtree_index()

       
        # this adds a sort of safety radius? Set to 0.2 previously, I will set it to 0 so it matches the exact buildings specified.
        self.Inflate(
            radius=self.inflation_radius
        )  # BUG Does weird clippings sometimes, eg when inflating a triangle #FIXME


    def Inflate(self, visualize=False, radius=1e-4):
        # Inflates buildings with given radius
        for building in self.buildings:
            building.inflate(rad=radius)

    def Panelize(self, size):
        # Divides building edges into smaller line segments, called panels.
        for building in self.buildings:
            building.panelize(size)

    def Calculate_Coef_Matrix(self, method="Vortex"):
        # !!Assumption: Seperate building interractions are neglected. Each building has its own coef_matrix
        for building in self.buildings:
            building.calculate_coef_matrix()

    def _create_rtree_index(self):
        for i, building in enumerate(self.buildings):
            bbox = building.get_bounding_box()
            self.rtree_index.insert(i, bbox.bounds)
        return None
            

    def get_nearby_buildings(self, drone_position, threshold_distance:float)->list[Building]:
        query_box = box(drone_position[0] - threshold_distance, drone_position[1] - threshold_distance,
                        drone_position[0] + threshold_distance, drone_position[1]+ threshold_distance)
        potential_buildings = list(self.rtree_index.intersection(query_box.bounds))

        nearby_buildings = []
        for i in potential_buildings:
            building_polygon = self.buildings[i].get_bounding_box()  # or however you represent the building shape
            drone_point = Point(drone_position)
            distance = drone_point.distance(building_polygon)
            if distance < threshold_distance:
                nearby_buildings.append(self.buildings[i])
        return nearby_buildings
    
    def contains_point(self, point2D:ArrayLike)->bool:
        'returns true if the point lies within any of the buildings'
        for building in self.buildings:
            if building.contains_point(point2D):
                return True
        return False
                

