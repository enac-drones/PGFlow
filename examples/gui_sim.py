import matplotlib.pyplot as plt
import numpy as np
from src.building import Building
from src.vehicle import Vehicle
from src.cases import Case, Cases
from src.arena import ArenaMap
from src.utils.simulation_utils import run_simulation, set_new_attribute
import src.utils.plot_utils as plt_utils
from matplotlib.patches import Polygon
from typing import List


# Code refactoring stuff below:

# class Entity:
#     """An entity comprised of n nodes in the world space.
#     this can be:
#     flight path (x,y) (x1,y1)
#     building (x,y)... (xn,yn)
    
#     """
#     ...

# class MutableEntity:
#     """Responsible for adding or removing nodes of an Entity"""


# class MoveableMixin():
#     """Responsible for moving an Entity in the world space"""
#     ...


# class DronePath(Entity,MoveableMixin):
#     ...


# class Polygon(Entity,MoveableMixin,MutableEntity):
#     ...


class InteractivePlot:   

    DRONE_CLICK_THRESHOLD = 0.2
    FIG_SIZE = (8, 8)
    AXIS_LIMITS = (-5, 5)


    def __init__(self):
        self._selected_building:Polygon = None
        self.original_colors:dict = {}
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
    def selected_building(self, patch):
        # If we're deselecting (setting to None), revert the color.
        if patch is None and self.selected_building is not None:
            orig_colors = self.original_colors.get(self._selected_building, {})
            self._selected_building.set_facecolor(orig_colors.get("facecolor", "default_face_color"))
            self._selected_building.set_edgecolor(orig_colors.get("edgecolor", "default_edge_color"))
            # Remove from the dictionary
            del self.original_colors[self._selected_building]

        # If we're selecting a new building, store its original colors and then change them.
        elif patch is not None:
            self.original_colors[patch] = {
                "facecolor": patch.get_facecolor(),
                "edgecolor": patch.get_edgecolor(),
            }
            
            # patch.set_facecolor((0.678, 0.847, 0.902, 0.7)) #Lightblue
            patch.set_facecolor((1,0.4,1, 0.7)) #Transparent red

            patch.set_edgecolor("black")

        # Set the actual value
        self._selected_building = patch
        self.update()

    def setup_data(self)->None:
        self.buildings = []
        self.drones = []
        self.current_drone = None
        self.mode = 'building'  # 'building', 'drone', or None
        self.current_building_points = []
        self.drone_start = None
        self.building_patches:List[Polygon] = []
        self.drone_patches = {}
        self.actions_stack = []  # New line to track the actions

        self.temp_elements = []  # List to store temporary graphical elements.

        self.selected_drone = None
        self.initial_click_position = None
        # self.selected_building = None
        self.selected_building_index = None
        self.selected_vertex = None

        return None
    
    def connect_event_handlers(self)->None:

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_button_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        return None
    
    def handle_vertex_movement(self,event):

        if not self.building_patches:
            return False
        # Flatten list of vertices with their indices (make a generator object)
        all_vertices = ((building, j, v) for i, building in enumerate(self.building_patches) for j, v in enumerate(building.get_xy()))
        # Find the closest vertex
        closest_building, closest_vertex_index, closest_vertex = min(
            all_vertices,
            key=lambda x: np.linalg.norm(np.array([event.xdata, event.ydata]) - x[2][:2])
        )

        # Check if the closest vertex is close enough to be selected
        dist = np.linalg.norm(np.array([event.xdata, event.ydata]) - closest_vertex[:2])
        if not dist < 0.2:  # This threshold determines how close the click should be to consider a match
            return False
        # self.selected_building_index = closest_building_index
        self.selected_vertex = closest_vertex_index
        self.selected_building = closest_building


        return True
    
    def handle_building_movement(self, event)->bool:
        for building in self.building_patches:
            # test = Building(np.hstack((building.get_xy(),np.zeros((building.get_xy().shape[0], 1)))))
            # BUG Create a new temporary polygon to use the contains_point() method due to the bug #27026
            temp_building = Polygon(building.get_xy())
            if temp_building.contains_point([event.xdata, event.ydata], radius = 0): 
                #BUG contains_point() only works if transparency of polygon set to zero, see matplotlib github issue #27026 
                #BUG apparently setting the radius of contains_point() to zero fixes the issue. Not in this case for some reason
                self.selected_building = building
                self.initial_click_position = (event.xdata, event.ydata)
                return True  # Return True to indicate this handler has processed the click
        self.selected_building = None
        return False

    def handle_drone_movement(self,event)->bool:
        # Check if a drone starting or ending point was clicked
        point = [event.xdata, event.ydata]
        for drone in self.drones:
            start_dist = np.linalg.norm(np.array(point) - drone.position[:2])
            end_dist = np.linalg.norm(np.array(point) - drone.goal[:2])
            if start_dist < 0.2:  # This threshold determines how close the click should be to consider a match
                self.selected_drone = drone
                self.dragging_drone_point = 'start'
                return True
            elif end_dist < 0.2:
                self.selected_drone = drone
                self.dragging_drone_point = 'end'
                return True
            
             # Check if the click is on the arrow connecting the drone start and end points
            marker_start, marker_end, arrow = self.drone_patches[drone]
            p0, p1 = np.array(marker_start.get_data()).flatten(), np.array(marker_end.get_data()).flatten() # Assuming your arrow has these methods
            if self.click_near_arrow(p0, p1, event, threshold=0.2):
                self.selected_drone = drone
                self.dragging_drone_point = 'arrow'
                self.initial_click_position = point
                return True
        
        self.selected_drone = None
        self.dragging_drone_point = None
        return False
    
    def handle_building_placement(self,event)->None:
        if self.current_drone:
            self.drone_start.remove()
            self.current_drone = None
        # Add a corner to the current building at the click location

        point, = self.ax.plot(event.xdata, event.ydata,'go')
        self.current_building_points.append(point)
        self.update()
        return None

    def handle_drone_placement(self,event)->None:
        # clear any buildings before starting drones
            # Add a drone at the click location
            if self.current_drone is None:
                # initialise the drone
                # what to do when we draw the initial position of the drone
                # This is the initial position of the drone

                self.current_drone = Vehicle(ID=f'V{len(self.drones)}',source_strength=1,imag_source_strength=0.5)
                self.current_drone.Set_Position([event.xdata, event.ydata, 0.5])

                self.drone_start, = self.ax.plot(*self.current_drone.position[:2],'ko')
                self.temp_elements.append(self.drone_start)
                self.update()
            else:
                # drone initial position is already defined, now add the destination (goal)
                # This is the goal position of the drone

                self.current_drone.Set_Goal(goal=[event.xdata, event.ydata,0.5], goal_strength=5, safety=None)
                self.current_drone.Go_to_Goal(
                    altitude=0.5, AoAsgn=0, t_start=0, Vinfmag=0
                )  # FIXME add these to the json
                self.drones.append(self.current_drone)
                self.actions_stack.append(('drone', self.current_drone))
                self.drone_start.remove()
                self.drone_start = None
                
                d = self.current_drone

                # plot the arrow 
                marker_start, = self.ax.plot(*d.position[:2], 'b*')  # Initial position in blue
                marker_end, = self.ax.plot(*d.goal[:2], 'r*')  # Goal position in red
                # Add an arrow with a line using the 'arrow' function
                arrow = self.ax.arrow(*d.position[:2], d.goal[0]-d.position[0], d.goal[1]-d.position[1], length_includes_head = True, head_width=0.2, head_length=0.2, fc='k', ec='k',linestyle = '-')
                self.drone_patches[d] = (marker_start, marker_end, arrow)
                
                self.current_drone = None
                self.update()
            return None
    
    def click_near_arrow(self, p0, p1, event, threshold=0.2):
        click_position = np.array([event.xdata, event.ydata])
        
        dist_start = np.linalg.norm(click_position - p0)
        dist_end = np.linalg.norm(click_position - p1)
        arrow_length = np.linalg.norm(p1-p0)
        
        # Using Heron's formula to compute area of triangle formed by start, end, and click points
        s = (dist_start + dist_end + arrow_length) / 2
        triangle_area = np.sqrt(s * (s - dist_start) * (s - dist_end) * (s - arrow_length))
        
        # Distance from click to the line segment
        distance_to_line = 2 * triangle_area / arrow_length

        # Calculate projection of click point onto the arrow line segment
        dot_product = np.dot(p1 - p0, click_position - p0) / arrow_length**2
        projected_point = p0 + dot_product * (p1 - p0)

        # Check if the projected point lies between start and end
        is_within_segment = np.all(np.minimum(p0, p1) <= projected_point) and np.all(projected_point <= np.maximum(p0, p1))
        
        if distance_to_line < threshold and is_within_segment:
            return True

        return False


                
    def on_click(self, event):
        #ORDER MATTERS

        # If clicked outside of the plot, do nothing
        if not event.xdata or not event.ydata:
            return
        
        # handle moving building vertices
        if self.handle_vertex_movement(event):
            return
        # Check if a drone was clicked and handle its movement if necessary
        if self.handle_drone_movement(event):
            return
        # Check if a building was clicked and handle its movement if necessary
        if self.handle_building_movement(event):
            return
        

        # if self.click_near_arrow(event):
        #     return
        
        # Proceed with building placement
        if self.mode == 'building':
            self.handle_building_placement(event)
            return
        
        # Proceed with drone placement
        elif self.mode == 'drone':
            self.handle_drone_placement(event)
            return
            
        # Update the plot
        self.update()

    def on_mouse_move(self, event):

        point = [event.xdata, event.ydata]

        #If the point is out of the map area, skip the rest of this method
        if any(not isinstance(item, (int, float)) for item in point):
            return
        
        if self.selected_building and self.initial_click_position:
            ds = np.array(point) - np.array(self.initial_click_position)
            # Move the building
            # set the vertices of the src.Building object, then copy them into the building patch
            self.selected_building.get_xy()[:, :2] += ds
            
            # Update the initial click position for next movement calculation
            self.initial_click_position = point
            
            # Redraw to show the moved building
            self.update()

        if self.selected_building is not None and self.selected_vertex is not None:
            # move the relevent vertex
            # If the selected vertex is the first or last of the polygon, move both first and last 
            last_vertex_index = len(self.selected_building.get_xy()) - 1
            if self.selected_vertex == 0 or self.selected_vertex == last_vertex_index:
                # Move the first vertex
                self.selected_building.get_xy()[0] = point
                # Move the last vertex
                self.selected_building.get_xy()[-1] = point
            else:
                # Move any other vertex
                self.selected_building.get_xy()[self.selected_vertex] = point

            self.update()  # Redraw to show the moved vertex
            
        if self.selected_drone:
            if self.dragging_drone_point == 'start':
                self.selected_drone.position = np.array([event.xdata, event.ydata, 0.5])
            elif self.dragging_drone_point == 'end':
                self.selected_drone.goal = np.array([event.xdata, event.ydata, 0.5])
            elif self.dragging_drone_point == 'arrow':
                # Move both start and end points, and update all corresponding patches
                ds = np.array(point) - np.array(self.initial_click_position)
                self.selected_drone.position[:2] += ds
                self.selected_drone.goal[:2] += ds

            self.initial_click_position = point
            marker_start, marker_end, arrow = self.drone_patches[self.selected_drone]
            d = self.selected_drone
            # marker_start.set(xdata = d.position[0], ydata = d.position[1])
            marker_start.set_xdata([d.position[0]])
            marker_start.set_ydata([d.position[1]]) 
            # marker_end.set(xdata = d.goal[0], ydata = d.goal[1])
            marker_end.set_xdata([d.goal[0]])
            marker_end.set_ydata([d.goal[1]]) 
            # arrow.set_positions(d.position[:2], d.goal[:2])
            self.update_arrow_position(arrow,d.position[:2],d.goal[:2])
            # arrow.posA = *d.position[:2]

            
            marker_start, marker_end, arrow = self.drone_patches[self.selected_drone]
            #remove the old ones
            # marker_start.remove()
            # marker_end.remove()
            # arrow.remove()

            # marker_start, = self.ax.plot(*d.position[:2], 'b*')  # Initial position in blue
            # marker_end, = self.ax.plot(*d.goal[:2], 'r*')  # Goal position in red
            # Add an arrow with a line using the 'arrow' function
            # arrow = self.ax.arrow(*d.position[:2], d.goal[0]-d.position[0], d.goal[1]-d.position[1], length_includes_head = True, head_width=0.2, head_length=0.2, fc='k', ec='k',linestyle = '-')
            self.drone_patches[d] = (marker_start, marker_end, arrow)
            
            self.update()  # This will redraw the drone starting or ending point in its new position

    def update_arrow_position(self, arrow, new_start:tuple, new_end:tuple):
        new_x_start, new_y_start = new_start
        new_x_end, new_y_end = new_end

        dx = new_x_end - new_x_start
        dy = new_y_end - new_y_start
        
        arrow.set_data(x=new_x_start, y=new_y_start, dx=dx, dy=dy)

    def on_button_release(self, event):
        self.selected_building = None
        self.initial_click_position = None
        self.selected_drone = None
        self.dragging_drone_point = None
        self.selected_building_index = None
        self.selected_vertex = None

    def on_key_press(self, event):
        if event.key == 'd':
            self.mode = 'drone'
        elif event.key == 'b':
            self.mode = 'building'
        elif event.key == 'tab' and self.mode == 'building' and len(self.current_building_points) >= 3:
        
            # plot the building
            vertices = np.array([point.get_xydata() for point in self.current_building_points])
            vertices = vertices.squeeze(axis=1)
            patch = Polygon(
                vertices,  # x,y coordinates of the vertices
                edgecolor=(0,0,0,1),      # Set border color to Black (R,G,B,A) where A is transparency
                facecolor=(0,0,1,0.5),     # set fill color to blue and alpha to 0.5
                # alpha=0.5,             # make it semi-transparent, applies to whole patch 
                closed=True,
                linewidth=2.0 
            )
            self.actions_stack.append(('building', patch))


            self.ax.add_patch(patch)

            # store a reference to the patch so we can remove it later
            self.building_patches.append(patch)# Store the patch
            # remove the temporary points:
            for point in self.current_building_points:
                point.remove()
            self.current_building_points = []
            # Update the plot
            self.update()

        if event.key == 'cmd+z':
            self.undo_last_action()
        
        elif event.key == "escape":
            self.clear_temp_elements()

        elif event.key == 'enter':
            my_case = self.generate_case(name = "Test Case")
            result = run_simulation(
                my_case,
                t=2000,
                update_every=1,
                stop_at_collision=False,
                max_avoidance_distance=3,
            )
            # plt.close()
            asdf = plt_utils.PlotTrajectories(my_case, update_every=50)
            asdf.show()
        # self.clear_temp_elements()

    def generate_case(self,name):
        height = 1.2
        # this line adds a third dimension to the x,y coordinates of the building patches and creates a building object from each patch
        buildings = [Building(np.hstack([patch.get_xy()[:-1], np.full((patch.get_xy()[:-1].shape[0], 1), height)])) for patch in self.building_patches]


        # buildings = [Building(patch.get_xy()) for patch in self.building_patches]
        c = Case(name = name)
        c.buildings = buildings
        c.vehicle_list = self.drones
        generator = Cases(filename='examples/gui_testing.json')
        generator.add_case(c)
        generator.update_json()

        complete_case = generator.get_case('examples/gui_testing.json','Test Case')
        return complete_case


    def update(self):
        # draw the canvas again
        self.fig.canvas.draw()

    

    def clear_temp_elements(self):
        for elem in self.temp_elements:
            elem.remove()
        for point in self.current_building_points:
            point.remove()
        self.temp_elements = []  # Clear the list after removing all elements from the plot.
        self.current_building_points = []
        self.current_drone = None
        self.update()


    def undo_last_action(self):
        if not self.actions_stack:
            return

        action, obj = self.actions_stack.pop()
        if action == 'building':
            # if obj in self.building_patches:
            obj.remove()
            self.building_patches.remove(obj)
            # patch = self.building_patches.pop(obj)
            # if patch:

        elif action == 'drone':
            if obj in self.drones:
                self.drones.remove(obj)
                marker_start, marker_end, arrow = self.drone_patches.pop(obj, (None,None,None))
                marker_start.remove()
                marker_end.remove()
                arrow.remove()

        self.fig.canvas.draw()  # Redraw the figure to reflect changes
        # self.update()



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
            "'b': switch to building mode, click to place vertices of building\n"
            "Tab: complete a building, \n"
            "'d': switch to drone mode, "
            "Enter: run the simulation"
        )

        fig.text(0.2, 0.93, instructions, fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        self.fig, self.ax = fig, ax
        return None

# Example usage:
plot = InteractivePlot()
plot.switch_to_building_mode()
print("done")
# The user can now click on the plot to place buildings





# Suggestions:
# Save arena, just buildings, just drones etc
# better instructions
# vectors showing output of panel flow for each drone
# dragging buildings
# changing drone with click and drag
# change drone parameters such as source strength, imaginary source strength, goal strength, goal safety etc
# cooperating or not (can turn on and off for each drone)



