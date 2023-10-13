from gui.patches import ObstaclePatch
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
from typing import List


class BuildingCreator:

    def __init__(self, ax:plt.Axes) -> None:
        self.ax = ax
        self.current_building_points: List[Line2D] = []
        self.building_patches: List[ObstaclePatch]  = []

    def create_building(self, vertices):
        patch = ObstaclePatch(
            vertices,
            edgecolor=(0,0,0,1),
            facecolor=(0,0,1,0.5),
            closed=True,
            linewidth=2.0,
            picker=True 
        )
        self.ax.add_patch(patch)
        self.building_patches.append(patch)

        for point in self.current_building_points:
            point.remove()
        self.current_building_points = []
        return patch
