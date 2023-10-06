import matplotlib.pyplot as plt
import numpy as np
from src.building import Building
from src.vehicle import Vehicle
from src.cases import Case, Cases
from src.arena import ArenaMap
from src.utils.simulation_utils import run_simulation, set_new_attribute
import src.utils.plot_utils as plt_utils
import matplotlib.patches as mpatches


class InteractivePlot:   

    DRONE_CLICK_THRESHOLD = 0.2
    FIG_SIZE = (8, 8)
    AXIS_LIMITS = (-5, 5)

    def __init__(self):
        # Setup the default plot
        self.plot_setup()
        # Define variables 
        self.setup_data()
        # Connect event handlers
        self.connect_event_handlers()
        plt.show()

    def setup_data(self)->None:
        self.buildings = []
        self.drones = []
        self.current_building = []
        self.current_drone = None
        self.mode = 'building'  # 'building', 'drone', or None
        self.current_building_points = []
        self.drone_start = None
        self.building_patches = {}
        self.drone_patches = {}
        self.actions_stack = []  # New line to track the actions

        self.temp_elements = []  # List to store temporary graphical elements.

        self.selected_drone = None
        self.initial_click_position = None
        self.selected_building = None
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

        if not self.buildings:
            return False
        # Flatten list of vertices with their indices
        all_vertices = ((i, j, v) for i, building in enumerate(self.buildings) for j, v in enumerate(building.vertices))
        
        # Find the closest vertex
        closest_building_index, closest_vertex_index, closest_vertex = min(
            all_vertices,
            key=lambda x: np.linalg.norm(np.array([event.xdata, event.ydata]) - x[2][:2])
        )

        # Check if the closest vertex is close enough to be selected
        dist = np.linalg.norm(np.array([event.xdata, event.ydata]) - closest_vertex[:2])
        if dist < 0.2:  # This threshold determines how close the click should be to consider a match
            self.selected_building_index = closest_building_index
            self.selected_vertex = closest_vertex_index
            return True
        return False
    
    def handle_building_movement(self, event)->bool:
        for building in self.buildings:
            if building.contains_point((event.xdata, event.ydata)):
                self.selected_building = building
                self.initial_click_position = (event.xdata, event.ydata)
                return True  # Return True to indicate this handler has processed the click
        return False

    def handle_drone_movement(self,event)->bool:
        # Check if a drone starting or ending point was clicked
        for drone in self.drones:
            start_dist = np.linalg.norm(np.array([event.xdata, event.ydata]) - drone.position[:2])
            end_dist = np.linalg.norm(np.array([event.xdata, event.ydata]) - drone.goal[:2])
            if start_dist < 0.2:  # This threshold determines how close the click should be to consider a match
                self.selected_drone = drone
                self.dragging_drone_point = 'start'
                return True
            elif end_dist < 0.2:
                self.selected_drone = drone
                self.dragging_drone_point = 'end'
                return True
        
        self.selected_drone = None
        self.dragging_drone_point = None
        return False
    
    def handle_building_placement(self,event)->None:
        if self.current_drone:
            self.drone_start.remove()
            self.current_drone = None
        # Add a corner to the current building at the click location

        self.current_building.append([event.xdata, event.ydata,1.2])
        point, = self.ax.plot(event.xdata, event.ydata,'go')
        self.current_building_points.append(point)
        self.update()
        return None

    def handle_drone_placement(self,event)->None:
        # clear any buildings before starting drones
            self.current_building = []
            # Add a drone at the click location
            if self.current_drone is None:
                # initialise the drone
                # what to do when we draw the initial position of the drone
                # This is the initial position of the drone

                self.current_drone = Vehicle(ID=f'V{len(self.drones)}',source_strength=1,imag_source_strength=0.5)
                self.current_drone.Set_Position([event.xdata, event.ydata, 0.5])

                self.drone_start, = self.ax.plot(*self.current_drone.position[:2],'ko')
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
                
    def on_click(self, event):

        # If clicked outside of the plot, do nothing
        if not event.xdata or not event.ydata:
            return
        
        if self.handle_vertex_movement(event):
            return
        # Check if a building was clicked and handle its movement if necessary
        if self.handle_building_movement(event):
            return
        # Check if a drone was clicked and handle its movement if necessary
        if self.handle_drone_movement(event):
            return

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
        if self.selected_building and self.initial_click_position:
            dx = event.xdata - self.initial_click_position[0]
            dy = event.ydata - self.initial_click_position[1]
            
            # Move the building
            # set the vertices of the src.Building object, then copy them into the building patch
            self.selected_building.vertices[:, 0] += dx
            self.selected_building.vertices[:, 1] += dy

            building_patch = self.building_patches[self.selected_building]
            building_patch.set_xy(self.selected_building.vertices[:, :2])
            
            # Update the initial click position for next movement calculation
            self.initial_click_position = (event.xdata, event.ydata)
            
            # Redraw to show the moved building
            self.update()

        if self.selected_building_index is not None and self.selected_vertex is not None:

            building = self.buildings[self.selected_building_index]
            building.vertices[self.selected_vertex, :2] = [event.xdata, event.ydata]
            building_patch = self.building_patches[building]
            
            building_patch.set_xy(building.vertices[:, :2])
            self.update()  # Redraw to show the moved vertex
            
        if self.selected_drone:
            if self.dragging_drone_point == 'start':
                self.selected_drone.position = np.array([event.xdata, event.ydata, 0.5])
            elif self.dragging_drone_point == 'end':
                self.selected_drone.goal = np.array([event.xdata, event.ydata, 0.5])
            
            marker_start, marker_end, arrow = self.drone_patches[self.selected_drone]
            #remove the old ones
            marker_start.remove()
            marker_end.remove()
            arrow.remove()

            d = self.selected_drone
            marker_start, = self.ax.plot(*d.position[:2], 'b*')  # Initial position in blue
            marker_end, = self.ax.plot(*d.goal[:2], 'r*')  # Goal position in red
            # Add an arrow with a line using the 'arrow' function
            arrow = self.ax.arrow(*d.position[:2], d.goal[0]-d.position[0], d.goal[1]-d.position[1], length_includes_head = True, head_width=0.2, head_length=0.2, fc='k', ec='k',linestyle = '-')
            self.drone_patches[d] = (marker_start, marker_end, arrow)
            
            self.update()  # This will redraw the drone starting or ending point in its new position


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
        # elif event.key == 'm':
        #     self.mode = 'move_building'
        elif event.key == 'tab' and self.mode == 'building' and len(self.current_building) >= 3:
            # add the building the self.buildings. The Building class is useful to get the vertices
            building = Building(self.current_building)
            self.buildings.append(building)
            # add the building to the actions stack
            self.actions_stack.append(('building', building))

            # remove the temporary points:
            for point in self.current_building_points:
                point.remove()
            self.current_building_points = []
            # plot the building
            patch = plt.Polygon(
                building.vertices[:,:2],
                edgecolor=(0,0,0,1),      # for example, set border color to Black (R,G,B,A) where A is transparency
                facecolor=(0,0,1,0.5),     # set fill color to blue and alpha to 0.5
                # alpha=0.5,             # make it semi-transparent, applies to whole patch 
                linewidth=2.0 
            )
            self.ax.add_patch(patch)

            # store a reference to the patch so we can remove it later
            self.building_patches[building] = patch  # Store the patch
            self.current_building = []
            # Update the plot
            self.update()

        if event.key == 'cmd+z':
            self.undo_last_action()

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
        c = Case(name = name)
        c.buildings = self.buildings
        c.vehicle_list = self.drones
        generator = Cases(filename='examples/gui_testing.json')
        generator.add_case(c)
        generator.update_json()

        complete_case = generator.get_case('examples/gui_testing.json','Test Case')
        # c.arena = ArenaMap(buildings=self.buildings)
        return complete_case


    def update(self):
        # draw the canvas again
        self.fig.canvas.draw()

    

    def clear_temp_elements(self):
        for elem in self.temp_elements:
            elem.remove()
        self.temp_elements = []  # Clear the list after removing all elements from the plot.
        self.current_building = []
        self.current_drone = None
        self.update()


    def undo_last_action(self):
        if not self.actions_stack:
            return

        action, obj = self.actions_stack.pop()
        if action == 'building':
            if obj in self.buildings:
                self.buildings.remove(obj)
                patch = self.building_patches.pop(obj, None)
                # if patch:
                patch.remove()

        elif action == 'drone':
            if obj in self.drones:
                self.drones.remove(obj)
                marker_start, marker_end, arrow = self.drone_patches.pop(obj, (None,None,None))
                marker_start.remove()
                marker_end.remove()
                arrow.remove()
        # elif action == 'point':
        #     obj.remove()
        #     self.current_building.pop()
        #     self.current_building_points.pop()
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
