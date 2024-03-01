import sys
sys.path.append('../')
# import matplotlib
# matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np

# Import animation package
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes

# Import slider package
from matplotlib.widgets import Slider, Button
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors

from typing import List
from gflow.vehicle import Vehicle
from gflow.cases import Case

from typing import Iterable


############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################



class PlotTrajectories:
    """Same as above but trying to use the FuncAnimation for the play button implementation which supposedly uses less CPU"""

    FIG_SIZE = (8, 8)
    AXIS_LIMITS = (-5, 5)
    # arrival_distance = 0.2
    FRAMES = np.linspace(0, 1, 101)
    SLIDER_ANIMATION_INTERVAL = FRAMES[1]-FRAMES[0]
    UPDATE_INTERVAL = 50
    BUILDING_EDGE_COLOUR = "black"
    BUILDING_FILL_COLOUR = "darkgray"
    BUILDING_INFLATED_EDGE_COLOUR = "b"
    BUILDING_INFLATED_FILL_COLOUR = "k"

    def __init__(self, case: Case, update_every: int):
        self.case = case
        self.Arena = case.arena
        self.ArenaR = case.arena
        self.arrival_distance = case.arrival_distance
        self.animation_proportion:float = 0 #proportion of animation completed according to frames ie 9/100 frames = 0.09
        self.modified_artists:set = set()

        self.vehicle_list = case.vehicle_list
        self.case_name = case.name
        self.update_every = update_every
        # plt.close('all')
        self.fig, self.ax = self.plot_setup()
        self.slider = self.create_slider(fig=self.fig)
        self.play_button = self.create_button(fig=self.fig)
        self.info_box = self.create_info_box(ax=self.ax)
        # self.case_name = self.show_case_name(ax=self.ax)
        self.plot_buildings(ax=self.ax, Arena=self.Arena, ArenaR=self.ArenaR)
        self.time_steps_max = self.get_max_timesteps(self.vehicle_list)

        # plot_list is a list that will hold the references to each trajectory plot
        self.plot_list = []
        # list to store (the references to) the drone icon plots
        self.drone_list = []
        # same as above, but display these only when certain separation minima are not respected
        self.warning_circles = []
        self.arrows = []
        self.connecting_lines:dict[tuple, Line2D] = {}
        # initialize empty array to store vehicle positions
        self.positions = np.zeros((len(self.vehicle_list), 3))
        self.initial_plot(vehicle_list=self.vehicle_list, ax=self.ax)

        # this variable will increase by 1 every time a collision is detected
        self.conflict_iterator = 0
        self.conflicts = {}
        self.conflicts["addressed"] = []
        # create new set to hold the conflicts that have already caused the simulation to pause:
        # addressed_conflicts = set()
        # connect the action of pressing the spacebar to the result we want it to have
        self.fig.canvas.mpl_connect("key_press_event", self.on_press)
        # Create the animation object, it starts automatically against my will. BUG? Unlikely...
        self.anim = FuncAnimation(
            self.fig,
            self.animate,
            interval=self.UPDATE_INTERVAL, # delay between frames in ms
            frames=self.FRAMES,
            init_func=None,
            blit=False,
            repeat=True, # whether to repeat the animation after the end 
            repeat_delay=1000, # delay between repeats in ms #BUG doesn't seem to delay at all
        )

        # tell the slider to update the plot when it is moved
        self.slider.on_changed(self.update)
        # self.slider.on_changed(self.animate)

        # call the play function when the button is pressed (to play or pause the animation)
        self.play_button.on_clicked(self.play)

        # again this line updates the plot, without it, the animation starts by default even though we have anim.event_source.stop()
        # perhaps there is a better way of doing this that I am not aware of.
        # plt.pause(0.1)
        # the line below also appears to do the trick, and better
        self.fig.canvas.draw()
        # self.fig.canvas.flush_events()


        # these three lines are a bit of a hack to stop the simulation which for some reason automatically starts BUG
        self.animation_running = True
        self.play(event=None)
        self.slider.set_val(0.0)

    def update(self, val):
        # return
        # val self.slider.val is the same as val
        # print(f"{val=}")
        # print(self.time_steps_max)
        plot_until = int(np.floor(val * self.time_steps_max))
        # self.modified_artists = []
        self.update_plot(plot_until)
        self.update_drone_positions(plot_until)
        self.update_warning_circles(plot_until)
        self.update_arrows(plot_until)

        #limit plot_until to the max timesteps-1 to avoid index errors at the end. 
        plot_until = min(plot_until, self.time_steps_max - 1)
        self.handle_connecting_lines(plot_until)
        self.collision_handling()
        # self.animation_proportion = val


    def animate(self, i):
        """Function that updates the slider and calls the update function. i is the FRAMES argument"""
        # obtain the slider value to 2dp
        # self.fig.canvas.flush_events()
        self.modified_artists.clear()
        current_slider_value = round(self.slider.val, 2)
        # print(f"{self.slider.val=}")
        # set i to the slider value so that the simulation stops when the slider reaches the end
        # it is 100x the slider value because the slider goes from 0 to 1 and the i from 0 to 99
        #FIXME need better logic to set the frame number to where the slider is 
        # (with the current implementation, frame number can not be changed easily)
        self.slider.set_val(
            (current_slider_value + self.SLIDER_ANIMATION_INTERVAL)
            % (self.slider.valmax + self.SLIDER_ANIMATION_INTERVAL)
        )        
        i = self.slider.val

        
        # stop the animation when the slider reaches the end
        #NOTE this can be done by setting repeat=False in FuncAnimation but then we wouldn't have access to the button to restart it
        if i == self.FRAMES[-1]:
            # calling the play function while the animation is running stops the animation
            self.play(event=None)

        # if blit=True, need to return the sequence of artists that need updating

        return tuple(self.modified_artists)

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
        return fig, ax

    def create_slider(self, fig):
        # Create axes for sliders
        # variable inside add_axes is left, bottom, width, height
        ax_prog = fig.add_axes([0.3, 0.92, 0.4, 0.05])
        ax_prog.spines["top"].set_visible(True)
        ax_prog.spines["right"].set_visible(True)

        # Create slider object to iterate through the plot
        slider = Slider(
            ax=ax_prog,
            label="Progress ",
            valinit=0.0,
            valstep=self.SLIDER_ANIMATION_INTERVAL/10,
            valmin=0,
            valmax=1.0,
            valfmt=" %1.1f ",
            facecolor="#cc7000",
        )
        return slider

    def create_button(self, fig):
        # create the play button axis object
        play_ax = fig.add_axes([0.8, 0.92, 0.1, 0.05])
        # create a play button at the location of the axis object
        play_button = Button(play_ax, "Play", color="0.8", hovercolor="0.95")
        return play_button

    def create_info_box(self, ax):
        # these are matplotlib.patch.Patch properties
        bounding_box = dict(boxstyle="round", facecolor="wheat", edgecolor="g", alpha=1)
        textstr = "Safe"
        # place a text box in upper left in axes coords
        info_box = ax.text(
            0.05,
            0.95,
            textstr,
            transform=ax.transAxes,
            fontsize=14,
            verticalalignment="top",
            bbox=bounding_box,
            color="g",
        )
        return info_box

    def show_case_name(self, ax):
        # these are matplotlib.patch.Patch properties
        bounding_box = dict(boxstyle="round", facecolor="wheat", edgecolor="g", alpha=1)
        textstr = self.case_name
        # place a text box in upper left in axes coords
        info_box = ax.text(
            0.5,
            0.95,
            textstr,
            transform=ax.transAxes,
            fontsize=14,
            verticalalignment="top",
            bbox=bounding_box,
            color="g",
        )
        return info_box

    def plot_buildings(self, ax, Arena, ArenaR):
        for building in Arena.buildings:
            ax.plot(
                np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
                np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
                self.BUILDING_EDGE_COLOUR,
                alpha=1,
            )
            ax.fill(
                np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
                np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
                self.BUILDING_FILL_COLOUR,
                alpha=1,
            )
        for buildingR in ArenaR.buildings:
            ax.plot(
                np.hstack((buildingR.vertices[:, 0], buildingR.vertices[0, 0])),
                np.hstack((buildingR.vertices[:, 1], buildingR.vertices[0, 1])),
                self.BUILDING_INFLATED_EDGE_COLOUR,
                alpha=0,
            )
            ax.fill(
                np.hstack((buildingR.vertices[:, 0], buildingR.vertices[0, 0])),
                np.hstack((buildingR.vertices[:, 1], buildingR.vertices[0, 1])),
                self.BUILDING_INFLATED_FILL_COLOUR,
                alpha=0
            )
        return None

    def get_max_timesteps(self, vehicle_list):
        # these few lines obtain the maximum length of any path for all the drones, aka the time taken for the last drone to reach its destination
        # maybe there's a neater way of doing this but it isn't computationally expensive so for now it's fine
        # max_timesteps stores the maximum amount of timesteps for any drone to reach its destination. time_steps_max*dt = t_max
        max_timesteps = max(len(vehicle.path[:, 0]) for vehicle in vehicle_list)
        return max_timesteps

    def initial_plot(self, vehicle_list:list[Vehicle], ax:Axes):
        for v_idx, vehicle in enumerate(vehicle_list):
            # define the current coordinates of the drone
            x, y, z = (
                vehicle_list[v_idx].path[-1, 0],
                vehicle_list[v_idx].path[-1, 1],
                vehicle_list[v_idx].path[-1, 2],
            )
            self.positions[v_idx] = [x, y, z]
            # Plot default data
            # note that the comma operator is mandatory, it turns the ax.plot object into a tuple
            (drone_path,) = ax.plot(
                vehicle_list[v_idx].path[: self.time_steps_max, 0],
                vehicle_list[v_idx].path[: self.time_steps_max, 1],
                linewidth=2,
            )
            # the line below is for adding an icon to the current vehicle position
            # the 'x' at the end is the position marker, can be changed to other things
            (drone_icon,) = ax.plot(x, y, "x")

            # plot the default warning circles
            # define the circle
            warning_circle = plt.Circle(
                (x, y),
                self.case.collision_threshold / 2,
                fill=False,
                edgecolor="k",
                linewidth=2,
            )
            # add the circle to the plot
            ax.add_artist(warning_circle)
            # print(*vehicle.desired_vectors[0])

            gflow_output_arrow = ax.arrow(x,y,*vehicle.desired_vectors[0],width=0.5)

            # ax.add_artist(gflow_output_arrow)
            self.arrows.append(gflow_output_arrow)

            self.warning_circles.append(warning_circle)

            self.plot_list.append(drone_path)
            # append the references to the drone icons to the drone icon list
            self.drone_list.append(drone_icon)
            # the following two lines plot the start and end points
            ax.plot(vehicle_list[v_idx].path[0, 0], vehicle_list[v_idx].path[0, 1], "")
            ax.plot(vehicle_list[v_idx].goal[0], vehicle_list[v_idx].goal[1], "*")
        return None

    

    def update_plot(self, plot_until):
        
        for i in range(len(self.plot_list)):
            self.plot_list[i].set_data(
                self.vehicle_list[i].path[:plot_until, 0],
                self.vehicle_list[i].path[:plot_until, 1],
            )
            self.plot_list[i].set_data(
                self.vehicle_list[i].path[:plot_until, 0],
                self.vehicle_list[i].path[:plot_until, 1],
            )
            # self.modified_artists.add(self.plot_list[i])


    def update_drone_positions(self, plot_until):
        for i in range(len(self.drone_list)):
            if plot_until == 0:
                x, y, z = self.vehicle_list[i].path[0, :3]
            elif plot_until < len(self.vehicle_list[i].path[:, 0]):
                x, y, z = self.vehicle_list[i].path[plot_until - 1, :3]
            else:
                x, y, z = self.vehicle_list[i].path[-1, :3]
            self.drone_list[i].set_data(x, y)
            # self.modified_artists.add(self.drone_list[i])
            self.positions[i] = [x, y, z]

    def update_arrows(self, plot_until):
        for i in range(len(self.drone_list)):
            if plot_until == 0:
                x, y, z = self.vehicle_list[i].path[0, :3]
            elif plot_until < len(self.vehicle_list[i].path[:, 0]):
                x, y, z = self.vehicle_list[i].path[plot_until - 1, :3]
            else:
                x, y, z = self.vehicle_list[i].path[-1, :3]
            
            try:
                [dx,dy] = self.vehicle_list[i].desired_vectors[plot_until]
            except IndexError:
                [dx,dy] = self.vehicle_list[i].desired_vectors[-1]
            self.arrows[i].set_data(x=x, y=y, dx=dx,dy=dy,width=0.1)
            # try:    
            #     # print(f"{plot_until=}")
            #     prin
            #     [dx,dy] = self.vehicle_list[i].desired_vectors[plot_until]
            # except IndexError:
            #     # print('wazaaa')
            #     [dx,dy] = self.vehicle_list[i].desired_vectors[-1]

            #     self.arrows[i].set_data(x=x, y=y, dx=dx,dy=dy,width=0.1)
            # # self.modified_artists.add(self.drone_list[i])
            # # self.positions[i] = [x, y, z]

    def update_warning_circles(self, plot_until):
        for i in range(len(self.warning_circles)):
            #start of simulation
            if plot_until == 0:
                self.warning_circles[i].set_edgecolor("k")
                # print(dir(self.warning_circles[i]),self.warning_circles[i].get_edgecolor())
            #during simulation
            elif plot_until < len(self.vehicle_list[i].path[:, 0]):
                self.warning_circles[i].set_fill(False)
                #show communication for up to 5 timesteps NOTE (or frames?) after the actual update so it flashes for longer
                # FIXME this is a terrible way to do things lol
                show_communication = plot_until % self.update_every in range(5)
                if show_communication:
                    self.warning_circles[i].set_edgecolor("g")
                    self.warning_circles[i].set_fill(True)
                    self.warning_circles[i].set_facecolor("lightblue")
                else:
                    self.warning_circles[i].set_edgecolor("gray")
                    self.warning_circles[i].set_fill(False)
            #At the end of the simulation
            else:
                self.warning_circles[i].set_fill(True)
                self.warning_circles[i].set_edgecolor("b")
                self.warning_circles[i].set_facecolor("skyblue")
            self.warning_circles[i].center = self.positions[i][:2]

            self.modified_artists.add(self.warning_circles[i])

    def collision_handling(self):
        """Handle collisions and update display accordingly."""
        distance_matrix = self.calculate_distance_matrix()

        for i in range(distance_matrix.shape[0]):
            # Skip drones that have reached their goals
            if self.has_reached_goal(i):
                continue

            for j in range(i + 1, distance_matrix.shape[1]):
                # Skip drones that have reached their goals
                if self.has_reached_goal(j):
                    continue

                if self.is_collision(i, j, distance_matrix):
                    self.handle_collision(i, j)

        self.update_info_box()

    def handle_connecting_lines(self, plot_until):
        """Draw lines connecting drones if close enough and update display accordingly.
        This method duplicates collision_handling and is just a rapid prototype"""
        distance_matrix = self.calculate_distance_matrix()

        for id in list(self.connecting_lines.keys()):
            line = self.connecting_lines[id]
            line.remove()
            del self.connecting_lines[id]

        for i in range(distance_matrix.shape[0]):
            # Skip drones that have reached their goals
            if self.has_reached_goal(i):
                continue

            for j in range(i + 1, distance_matrix.shape[1]):
                # Skip drones that have reached their goals

                if self.has_reached_goal(j):
                    continue

                if distance_matrix[i, j] < self.case.max_avoidance_distance:
                    x_values = [self.vehicle_list[i].path[plot_until, 0], self.vehicle_list[j].path[plot_until, 0]]
                    y_values = [self.vehicle_list[i].path[plot_until, 1], self.vehicle_list[j].path[plot_until, 1]]
                    distance = distance_matrix[i, j]
                    max_distance = self.case.max_avoidance_distance
                    p = 1 - distance/max_distance # 1 at no distance, 0 and max_distance

                    max_linewidth = 4
                    # Create a colormap that transitions from green to red
                    # cmap = plt.cm.RdYlGn_r  # 'RdYlGn_r' is the reversed Red-Yellow-Green colormap
                    # cmap = plt.cm.Reds_r # Red black map

                    # Normalize the distance value to range [0, 1]
                    # norm = mcolors.Normalize(vmin=0, vmax=max_distance)
                    # p_adjusted = p**2  # Adjust this power for desired transition. Higher values will make it red sooner.
                    # color_value = cmap(norm(distance))
                    # color_value = cmap(p_adjusted)
                    #not using colour for now, but could be interesting
                    line = self.ax.plot(x_values, y_values, 'k-', alpha = p, lw = p * max_linewidth )[0]  # 'k-' specifies a black line
                    self.connecting_lines[(i,j)] = line  # 'k-' specifies a black line



    def calculate_distance_matrix(self):
        """Calculate the Euclidean distance matrix between drones."""
        return np.sqrt(
            np.sum((self.positions[:, np.newaxis] - self.positions) ** 2, axis=-1)
        )

    def has_reached_goal(self, drone_index):
        """Check if a drone has reached its goal."""
        return (
            np.linalg.norm(
                self.vehicle_list[drone_index].goal - self.positions[drone_index]
            )
            < self.arrival_distance
        )

    def is_collision(self, drone_index1, drone_index2, distance_matrix):
        """Check if there is a collision between two drones."""
        collision_threshold = self.case.collision_threshold
        return distance_matrix[drone_index1, drone_index2] < collision_threshold

    def handle_collision(self, drone_index1, drone_index2):
        """Handle a collision between two drones."""
        # Update warning circles
        self.warning_circles[drone_index1].set_edgecolor("r")
        self.warning_circles[drone_index2].set_edgecolor("r")

        # Record the collision
        if self.conflict_iterator in self.conflicts.keys():
            self.conflicts[self.conflict_iterator].append((drone_index1, drone_index2))
        else:
            self.conflicts[self.conflict_iterator] = [(drone_index1, drone_index2)]

    def update_info_box(self):
        """Update the info box with conflict information."""
        if self.conflict_iterator in self.conflicts.keys():
            # Handle conflicts
            self.handle_conflict_info_box()
        else:
            # No conflicts, set box to safe
            self.handle_safe_info_box()

        self.conflict_iterator += 1

    def handle_conflict_info_box(self):
        """Update the info box for a conflict."""
        # Handle conflicts
        bounding_box = dict(
            boxstyle="round", facecolor="skyblue", edgecolor="r", alpha=1
        )
        textstr = f"Conflict detected!\nDrones {[drones for drones in self.conflicts[self.conflict_iterator]]}"
        self.info_box.set_text(textstr)
        self.info_box.set_c("k")
        self.info_box.set_bbox(bounding_box)

        for conflict in self.conflicts[self.conflict_iterator]:
            if int(self.conflict_iterator - 1) in self.conflicts.keys():
                if conflict not in self.conflicts[self.conflict_iterator - 1]:
                    self.stop()
            else:
                self.stop()

    def handle_safe_info_box(self):
        """Update the info box for a safe condition."""
        # No conflicts, set box to safe
        bounding_box = dict(boxstyle="round", facecolor="wheat", edgecolor="g", alpha=1)
        textstr = f"Safe"
        self.info_box.set_text(textstr)
        self.info_box.set_bbox(bounding_box)
        self.info_box.set_c("k")

    # anim.event_source.stop()
    def play(self, event):
        """Function that is called every time the play button is pressed. It will alternate between play and pause and start/stop the animation"""
        # running is not a default attribute of the FuncAnimation object, but we have defined it ourselves lower down
        if self.animation_running:
            self.anim.event_source.stop()
            self.play_button.label.set_text("Play")
            self.animation_running = False
        else:
            self.anim.event_source.start()
            self.play_button.label.set_text("Pause")
            self.animation_running = True
        # this line seems to update the plot. Without it, the Play and Pause will not update until the mouse leaves the button area.
        # plt.pause(0.1)
        self.fig.canvas.draw()
        # self.fig.canvas.flush_events()

        return None

    # anim.event_source.stop()
    def stop(self):
        """function that can be called in the code to stop the animation"""
        # running is not a default attribute of the FuncAnimation object, but we have defined it ourselves lower down
        # self.animation_running:
        self.anim.event_source.stop()
        self.play_button.label.set_text("Play")
        self.animation_running = False
        # this line seems to update the plot. Without it, the Play and Pause will not update until the mouse leaves the button area.
        self.fig.canvas.draw()
        # self.fig.canvas.flush_events()
        return None

    def on_press(self, event):
        """Allows the user to pause and play the animation with the spacebar"""
        sys.stdout.flush()
        if event.key == " ":
            self.play(event=None)
            self.fig.canvas.draw()
            # self.fig.canvas.flush_events()
        return None

    

    def show(self):
        # show the plot
        plt.show()
        return None
    


