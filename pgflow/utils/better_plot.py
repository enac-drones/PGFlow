
from __future__ import annotations


from typing import TYPE_CHECKING, Iterable, List
if TYPE_CHECKING:
    from pgflow.cases import Case
    from pgflow.building import Building


# from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Polygon

class BetterPlot:
    "Better Plotting class"
    FRAMES:int = 100
    LIMITS = (-5,5)
    def __init__(self, case:Case)->None:
        self.case = case
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(*self.LIMITS)
        self.ax.set_ylim(*self.LIMITS)
    
    def create_animation(self)->None:
        anim = FuncAnimation(
            fig=self.fig,
            func=self.animate,
            frames=self.FRAMES,
            init_func=self.initial_plot,
            interval=100,
            blit=True,
            )
        
        return anim
        
    def initial_plot(self)->Iterable:
        '''Initial plot at t=0'''
        buildings = self.get_buildings(self.case.buildings)
        for building in buildings:
            self.ax.add_artist(building)

        return buildings

    def animate(self, i:int)->Iterable:
        '''Animation function'''
        pass

    def get_buildings(self,buildings: List[Building]):
        '''Plot buildings'''
        building_artists = []
        for building in buildings:
            building_artist = Polygon(building.vertices[:,:2])
            building_artists.append(building_artist)

        return building_artists
    
    def show(self)->None:
        plt.show()





