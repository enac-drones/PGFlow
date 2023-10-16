import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import ArrayLike
from src.building import Building
from src.vehicle import Vehicle
from src.cases import Case, Cases
from src.arena import ArenaMap
from src.utils.simulation_utils import run_simulation, set_new_attribute
import src.utils.plot_utils as plt_utils
from matplotlib.patches import Polygon, FancyArrow
from matplotlib.lines import Line2D
from typing import List, Dict

from gui.entities import Drone, Obstacle
from gui.patches import Marker, DronePath, ObstaclePatch
from gui.utils import distance_between_points
from gui.construction import BuildingCreator


class InteractivePlot:

    CLICK_THRESHOLD = 0.14
    FIG_SIZE = (8, 8)
    AXIS_LIMITS = (-5, 5)

    def __init__(self):
        self._selected_building: Obstacle = None
        self.original_colors: dict = {}
        # Setup the default plot
        self.plot_setup()
        # Define variables
        self.setup_data()
        # Connect event handlers
        self.connect_event_handlers()

        self.building_creator = BuildingCreator(self.ax)

        plt.show()

    @property
    def selected_building(self):
        return self._selected_building

    @selected_building.setter
    def selected_building(self, new_building: Obstacle):
        """Highlight selected building in pink or deselect it if it is already selected.
        This function is called when a building is selected or deselected.
        patch: ObstaclePatch
        Return: None
        """
        if self._selected_building:
            current_patch = self.building_patches[self._selected_building]
            current_patch.deselect()
        if new_building:
            new_building_patch = self.building_patches[new_building]
            new_building_patch.select()
        self._selected_building = new_building
        self.update()

    def setup_data(self) -> None:
        self.drones: list[Drone] = []
        self.buildings: list[Building] = []
        self.current_drone = None
        self.mode = "building"  # 'building', 'drone', or None
        self.drone_start = None
        self.drone_patches: dict[Drone, DronePath] = {}
        self.building_patches: dict[Building, ObstaclePatch] = {}
        self.current_building_points: list[Line2D] = []
        self.actions_stack = []  # New line to track the actions

        self.temp_elements = []  # List to store temporary graphical elements.

        self.selected_drone: Drone = None
        self.initial_click_position = None
        self.selected_vertex = None
        self.building_picked = False

        return None

    def connect_event_handlers(self) -> None:

        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.fig.canvas.mpl_connect("button_release_event", self.on_button_release)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.fig.canvas.mpl_connect("pick_event", self.on_pick)

        return None

    def handle_vertex_movement(self, event):

        if not self.building_patches:
            return False
        # Flatten list of vertices with their indices (make a generator object)
        # all_vertices = ((building, j, v) for i, building in enumerate(self.building_patches) for j, v in enumerate(building.get_xy()))
        all_vertices = (
            (building, j, v)
            for building in self.building_patches.keys()
            for j, v in enumerate(building.vertices)
        )

        # Find the closest vertex
        closest_building, closest_vertex_index, closest_vertex = min(
            all_vertices,
            key=lambda x: distance_between_points(x[2][:2], [event.xdata, event.ydata]),
        )

        # Check if the closest vertex is close enough to be selected
        dist = np.linalg.norm(np.array([event.xdata, event.ydata]) - closest_vertex[:2])
        if (
            not dist < self.CLICK_THRESHOLD
        ):  # This threshold determines how close the click should be to consider a match
            return False
        self.selected_vertex = closest_vertex_index
        self.initial_click_position = None
        self.selected_building = closest_building

        return True



    def handle_drone_movement(self, event) -> bool:
        # Check if a drone starting or ending point was clicked
        point = [event.xdata, event.ydata]
        for drone in self.drones:
            start_dist = distance_between_points(drone.position[:2], point)
            end_dist = distance_between_points(drone.goal[:2], point)
            if (
                start_dist < self.CLICK_THRESHOLD
            ):  # This threshold determines how close the click should be to consider a match
                self.selected_drone = drone
                self.dragging_drone_point = "start"
                return True
            elif end_dist < self.CLICK_THRESHOLD:
                self.selected_drone = drone
                self.dragging_drone_point = "end"
                return True

            # Check if the click is on the arrow connecting the drone start and end points
            if drone.click_near_arrow(
                drone.position[:2],
                drone.goal[:2],
                event,
                threshold=self.CLICK_THRESHOLD,
            ):
                self.selected_drone = drone
                self.dragging_drone_point = "arrow"
                self.initial_click_position = point
                return True

        self.selected_drone = None
        self.dragging_drone_point = None
        return False

    def handle_building_placement(self, event) -> None:
        self.selected_building = None
        if self.current_drone:
            self.temp_elements.remove(self.drone_start)
            self.drone_start.remove()
            self.current_drone = None
        # Add a corner to the current building at the click location

        point = Marker((event.xdata, event.ydata), "go").create_marker()

        self.current_building_points.append(point)
        self.update()
        return None

    def handle_drone_placement(self, event) -> None:
        # clear any buildings before starting drones
        # Add a drone at the click location
        self.selected_building = None
        if self.current_drone is None:
            # initialise the drone
            # what to do when we draw the initial position of the drone
            # This is the initial position of the drone

            self.current_drone = Drone(
                ID=f"V{len(self.drones)}", position=None, goal=None
            )
            self.current_drone.position = [event.xdata, event.ydata, 0.5]

            # self.drone_start, = self.ax.plot(*self.current_drone.position[:2],'ko')
            self.drone_start = Marker(
                self.current_drone.position[:2], style="ko"
            ).create_marker()
            # self.ax.add_artist(self.drone_start)
            self.temp_elements.append(self.drone_start)
            self.update()
        else:
            # drone initial position is already defined, now add the destination (goal)
            # This is the goal position of the drone
            self.current_drone.goal = [event.xdata, event.ydata, 0.5]

            self.drones.append(self.current_drone)
            self.actions_stack.append(("drone", self.current_drone))
            self.temp_elements.remove(self.drone_start)
            self.drone_start.remove()
            self.drone_start = None

            # d = self.current_drone

            current_drone_path = DronePath(self.current_drone, self.ax)
            current_drone_path.create_patches()

            self.drone_patches[self.current_drone] = current_drone_path
            self.current_drone = None
            self.update()
        return None

    def on_click(self, event):
        # ORDER MATTERS

        # If clicked outside of the plot, do nothing
        if not event.xdata or not event.ydata:
            return

        # handle moving building vertices
        if self.handle_vertex_movement(event):
            return

        if self.selected_building:
            return
        self.selected_building = None

        # Check if a drone was clicked and handle its movement if necessary
        if self.handle_drone_movement(event):
            return
        # Check if a building was clicked and handle its movement if necessary

        # Proceed with building placement
        if self.mode == "building":
            self.handle_building_placement(event)
            return

        # Proceed with drone placement
        elif self.mode == "drone":
            self.handle_drone_placement(event)
            return

        # Update the plot
        self.update()

    def on_pick(self, event):
        # Check if the picked artist is a Polygon (optional but can be useful)
        if not isinstance(event.artist, plt.Polygon):
            return
        polygon = event.artist
        for building, building_patch in self.building_patches.items():
            if building_patch == polygon:
                self.selected_building = building
                break

        self.initial_click_position = [event.mouseevent.xdata, event.mouseevent.ydata]
        # Your code to handle the picked building here
        # ...

    def on_mouse_move(self, event):

        point = [event.xdata, event.ydata]

        # If the point is out of the map area, skip the rest of this method
        if any(not isinstance(item, (int, float)) for item in point):
            return
        ##########################################################################################
        # move the vertex if one is selected
        if self.selected_building is not None and self.selected_vertex is not None:
            # # move the relevent vertex
            self.selected_building.move_vertex(self.selected_vertex, point)
            self.building_patches[self.selected_building].update_visual()

            self.update()  # Redraw to show the moved vertex

        ###########################################################################################
        # move the whole building patch
        elif self.selected_building and self.initial_click_position:
            ds = np.array(point) - np.array(self.initial_click_position)
            # Move the building
            # set the vertices of the src.Building object, then copy them into the building patch
            self.selected_building.move_building(ds)
            self.building_patches[self.selected_building].update_visual()
            # Update the initial click position for next movement calculation
            self.initial_click_position = point

            # Redraw to show the moved building
            self.update()
        ###########################################################################################
        # Move the drone
        elif self.selected_drone:
            if self.dragging_drone_point == "start":
                self.selected_drone.position = np.array([*point, 0.5])

            elif self.dragging_drone_point == "end":
                self.selected_drone.goal = np.array([*point, 0.5])
            elif self.dragging_drone_point == "arrow":
                # Move both start and end points, and update all corresponding patches
                ds = np.array(point) - np.array(self.initial_click_position)

                self.selected_drone.move_whole_drone(ds)

            self.initial_click_position = point
            self.drone_patches[
                self.selected_drone
            ].update()  # update the graphics of the drone

            self.update()  # This will redraw the drone starting or ending point in its new position

    def on_button_release(self, event):
        self.selected_building = None
        self.initial_click_position = None
        self.selected_drone = None
        self.dragging_drone_point = None
        self.selected_vertex = None

    def on_key_press(self, event):
        # switch between building and drone placement modes
        self.toggle_mode(event)

        if (
            event.key == "tab"
            and self.mode == "building"
            and len(self.current_building_points) >= 3
        ):
            # plot the building
            self.finalize_building()

        if event.key == "cmd+z":
            self.undo_last_action()

        elif event.key == "escape":
            self.clear_temp_elements()

        elif event.key == "enter":
            # run the simulation
            self.run()

    def generate_case(self, name):
        height = 1.2
        # this line adds a third dimension to the x,y coordinates of the building patches and creates a building object from each patch
        buildings = [
            Building(
                np.hstack(
                    [
                        building.vertices,
                        np.full((building.vertices.shape[0], 1), height),
                    ]
                )
            )
            for building in self.building_patches
        ]

        # buildings = [Building(patch.get_xy()) for patch in self.building_patches]
        c = Case(name=name)
        c.buildings = buildings
        c.vehicle_list = []
        c.vehicle_list = [
            Vehicle(ID=v.ID, source_strength=1, imag_source_strength=0.5)
            for v in self.drones
        ]
        for idx, d in enumerate(self.drones):
            c.vehicle_list[idx].Set_Position(d.position)
            c.vehicle_list[idx].Set_Goal(goal=d.goal, goal_strength=5, safety=None)
            c.vehicle_list[idx].Go_to_Goal(
                altitude=0.5, AoAsgn=0, t_start=0, Vinfmag=0
            )  # FIXME add these to the json
        generator = Cases(filename="examples/gui_testing.json")
        generator.add_case(c)
        generator.update_json()

        complete_case = generator.get_case("examples/gui_testing.json", "Test Case")
        return complete_case

    def update(self):
        # draw the canvas again
        self.fig.canvas.draw()

    def clear_temp_elements(self):
        for elem in self.temp_elements:
            elem.remove()
        for point in self.current_building_points:
            point.remove()
        self.temp_elements = (
            []
        )  # Clear the list after removing all elements from the plot.
        self.current_building_points = []
        self.current_drone = None
        self.update()

    def undo_last_action(self):
        if not self.actions_stack:
            return

        action, obj = self.actions_stack.pop()
        if action == "building":
            patch = self.building_patches[obj]
            patch.remove()
            self.buildings.remove(obj)
            del self.building_patches[obj]

        elif action == "drone":
            if obj in self.drones:
                self.drones.remove(obj)
                marker_start, marker_end, arrow = self.drone_patches.pop(obj).patches()

                marker_start.remove()
                marker_end.remove()
                arrow.remove()

        self.fig.canvas.draw()  # Redraw the figure to reflect changes
        # self.update()

    def run(self):
        my_case = self.generate_case(name="Test Case")
        result = run_simulation(
            my_case,
            t=2000,
            update_every=1,
            stop_at_collision=False,
            max_avoidance_distance=20,
        )
        asdf = plt_utils.PlotTrajectories(my_case, update_every=1)
        asdf.show()

    def toggle_mode(self, event):
        """
        Switch between building and drone placement modes
        """
        if event.key == "d":
            self.mode = "drone"
        elif event.key == "b":
            self.mode = "building"

    def finalize_building(self):
        if not len(self.current_building_points) >= 3:
            return
        vertices = np.array(
            [point.get_xydata() for point in self.current_building_points]
        )
        vertices = vertices.squeeze(axis=1)
        building = Obstacle(vertices)
        patch = self.building_creator.create_building(building)
        # self.building_patches.append(patch)
        self.building_patches[building] = patch
        self.buildings.append(building)
        self.actions_stack.append(("building", building))
        self.ax.add_patch(patch)

        # Handle the removal of temporary points here
        for point in self.current_building_points:
            point.remove()
        self.current_building_points = []
        self.update()

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
            "'b': switch to building mode, click to place vertices of building\n"
            "Tab: complete a building, \n"
            "'d': switch to drone mode, "
            "Enter: run the simulation"
        )

        fig.text(
            0.2,
            0.93,
            instructions,
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        self.fig, self.ax = fig, ax
        return None


if __name__ == "__main__":
    # Example usage:

    plot = InteractivePlot()
    print("done")


# Suggestions:
# Save arena, just buildings, just drones etc
# better instructions
# vectors showing output of panel flow for each drone
# dragging buildings
# changing drone with click and drag
# change drone parameters such as source strength, imaginary source strength, goal strength, goal safety etc
# cooperating or not (can turn on and off for each drone)