# FuncAnimation args:
# (fig: Figure, func: (...) -> Iterable[Artist], frames: Iterable[Artist] | int | (() -> Generator) | None = ..., init_func: (() -> Iterable[Artist]) | None = ..., fargs: tuple[Any, ...] | None = ..., save_count: int | None = ..., *, cache_frame_data: bool = ..., **kwargs: Any) -> None
# TimedAnimation subclass that makes an animation by repeatedly calling a function *func*.

# Parameters
# fig : ~matplotlib.figure.Figure
#     The figure object used to get needed events, such as draw or resize.

# func : callable
#     The function to call at each frame. The first argument will be the next value in *frames*. Any additional positional arguments can be supplied using functools.partial or via the *fargs* parameter.

#     The required signature is:

#         def func(frame, *fargs) -> iterable_of_artists
#     It is often more convenient to provide the arguments using functools.partial. In this way it is also possible to pass keyword arguments. To pass a function with both positional and keyword arguments, set all arguments as keyword arguments, just leaving the *frame* argument unset:

#         def func(frame, art, *, y=None):
#             ...

#         ani = FuncAnimation(fig, partial(func, art=ln, y='foo'))
#     If blit == True, *func* must return an iterable of all artists that were modified or created. This information is used by the blitting algorithm to determine which parts of the figure have to be updated. The return value is unused if blit == False and may be omitted in that case.

