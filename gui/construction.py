from gui.patches import ObstaclePatch
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
from typing import List
from gui.entities import Obstacle
import numpy as np


class BuildingCreator:
    def __init__(self, ax: plt.Axes) -> None:
        self.ax = ax

    def create_building(self, building: Obstacle):
        patch = ObstaclePatch(
            building,
            edgecolor=(0, 0, 0, 1),
            facecolor=(0, 0, 1, 0.5),
            closed=True,
            linewidth=2.0,
            picker=True,
        )

        return patch
