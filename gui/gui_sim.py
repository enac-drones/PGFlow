from __future__ import annotations

#FIXME these two lines are necessary because sometimes the imports don't work
import sys
sys.path.append(".")

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import ArrayLike

# from src.utils.simulation_utils import run_simulation, set_new_attribute
from matplotlib.lines import Line2D
from typing import List, Dict

from gui.entities import Drone, Obstacle
from gui.patches import Marker, DronePatch, ObstaclePatch
from gui.utils import distance_between_points, generate_case, run_case
from gui.construction import PatchManager
from gui.actions_stack import ActionsStack
from gui.ui_components import UIComponents
from gui.observer_utils import Observer

class InteractivePlot(Observer):

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
            current_patch = self.patch_manager.get_building_patch(self._selected_building)
            current_patch.deselect()
        if new_building:
            new_building_patch = self.patch_manager.get_building_patch(new_building)
            new_building_patch.select()
        self._selected_building = new_building
        self.update()

    def setup_data(self) -> None:
        # self.ui_components:UIComponents = UIComponents(self.ax)
        self.ui_components = UIComponents(self.ax)
        self.ui_components.add_observer(self)
        #this line makes sure the current axes are the main ones
        plt.sca(self.ax)

        self.patch_manager = PatchManager(self.ax)


        self.drones: list[Drone] = []
        self.buildings: list[Obstacle] = []
        self.current_drone = None
        self.mode = "building"  # 'building', 'drone', or None
        self.drone_start = None
        self.actions_stack = ActionsStack()  # New line to track the actions


        self.selected_drone: Drone = None
        self.initial_click_position = None
        self.selected_vertex = None

        return None

    def connect_event_handlers(self) -> None:

        self.fig.canvas.mpl_connect("pick_event", self.on_pick)
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.fig.canvas.mpl_connect("button_release_event", self.on_button_release)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)

        return None

    def handle_vertex_movement(self, event):
        """Returns True if a click is near a vertex of an obstacle"""
        print(self.buildings)
        if not self.buildings:
            return False

        # Find the closest vertex
        closest_building, closest_vertex_index = self._get_closest_vertex(
            [event.xdata, event.ydata]
        )

        # Check if the closest vertex is close enough to be selected
        dist = distance_between_points(
            closest_building.vertices[closest_vertex_index][:2],
            [event.xdata, event.ydata],
        )
        if dist >= self.CLICK_THRESHOLD:
            return False

        self.selected_vertex = closest_vertex_index
        self.initial_click_position = None
        self.selected_building = closest_building
        return True

    def _get_closest_vertex(self, point):
        """Find the closest vertex to the given point."""
        all_vertices = (
            (building, j)
            for building in self.buildings
            for j in range(len(building.vertices))
        )

        return min(
            all_vertices,
            key=lambda x: distance_between_points(x[0].vertices[x[1]][:2], point),
        )

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
            self.patch_manager.remove_temp_drone_start(self.drone_start)
            self.current_drone = None
        # Add a corner to the current building at the click location

        point = Marker((event.xdata, event.ydata), "go").create_marker()

        # self.current_building_points.append(point)
        self.patch_manager.add_building_vertex(point)
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
            # clear all other temporary elements
            self.patch_manager.clear_building_vertices()
            self.current_drone = Drone(
                ID=f"V{len(self.drones)}", position=None, goal=None
            )
            self.current_drone.position = [event.xdata, event.ydata, 0.5]

            self.drone_start = Marker(
                self.current_drone.position[:2], style="ko"
            ).create_marker()
            self.patch_manager.add_temp_drone_start(self.drone_start)
            self.update()
        else:
            # drone initial position is already defined, now add the destination (goal)
            # This is the goal position of the drone
            self.current_drone.goal = [event.xdata, event.ydata, 0.5]

            self.drones.append(self.current_drone)
            self.actions_stack.add_action("drone", self.current_drone)
            self.patch_manager.remove_temp_drone_start(self.drone_start)
            self.drone_start = None


            # add drone patch to patch_manager
            self.patch_manager.add_drone_patch(self.current_drone)
            self.current_drone = None
            self.update()
        return None

    def add_new_vertex(self, event) -> bool:
        for building in self.buildings:
            if building.insert_vertex((event.xdata, event.ydata)):
                # Redraw the building if a vertex was added
                self.patch_manager.redraw_building(building)
                self.update()
                return True
        return False

    def handle_deselect(self, event):
        if self.selected_building:
            if not self.selected_building.contains_point([event.xdata, event.ydata]):
                self.selected_building = None
            return True

    def on_click(self, event):
        """
        This method is called when a click is detected on the plot.
        The event object contains information about the click, such as its position.
        You can use this information to add new elements to the plot, such as a new building or a new drone.
        #TODO ORDER MATTERS, events will be handled in the order they are listed in this method"""

        # If clicked outside of the plot, do nothing
        # if not event.xdata or not event.ydata:
        #     return
        if event.inaxes != self.ax:
            return

        # handle moving building vertices
        if self.handle_vertex_movement(event):
            return

        # add a new vertex if near a building edge and allow moving it around with the mouse...
        # by calling the vertex movement handler again
        if self.add_new_vertex(event):
            self.handle_vertex_movement(event)
            return

        # if a building is selected and we click outside of it, it is deselected (but nothing else happens)
        if self.handle_deselect(event):
            return

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
        print("picked")
        # Check if the picked artist is a Polygon (optional but can be useful)
        if not isinstance(event.artist, plt.Polygon):
            print("early return")
            return
        # polygon = event.artist
        building = self.patch_manager.get_building_from_patch(event.artist)
        self.selected_building = building


        self.initial_click_position = [event.mouseevent.xdata, event.mouseevent.ydata]


    def on_mouse_move(self, event):

        # check to make sure the mouse is still in the main axes 
        # and not over a button or other axes object
        # or outside the axes altogether
        if event.inaxes != self.ax:
            return

        point = [event.xdata, event.ydata]

        ##########################################################################################
        # move the vertex if one is selected
        if self.selected_building is not None and self.selected_vertex is not None:
            # # move the relevent vertex
            self.selected_building.move_vertex(self.selected_vertex, point)
            self.patch_manager.redraw_building(self.selected_building)

            self.update()  # Redraw to show the moved vertex

        ###########################################################################################
        # move the whole building patch
        elif self.selected_building and self.initial_click_position:
            ds = np.array(point) - np.array(self.initial_click_position)
            # Move the building
            # set the vertices of the src.Building object, then copy them into the building patch
            self.selected_building.move_building(ds)
            self.patch_manager.redraw_building(self.selected_building)
            # self.building_patches[self.selected_building].update_visual()
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
            # This will redraw the drone starting or ending point in its new position
            self.patch_manager.redraw_drone(self.selected_drone)

            self.update()  

    def on_button_release(self, event):
        self.initial_click_position = None
        self.selected_drone = None
        self.dragging_drone_point = None
        self.selected_vertex = None

    def delete_selected_building(self):
        if self.selected_building:
            self.actions_stack.remove_action("building", self.selected_building)
            building = self.selected_building
            self.selected_building = None
            self.patch_manager.remove_building_patch(building)
            self.buildings.remove(building)
            self.update()

    def on_key_press(self, event):
        # switch between building and drone placement modes
        self.switch_mode(event)

        if (
            event.key == "tab"
            and self.mode == "building"
        ):
            # plot the building
            self.finalize_building()

        if event.key == "cmd+z":
            self.undo_last_action()

        elif event.key == "backspace":
            self.delete_selected_building()

        elif event.key == "escape":
            self.clear_temp_elements()

        elif event.key == "enter":

            self.run()

    def run(self):
        case = generate_case(
                name="Test Case", buildings=self.buildings, drones=self.drones
            )
        run_case(case)

    def update(self):
        # draw the canvas again
        self.fig.canvas.draw()

    def clear_temp_elements(self):

        self.patch_manager.clear_temp_drone_starts()
        self.patch_manager.clear_building_vertices()

        self.current_drone = None
        self.update()

    def undo_last_action(self):
        if not self.actions_stack.actions:
            return

        action, obj = self.actions_stack.retrieve_last_action()
        if action == "building":
            self.selected_building = None
            self.patch_manager.remove_building_patch(obj)

            self.buildings.remove(obj)

        elif action == "drone":
            if obj in self.drones:
                self.drones.remove(obj)
                self.patch_manager.remove_drone_patch(obj)

        self.update()

    def switch_mode(self, event):
        """
        Switch between building and drone placement modes
        """
        if event.key == "d":
            self.mode = "drone"
        elif event.key == "b":
            self.mode = "building"
    
    def toggle_mode(self):
        if self.mode == "building":
            self.mode = "drone"
        elif self.mode == "drone":
            self.mode = "building"

    def finalize_building(self):
        building = self.patch_manager.make_building()
        if building:
            # this if statement checks to see if a building was created
            # ie if the vertex number was >=3
            self.buildings.append(building)
            self.actions_stack.add_action("building", building)
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
            0.91,
            instructions,
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        self.fig, self.ax = fig, ax
        return None
    
    def call(self, event: str, *args, **kwargs):
        if event == "build_mode":
            self.toggle_mode()
        elif event == "reset":
            self.reset()
        elif event == "run":
            self.run()

    def reset(self):
        self.selected_building = None
        self.clear_temp_elements()
        # Remove all building and drone patches
        self.patch_manager.clear_all()
       
        # Empty the buildings and drones lists
        self.buildings.clear()
        self.drones.clear()

        # Empty the actions stack
        self.actions_stack.clear()

        # Redraw the plot
        self.ax.figure.canvas.draw()


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