# frames : iterable, int, generator function, or None, optional
#     Source of data to pass *func* and each frame of the animation

# If an iterable, then simply use the values provided. If the
#       iterable has a length, it will override the *save_count* kwarg.

# If an integer, then equivalent to passing range(frames)

# If a generator function, then must have the signature:

#          def gen_function() -> obj
# If *None*, then equivalent to passing itertools.count.
#     In all of these cases, the values in *frames* is simply passed through to the user-supplied *func* and thus can be of any type.

# init_func : callable, optional
#     A function used to draw a clear frame. If not given, the results of drawing from the first item in the frames sequence will be used. This function will be called once before the first frame.

#     The required signature is:

#         def init_func() -> iterable_of_artists
#     If blit == True, *init_func* must return an iterable of artists to be re-drawn. This information is used by the blitting algorithm to determine which parts of the figure have to be updated. The return value is unused if blit == False and may be omitted in that case.

# fargs : tuple or None, optional
#     Additional arguments to pass to each call to *func*. Note: the use of functools.partial is preferred over *fargs*. See *func* for details.

# save_count : int, optional
#     Fallback for the number of values from *frames* to cache. This is only used if the number of frames cannot be inferred from *frames*, i.e. when it's an iterator without length or a generator.

# interval : int, default: 200
#     Delay between frames in milliseconds.

# repeat_delay : int, default: 0
#     The delay in milliseconds between consecutive animation runs, if *repeat* is True.

# repeat : bool, default: True
#     Whether the animation repeats when the sequence of frames is completed.

# blit : bool, default: False
#     Whether blitting is used to optimize drawing. Note: when using blitting, any animated artists will be drawn according to their zorder; however, they will be drawn on top of any previous artists, regardless of their zorder.

# cache_frame_data : bool, default: True
#     Whether frame data is cached. Disabling cache might be helpful when frames contain large objects.

