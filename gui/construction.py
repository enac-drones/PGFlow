from gui.patches import ObstaclePatch
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
from typing import List
from gui.entities import Obstacle, Drone
import numpy as np


class Creator:
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

class PatchManager:
    def __init__(self, ax: plt.Axes):
        self.ax = ax
        self.building_patches = {}
        self.drone_patches = {}

    def add_building_patch(self, building: Obstacle, **kwargs):
        patch = ObstaclePatch(
            building,
            edgecolor=kwargs.get('edgecolor', (0, 0, 0, 1)),
            facecolor=kwargs.get('facecolor', (0, 0, 1, 0.5)),
            closed=kwargs.get('closed', True),
            linewidth=kwargs.get('linewidth', 2.0),
            picker=kwargs.get('picker', True),
        )
        self.ax.add_patch(patch)
        self.building_patches[building] = patch

    def add_drone_patch(self, drone: Drone, **kwargs):
        # Similar logic for adding drone patches
        pass

    def remove_building_patch(self, building: Obstacle):
        if building in self.building_patches:
            self.building_patches[building].remove()
            del self.building_patches[building]

    def remove_drone_patch(self, drone: Drone):
        # Similar logic for removing drone patches
        pass

    def clear_all(self):
        for patch in self.building_patches.values():
            patch.remove()
        for patch in self.drone_patches.values():
            patch.remove()
        self.building_patches.clear()
        self.drone_patches.clear()

