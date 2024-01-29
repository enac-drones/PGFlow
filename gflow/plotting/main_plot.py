import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json

from gflow.plotting.graphics.path_graphics import PathPlotter
from gflow.plotting.graphics.building_graphics import BuildingsPlotter
from gflow.plotting.graphics.drone_graphics import DronePlotter
from gflow.plotting.graphics.arrow_graphics import ArrowPlotter
from gflow.plotting.observer_utils import Observer
from gflow.plotting.ui_components import UIComponents

class SimulationVisualizer(Observer):
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.full_data = {}
        self.buildings = []
        self.vehicles = []
        self.paths = []
        self.current_frame = 0
        self.num_frames = 1000
        self.simulation_running = True

        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.load_data()
        self.setup(self.ax)
        self.anim = self.animate_simulation(self.fig)

    def load_data(self):
        """Load and parse data from the JSON file."""
        with open(self.json_file_path, 'r') as file:
            data:dict = json.load(file)
            self.buildings = data.get('buildings', [])
            self.vehicles = data.get('vehicles', [])
            self.arrows = data.get('desired_vectors', [])
            self.full_data = data

    def setup(self, ax):
        LIMS = (-5,5)
        ax.set_xlim(LIMS)
        ax.set_ylim(LIMS)
        ax.set_aspect('equal', adjustable='box')

        self.ui_components = UIComponents(self.ax)
        self.ui_components.add_observer(self)
        #this line makes sure the current axes are the main ones
        plt.sca(ax)

        # Initialize plotters
        buildings_plotter = BuildingsPlotter(self.buildings)
        buildings_plotter.plot(ax)
        self.drone_plotter = DronePlotter(self.vehicles)
        self.drone_plotter.plot(ax)
        # patches = drone_plotter.get_patches()
        # for p in patches:
        #     p.set_animated(False)
        path_manager = PathPlotter(self.vehicles)
        path_manager.plot(ax)
        self.arrow_manager = ArrowPlotter(self.vehicles)
        self.arrow_manager.plot(ax)

    def show_plot(self):
        plt.show()


    def call(self, event:str):
        if event == 'run':
            print('run')
            if not self.simulation_running:
                self.anim.resume()
                self.simulation_running = True

        elif event == 'pause':
            print("pause")
            if self.simulation_running:
                self.anim.pause()
                self.simulation_running = False

        elif event == 'reset':
            self.current_frame = 0
            if not self.simulation_running:
                self.update_visuals(frame=0)
        else:
            print('other')


    def animate_simulation(self, fig):
        
        # Set up the animation

        def animate(frame):
            # Use self.current_frame instead of the frame parameter
            self.drone_plotter.animate_drones(self.current_frame, self.num_frames)
            # patches = drone_plotter.get_patches()
            self.arrow_manager.animate_arrows(self.current_frame, self.num_frames)
            
            # Increment and reset frame counter
            self.current_frame += 1
            if self.current_frame >= self.num_frames:
                self.current_frame = 0

            # Redraw the canvas
            fig.canvas.draw_idle()

            #only return something if using blitting
            return None #patches


        anim = FuncAnimation(fig=fig,
                             func=animate,
                             frames=range(self.num_frames),
                             init_func=None,
                             interval=10/self.num_frames,
                            #  interval=10,
                             repeat=True,
                            #  repeat_delay = 1000,
                             blit=False,
                             )

        return anim
    
    def update_visuals(self, frame):
        """Update the visuals of the simulation to a specific frame."""
        # This should contain the logic to update your plot to a specific frame
        # For example, you might call animate_drones, animate_arrows, etc., for the given frame
        self.drone_plotter.animate_drones(frame, self.num_frames)
        self.arrow_manager.animate_arrows(frame, self.num_frames)
        self.fig.canvas.draw_idle()

    

# Example usage
if __name__ == '__main__':
    visualizer = SimulationVisualizer('example_output.json')
    visualizer.show_plot()
