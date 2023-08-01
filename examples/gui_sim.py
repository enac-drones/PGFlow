import matplotlib.pyplot as plt
import numpy as np
from src.building import Building
from src.vehicle import Vehicle
from src.cases import Case, Cases
from src.arena import ArenaMap
from src.utils.simulation_utils import run_simulation, set_new_attribute
import src.utils.plot_utils as plt_utils


class InteractivePlot:
    FIG_SIZE = (8, 8)
    AXIS_LIMITS = (-5, 5)
    def __init__(self):
        self.fig, self.ax = self.plot_setup()
        self.ax.set_xlim((-5, 5))
        self.ax.set_ylim((-5, 5))
        self.buildings = []
        self.drones = []
        self.current_building = []
        self.current_drone = None
        self.mode = 'building'  # 'building', 'drone', or None
        self.current_building_points = []
        self.drone_start = None

        # Connect event handlers
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)


        plt.show()

    def on_click(self, event):
        # print(f'{self.mode = }')
        # print(self.buildings,self.current_building, len(self.current_building),self.mode)
        if not event.xdata or not event.ydata:
            return None
        if self.mode == 'building':
            self.current_drone = None
            # print("in building mode")
            # Add a corner to the current building at the click location
            self.current_building.append([event.xdata, event.ydata,1.2])
        elif self.mode == 'drone':
            # clear any buildings before starting drones
            self.current_building = []
            # Add a drone at the click location
            if self.current_drone is None:
                # This is the initial position of the drone
                self.current_drone = Vehicle(ID=f'V{len(self.drones)}',source_strength=1,imag_source_strength=0.5)
                self.current_drone.Set_Position([event.xdata, event.ydata, 0.5])
            else:
                # This is the goal position of the drone
                # self.current_drone.goal = np.array([event.xdata, event.ydata,1.2])

                # myVehicle.Set_Position(position)
                self.current_drone.Set_Goal(goal=[event.xdata, event.ydata,0.5], goal_strength=5, safety=None)
                self.current_drone.Go_to_Goal(
                    altitude=0.5, AoAsgn=0, t_start=0, Vinfmag=0
                )  # FIXME add these to the json
                self.drones.append(self.current_drone)
                self.current_drone = None

        # Update the plot
        self.update()

    def on_key_press(self, event):
        if event.key == 'd':
            self.mode = 'drone'
        elif event.key == 'b':
            self.mode = 'building'
        elif event.key == 'tab' and self.mode == 'building' and len(self.current_building) >= 3:
            # print(f'{self.current_building = }')
            # The building is complete; add it to the list of buildings
            self.buildings.append(Building(self.current_building))
            self.current_building = []
            # Update the plot
            self.update()
        elif event.key == 'enter':
            my_case = self.generate_case(name = "Test Case")
            # print(my_case.vehicle_list,"dad")
            result = run_simulation(
                my_case,
                t=2000,
                update_every=1,
                stop_at_collision=False,
                max_avoidance_distance=20,
            )
            # print(my_case.vehicle_list,"dad")
            plt.close()
            asdf = plt_utils.PlotTrajectories(my_case, update_every=50)
            asdf.show()

    def generate_case(self,name):
        c = Case(name = name)
        c.buildings = self.buildings
        # print(f'{self.drones=}')
        c.vehicle_list = self.drones
        # print(f'{c.vehicle_list=}')
        generator = Cases(filename='examples/gui_testing.json')
        generator.add_case(c)
        generator.update_json()

        complete_case = generator.get_case('examples/gui_testing.json','Test Case')
        # c.arena = ArenaMap(buildings=self.buildings)
        # print(c.buildings,c.vehicle_list)
        return complete_case


    def update(self):
        # Clear the plot
        # print("inside update mode")
        # self.ax.clear()
        self.update_buildings()
        # Plot the current drones
        self.update_drones()
        # If a building or drone is currently being placed, plot it as well
        # if self.current_building:
        #     self.ax.add_patch(plt.Polygon(self.current_building, fill=None, edgecolor='r'))

        # if self.current_drone is not None:
        #     self.ax.plot(*self.current_drone.position, 'go')  # Initial position in green

        self.fig.canvas.draw()

    def update_buildings(self):
        if not self.current_building:
            for point in self.current_building_points:
                point.remove()
            self.current_building_points = []
        for coord in self.current_building:
            point, = self.ax.plot(*coord[:2],'go')
            self.current_building_points.append(point)
        # Plot the current buildings
        for building in self.buildings:
            # print(building.vertices.shape)
            # column_slice = slice(None,2,None) testing the slice class and failing lol
            self.ax.add_patch(plt.Polygon(building.vertices[:,:2]))

    def update_drones(self):
        # print('in update')
        if self.current_drone:
            # print('adfasd',self.current_drone.position[:2])
            self.drone_start, = self.ax.plot(*self.current_drone.position[:2],'ko')
        elif self.drone_start:
            # print('hahahah')
            self.drone_start.remove()
            self.drone_start = None
            
        for drone in self.drones:
            self.ax.plot(*drone.position[:2], 'b*')  # Initial position in blue
            self.ax.plot(*drone.goal[:2], 'r*')  # Goal position in red
            # Add an arrow with a line using the 'arrow' function
            self.ax.arrow(*drone.position[:2], drone.goal[0]-drone.position[0], drone.goal[1]-drone.position[1], length_includes_head = True, head_width=0.2, head_length=0.2, fc='k', ec='k',linestyle = '-')



    def switch_to_building_mode(self):
        self.mode = 'building'

    def switch_to_drone_mode(self):
        self.mode = 'drone'

    def plot_setup(self):
        fig = plt.figure(figsize=self.FIG_SIZE)
        ax = fig.add_subplot(111)
        fig.subplots_adjust(bottom=0.1, top=0.9)

        ax.set_xlim(self.AXIS_LIMITS)
        ax.set_ylim(self.AXIS_LIMITS)
        ax.set_box_aspect(1)
        ax.set_xlabel("East --> (m)")
        ax.set_ylabel("North --> (m)")
        ax.grid(color="k", linestyle="-", linewidth=0.5, which="major")
        ax.grid(color="k", linestyle=":", linewidth=0.5, which="minor")
        # ax.grid(True)
        ax.minorticks_on()

        # Add instructions
        instructions = (
            "Instructions:\n"
            "'b': switch to building mode, "
            "'d': switch to drone mode \n"
            "Tab: complete a building, "
            "Enter: run the simulation"
        )
        fig.text(0.2, 0.93, instructions, fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        return fig, ax

# Example usage:
plot = InteractivePlot()
plot.switch_to_building_mode()
print("done")
# The user can now click on the plot to place buildings
