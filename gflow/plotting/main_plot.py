import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json

from gflow.plotting.graphics.path_graphics import PathPlotter
from gflow.plotting.graphics.building_graphics import BuildingsPlotter
from gflow.plotting.graphics.drone_graphics import DronePlotter
from gflow.plotting.entities.building import BuildingEntity
from gflow.plotting.entities.drone import DroneEntity
from gflow.plotting.entities.path import PathEntity

class SimulationVisualizer:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.buildings = []
        self.vehicles = []
        self.paths = []
        self.load_data()

    def load_data(self):
        """Load and parse data from the JSON file."""
        with open(self.json_file_path, 'r') as file:
            data:dict = json.load(file)
            self.buildings = data.get('buildings', [])
            self.vehicles = data.get('vehicles', [])

    def initial_plot(self):
        fig, ax = plt.subplots()

        # Plot buildings
        buildings_plotter = BuildingsPlotter(self.buildings)
        buildings_plotter.plot(ax)
        buildings_plotter.set_building_attributes(fc = "k", ec = "r")

        # Plot vehicles and their paths
        drone_plotter = DronePlotter(vehicle_data=self.vehicles)
        drone_plotter.plot(ax)
        drone_plotter.set_circle_attributes(radius=1, ec = "pink", lw = 1)
        drone_plotter.set_point_attributes(color="r",marker="*")

        path_manager = PathPlotter(vehicle_data=self.vehicles)
        path_manager.plot(ax)

        path_manager.set_path_attributes(color="r",linewidth=2)

        LIMS = (-5,5)
        ax.set_xlim(LIMS)
        ax.set_ylim(LIMS)

        ax.set_aspect('equal', adjustable='box')
        plt.show()

    def animate_simulation(self):
        fig, ax = plt.subplots()

        # Initialize plotters
        buildings_plotter = BuildingsPlotter(self.buildings)
        buildings_plotter.plot(ax)
        drone_plotter = DronePlotter(self.vehicles)
        drone_plotter.plot(ax)
        path_manager = PathPlotter(self.vehicles)
        path_manager.plot(ax)
        # Set up the animation
        num_frames = 10000
        def animate(frame):
            drone_plotter.animate_drones(frame,num_frames)
            patches = drone_plotter.get_patches()
            # Redraw the canvas
            fig.canvas.draw_idle()
            return patches

        # Determine the number of frames based on the longest path
        # num_frames = max(len(drone.path.path) for drone in drone_plotter.drone_entities)

        # anim = FuncAnimation(fig, animate, frames=num_frames, interval=100, repeat=False)
        anim = FuncAnimation(fig=fig,
                             func=animate,
                             frames=num_frames,
                             init_func=None,
                             interval=1,
                             repeat=True,
                             repeat_delay = 1000,
                             blit=False,
                             )

        LIMS = (-5,5)
        ax.set_xlim(LIMS)
        ax.set_ylim(LIMS)

        ax.set_aspect('equal', adjustable='box')
        plt.show()

        return anim

# Example usage
if __name__ == '__main__':
    visualizer = SimulationVisualizer('example_output.json')
    visualizer.animate_simulation()
