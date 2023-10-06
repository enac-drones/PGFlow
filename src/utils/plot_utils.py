import sys

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np

# Import animation package
from matplotlib.animation import FuncAnimation

# Import slider package
from matplotlib.widgets import Slider, Button
from typing import List
from src.vehicle import Vehicle
from src.cases import Case


def plot_trajectories(Arena, ArenaR, Vehicle_list):
    plt.figure(figsize=(5, 5))
    minx = -5
    maxx = 5
    miny = -5
    maxy = 5
    plt.grid(color="k", linestyle="-.", linewidth=0.5)
    for building in Arena.buildings:
        plt.plot(
            np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
            np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
            "salmon",
            alpha=0.5,
        )
        plt.fill(
            np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
            np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
            "salmon",
            alpha=0.5,
        )
    for buildingR in ArenaR.buildings:
        plt.plot(
            np.hstack((buildingR.vertices[:, 0], buildingR.vertices[0, 0])),
            np.hstack((buildingR.vertices[:, 1], buildingR.vertices[0, 1])),
            "m",
        )
        plt.fill(
            np.hstack((buildingR.vertices[:, 0], buildingR.vertices[0, 0])),
            np.hstack((buildingR.vertices[:, 1], buildingR.vertices[0, 1])),
            "m",
        )
    for _v in range(len(Vehicle_list)):
        plt.plot(Vehicle_list[_v].path[:, 0], Vehicle_list[_v].path[:, 1], linewidth=2)
        plt.plot(Vehicle_list[_v].path[0, 0], Vehicle_list[_v].path[0, 1], "o")
        plt.plot(Vehicle_list[_v].goal[0], Vehicle_list[_v].goal[1], "x")
    plt.xlabel("East-direction --> (m)")
    plt.ylabel("North-direction --> (m)")
    plt.xlim([minx, maxx])
    plt.ylim([miny, maxy])
    plt.show()


def plot_trajectories1(Arena, ArenaR, Vehicle_list):
    # limit is the percentage of the plot you would like to have
    # plt.close('all')
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111)
    fig.subplots_adjust(bottom=0.1, top=0.9)

    # Create axes for sliders
    # variable inside add_axes is left, bottom, width, height
    ax_prog = fig.add_axes([0.3, 0.92, 0.4, 0.05])
    ax_prog.spines["top"].set_visible(True)
    ax_prog.spines["right"].set_visible(True)

    # Create sliders
    slider = Slider(
        ax=ax_prog,
        label="Progress ",
        valinit=5.0,
        valstep=0.001,
        valmin=0,
        valmax=1.0,
        valfmt=" %1.1f ",
        facecolor="#cc7000",
    )

    # create the play button
    # play_ax = plt.axes([0.8, 0.92, 0.1, 0.05])
    play_ax = fig.add_axes([0.8, 0.92, 0.1, 0.05])
    play_button = Button(play_ax, "Play", color="0.8", hovercolor="0.95")

    #####################################################################################
    # these control the size of the slider for some reason (at least in x)
    # minx = 0
    # maxx = 1
    # miny = -5
    # maxy = 5

    for building in Arena.buildings:
        # print(f"building vertices are {(building.vertices[:,0],building.vertices[0,0])}")
        ax.plot(
            np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
            np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
            "salmon",
            alpha=0.5,
        )
        ax.fill(
            np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
            np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
            "salmon",
            alpha=0.5,
        )
    for buildingR in ArenaR.buildings:
        ax.plot(
            np.hstack((buildingR.vertices[:, 0], buildingR.vertices[0, 0])),
            np.hstack((buildingR.vertices[:, 1], buildingR.vertices[0, 1])),
            "m",
        )
        ax.fill(
            np.hstack((buildingR.vertices[:, 0], buildingR.vertices[0, 0])),
            np.hstack((buildingR.vertices[:, 1], buildingR.vertices[0, 1])),
            "m",
        )

    # plot_list_dict = {}
    list_of_point_lengths = []
    for i in range(len(Vehicle_list)):
        n_points = len(Vehicle_list[i].path[:, 0])
        list_of_point_lengths.append(n_points)
    n = max(list_of_point_lengths)

    # plot_list is a list that will hold the references to each trajectory plot
    plot_list = []
    # list to store (the references to) the drone icon plots
    drone_list = []
    # same as above, but display these only when certain separation minima are not respected
    warning_circles = []
    for _v in range(len(Vehicle_list)):
        # define the current coordinates of the drone
        x, y = Vehicle_list[_v].path[-1, 0], Vehicle_list[_v].path[-1, 1]
        # Plot default data
        (f_d,) = ax.plot(
            Vehicle_list[_v].path[:n, 0], Vehicle_list[_v].path[:n, 1], linewidth=2
        )
        # the line below is for adding an icon to the current vehicle position
        # also the 'x' at the end is the position marker, can be changed to other things
        (drone_icon,) = ax.plot(
            Vehicle_list[_v].path[-1, 0], Vehicle_list[_v].path[-1, 1], "x"
        )
        # plot the default warning circles
        # circle1 = plt.Circle((x, y), 0.2, color = "r")
        # plot the circle
        warning_circle = plt.Circle((x, y), 0.2, fill=False, edgecolor="r", linewidth=2)
        ax.add_artist(warning_circle)
        # warning_circle, = ax.plot(x, y, 'ro')

        # warning_circle = ax.add_patch( circle1 )
        warning_circles.append(warning_circle)

        plot_list.append(f_d)
        # also uncomment the line below once drone_icon is fixed
        drone_list.append(drone_icon)
        # the following two lines plot the start and end points
        ax.plot(Vehicle_list[_v].path[0, 0], Vehicle_list[_v].path[0, 1], "")
        ax.plot(Vehicle_list[_v].goal[0], Vehicle_list[_v].goal[1], "*")

    # Update values
    def update(val):
        # scale val to be between 0 and 1 while the problem with the slider is not fixed
        # temp stores the current value of the slider (a float between 0 and 1)
        temp = slider.val
        # n stores the maximum number of iterations it took for a drone to reach its destination. This is equivalent to time if ...
        # travelling at a constant speed. plot_until therefore is the current time value of the simulation.
        plot_until = int(np.floor(temp * n))
        # print(f"plot_until is currently {plot_until}")
        for i in range(len(plot_list)):
            # we are now telling the code to plot the drone trajectories only until the value of the slider (or time)
            plot_list[i].set_data(
                Vehicle_list[i].path[:plot_until, 0],
                Vehicle_list[i].path[:plot_until, 1],
            )
            if plot_until == 0:
                # if t=0 we want to draw the drone icons at their starting points
                drone_list[i].set_data(
                    Vehicle_list[i].path[0, 0], Vehicle_list[i].path[0, 1]
                )
                warning_circles[i].center = (
                    Vehicle_list[i].path[0, 0],
                    Vehicle_list[i].path[0, 1],
                )
                # warning_circles[i].set_data(Vehicle_list[i].path[0,0],Vehicle_list[i].path[0,1])
            elif plot_until < len(Vehicle_list[i].path[:, 0]):
                # if t < the time it takes for this drone to reach its destination, show the drone icon at its current position
                drone_list[i].set_data(
                    Vehicle_list[i].path[plot_until - 1, 0],
                    Vehicle_list[i].path[plot_until - 1, 1],
                )
                warning_circles[i].center = (
                    Vehicle_list[i].path[plot_until - 1, 0],
                    Vehicle_list[i].path[plot_until - 1, 1],
                )
                warning_circles[i].set_fill(False)
                warning_circles[i].set_edgecolor("g")
            else:
                # here is where we plot what we want once the drone is at its destination
                # if t >= time taken for the drone to reach its destination, ensure the drone icon is shown at its destination
                # to avoid indexing errors
                drone_list[i].set_data(
                    Vehicle_list[i].path[-1, 0], Vehicle_list[i].path[-1, 1]
                )
                # plt.Circle object has severable attributes that can be dynamically modified
                warning_circles[i].center = (
                    Vehicle_list[i].path[-1, 0],
                    Vehicle_list[i].path[-1, 1],
                )
                warning_circles[i].set_fill(True)
                warning_circles[i].set_facecolor("b")

        fig.canvas.draw_idle()

    # define play function
    def play(event):
        for val in np.linspace(0, 1, 100):
            slider.set_val(val)
            update(val)
            # fig.canvas.draw_idle()
            plt.pause(0.01)
        # play(event)

    slider.on_changed(update)
    play_button.on_clicked(play)

    # everything with plt. is not necessarily working due to the subfigure situation, will fix
    # plt.xlabel('East-direction --> (m)')
    # plt.ylabel('North-direction --> (m)')
    # plt.xlim([minx, maxx])
    # plt.ylim([miny, maxy])
    ax.set_xlim([-5, 5])
    ax.set_ylim([-5, 5])
    ax.set_box_aspect(1)
    ax.set_xlabel("East --> (m)")
    ax.set_ylabel("North --> (m)")
    # print("we are here")
    ax.grid(color="k", linestyle="-", linewidth=0.5, which="major")
    ax.grid(color="k", linestyle=":", linewidth=0.5, which="minor")
    # ax.grid(True)
    ax.minorticks_on()
    plt.show()


###################################################################################


# class plot_trajectories2:
#     """Same as above but trying to use the FuncAnimation for the play button implementation which supposedly uses less CPU"""

#     def __init__(self, case: Case, update_every: int):
#         self.case = case
#         self.Arena = case.arena
#         self.ArenaR = case.arena
#         self.vehicle_list = case.vehicle_list
#         self.case_name = case.name
#         self.update_every = update_every
#         # plt.close('all')
#         self.fig, self.ax = self.plot_setup()
#         self.slider = self.create_slider(fig=self.fig)
#         self.play_button = self.create_button(fig=self.fig)
#         self.info_box = self.create_info_box(ax=self.ax)
#         self.case_name = self.show_case_name(ax=self.ax)
#         self.plot_buildings(ax=self.ax, Arena=self.Arena, ArenaR=self.ArenaR)
#         self.time_steps_max = self.get_max_timesteps(self.vehicle_list)

#         # plot_list is a list that will hold the references to each trajectory plot
#         self.plot_list = []
#         # list to store (the references to) the drone icon plots
#         self.drone_list = []
#         # same as above, but display these only when certain separation minima are not respected
#         self.warning_circles = []
#         # initialize empty array to store vehicle positions
#         self.positions = np.zeros((len(self.vehicle_list), 3))
#         self.initial_plot(Vehicle_list=self.vehicle_list, ax=self.ax)

#         # this variable will increase by 1 every time a collision is detected
#         self.conflict_iterator = 0
#         self.conflicts = {}
#         self.conflicts["addressed"] = []
#         # create new set to hold the conflicts that have already caused the simulation to pause:
#         # addressed_conflicts = set()
#         # connect the action of pressing the spacebar to the result we want it to have
#         self.fig.canvas.mpl_connect("key_press_event", self.on_press)
#         # Create the animation object, it starts automatically against my will BUG
#         self.anim = FuncAnimation(
#             self.fig,
#             self.animate,
#             interval=50,
#             frames=101,
#             init_func=None,
#             blit=False,
#             repeat=True,
#             repeat_delay=1000,
#         )

#         # tell the slider to update the plot when it is moved
#         self.slider.on_changed(self.update)
#         # call the play function when the button is pressed (to play or pause the animation)
#         self.play_button.on_clicked(self.play)

#         # again this line updates the plot, without it, the animation starts by default even though we have anim.event_source.stop()
#         # perhaps there is a better way of doing this that I am not aware of.
#         # plt.pause(0.1)
#         # the line below also appears to do the trick, and better
#         self.fig.canvas.draw()

#         # these three lines are a bit of a hack to stop the simulation which for some reason automatically starts BUG
#         self.animation_running = True
#         self.play(event=None)
#         self.slider.set_val(0.0)
#         # fig.canvas.draw_idle()

#     def plot_setup(self):
#         fig = plt.figure(figsize=(8, 8))
#         ax = fig.add_subplot(111)
#         fig.subplots_adjust(bottom=0.1, top=0.9)

#         ax.set_xlim([-5, 5])
#         ax.set_ylim([-5, 5])
#         ax.set_box_aspect(1)
#         ax.set_xlabel("East --> (m)")
#         ax.set_ylabel("North --> (m)")
#         ax.grid(color="k", linestyle="-", linewidth=0.5, which="major")
#         ax.grid(color="k", linestyle=":", linewidth=0.5, which="minor")
#         # ax.grid(True)
#         ax.minorticks_on()
#         return fig, ax

#     def create_slider(self, fig):
#         # Create axes for sliders
#         # variable inside add_axes is left, bottom, width, height
#         ax_prog = fig.add_axes([0.3, 0.92, 0.4, 0.05])
#         ax_prog.spines["top"].set_visible(True)
#         ax_prog.spines["right"].set_visible(True)

#         # Create slider object to iterate through the plot
#         slider = Slider(
#             ax=ax_prog,
#             label="Progress ",
#             valinit=5.0,
#             valstep=0.001,
#             valmin=0,
#             valmax=1.0,
#             valfmt=" %1.1f ",
#             facecolor="#cc7000",
#         )
#         return slider

#     def create_button(self, fig):
#         # create the play button axis object
#         play_ax = fig.add_axes([0.8, 0.92, 0.1, 0.05])
#         # create a play button at the location of the axis object
#         play_button = Button(play_ax, "Play", color="0.8", hovercolor="0.95")
#         return play_button

#     def create_info_box(self, ax):
#         # these are matplotlib.patch.Patch properties
#         bounding_box = dict(boxstyle="round", facecolor="wheat", edgecolor="g", alpha=1)
#         textstr = "Safe"
#         # place a text box in upper left in axes coords
#         info_box = ax.text(
#             0.05,
#             0.95,
#             textstr,
#             transform=ax.transAxes,
#             fontsize=14,
#             verticalalignment="top",
#             bbox=bounding_box,
#             color="g",
#         )
#         return info_box

#     def show_case_name(self, ax):
#         # these are matplotlib.patch.Patch properties
#         bounding_box = dict(boxstyle="round", facecolor="wheat", edgecolor="g", alpha=1)
#         textstr = self.case_name
#         # place a text box in upper left in axes coords
#         info_box = ax.text(
#             0.5,
#             0.95,
#             textstr,
#             transform=ax.transAxes,
#             fontsize=14,
#             verticalalignment="top",
#             bbox=bounding_box,
#             color="g",
#         )
#         return info_box

#     def plot_buildings(self, ax, Arena, ArenaR):
#         for building in Arena.buildings:
#             # print(f"building vertices are {(building.vertices[:,0],building.vertices[0,0])}")
#             ax.plot(
#                 np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
#                 np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
#                 "salmon",
#                 alpha=0.5,
#             )
#             ax.fill(
#                 np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
#                 np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
#                 "salmon",
#                 alpha=0.5,
#             )
#         for buildingR in ArenaR.buildings:
#             ax.plot(
#                 np.hstack((buildingR.vertices[:, 0], buildingR.vertices[0, 0])),
#                 np.hstack((buildingR.vertices[:, 1], buildingR.vertices[0, 1])),
#                 "m",
#             )
#             ax.fill(
#                 np.hstack((buildingR.vertices[:, 0], buildingR.vertices[0, 0])),
#                 np.hstack((buildingR.vertices[:, 1], buildingR.vertices[0, 1])),
#                 "m",
#             )
#         return None

#     def get_max_timesteps(self, Vehicle_list):
#         # these few lines obtain the maximum length of any path for all the drones, aka the time taken for the last drone to reach its destination
#         # maybe there's a neater way of doing this but it isn't computationally expensive so for now it's fine
#         list_of_point_lengths = []
#         for i in range(len(Vehicle_list)):
#             n_points = len(Vehicle_list[i].path[:, 0])
#             list_of_point_lengths.append(n_points)
#         # time_steps_max stores the maximum amount of timesteps for any drone to reach its destination. time_steps_max*dt = t_max
#         return max(list_of_point_lengths)

#     def initial_plot(self, Vehicle_list, ax):
#         for _v in range(len(Vehicle_list)):
#             # define the current coordinates of the drone
#             x, y, z = (
#                 Vehicle_list[_v].path[-1, 0],
#                 Vehicle_list[_v].path[-1, 1],
#                 Vehicle_list[_v].path[-1, 2],
#             )
#             self.positions[_v] = [x, y, z]
#             # print(positions, type(positions))
#             # Plot default data
#             # note that the comma operator is mandatory, it turns the ax.plot object into a tuple
#             (f_d,) = ax.plot(
#                 Vehicle_list[_v].path[: self.time_steps_max, 0],
#                 Vehicle_list[_v].path[: self.time_steps_max, 1],
#                 linewidth=2,
#             )
#             # the line below is for adding an icon to the current vehicle position
#             # also the 'x' at the end is the position marker, can be changed to other things
#             (drone_icon,) = ax.plot(x, y, "x")

#             # plot the default warning circles
#             # define the circle
#             warning_circle = plt.Circle(
#                 (x, y),
#                 self.case.collision_threshold / 2,
#                 fill=False,
#                 edgecolor="r",
#                 linewidth=2,
#             )
#             # add the circle to the plot
#             ax.add_artist(warning_circle)

#             self.warning_circles.append(warning_circle)

#             self.plot_list.append(f_d)
#             # append the references to the drone icons to the drone icon list
#             self.drone_list.append(drone_icon)
#             # the following two lines plot the start and end points
#             ax.plot(Vehicle_list[_v].path[0, 0], Vehicle_list[_v].path[0, 1], "")
#             ax.plot(Vehicle_list[_v].goal[0], Vehicle_list[_v].goal[1], "*")
#         return None

#     # Update values
#     def update(self, val):
#         # self.time_steps_max stores the maximum number of iterations it took for a drone to reach its destination. This is equivalent to time if ...
#         # ...travelling at a constant speed. plot_until therefore is the current time value of the simulation.
#         plot_until = int(np.floor(self.slider.val * self.time_steps_max))
#         for i in range(len(self.plot_list)):
#             # we are now telling the code to plot the drone trajectories only until the value of the slider (or time)
#             self.plot_list[i].set_data(
#                 self.vehicle_list[i].path[:plot_until, 0],
#                 self.vehicle_list[i].path[:plot_until, 1],
#             )

#             if plot_until == 0:
#                 # here is what we plot when the drones are at their starting positions
#                 # if t=0 we want to draw the drone icons at their starting points
#                 x, y, z = self.vehicle_list[i].path[0, :3]
#                 self.warning_circles[i].set_edgecolor("b")
#             elif plot_until < len(self.vehicle_list[i].path[:, 0]):
#                 # here is what we plot during drone transit
#                 # if t < the time it takes for this drone to reach its destination, show the drone icon at its current position
#                 x, y, z = self.vehicle_list[i].path[plot_until - 1, :3]
#                 self.warning_circles[i].set_fill(False)
#                 # self.warning_circles[i].set_edgecolor("g")
#                 if (
#                     plot_until % self.update_every == 0
#                     or (plot_until - 1) % self.update_every == 0
#                     or (plot_until - 2) % self.update_every == 0
#                     or (plot_until - 3) % self.update_every == 0
#                     or (plot_until - 4) % self.update_every == 0
#                     or (plot_until - 5) % self.update_every == 0
#                 ):
#                     self.warning_circles[i].set_edgecolor("y")
#                 else:
#                     self.warning_circles[i].set_edgecolor("g")
#             else:
#                 # here is where we plot what we want once the drone is at its destination
#                 # if t >= time taken for the drone to reach its destination, ensure the drone icon is shown at its destination
#                 # to avoid indexing errors
#                 x, y, z = self.vehicle_list[i].path[-1, :3]
#                 # plt.Circle object has severable attributes that can be dynamically modified
#                 self.warning_circles[i].set_fill(True)
#                 self.warning_circles[i].set_facecolor("skyblue")
#                 self.warning_circles[i].set_edgecolor("b")
#             self.drone_list[i].set_data(x, y)
#             self.warning_circles[i].center = (x, y)
#             self.positions[i] = [x, y, z]
#         # now detect and handle collisions
#         self.collision_handling()
#         return self.plot_list + self.drone_list + self.warning_circles

#     def collision_handling(self):
#         """Figure out if there is a collision and what to display when collisions are encountered"""
#         distance_matrix = np.sqrt(
#             np.sum((self.positions[:, np.newaxis] - self.positions) ** 2, axis=-1)
#         )
#         # set collision threshold
#         collision_threshold = self.case.collision_threshold
#         for i in range(distance_matrix.shape[0]):
#             if np.linalg.norm(self.vehicle_list[i].goal - self.positions[i]) < 0.2:
#                 continue
#             for j in range(i + 1, distance_matrix.shape[1]):
#                 if np.linalg.norm(self.vehicle_list[j].goal - self.positions[j]) < 0.2:
#                     continue
#                 if distance_matrix[i, j] < collision_threshold:
#                     # print(f"Collision detected between drones {i} and {j}")
#                     self.warning_circles[i].set_edgecolor("r")
#                     self.warning_circles[j].set_edgecolor("r")
#                     # conflicts.update([i,j])
#                     if self.conflict_iterator in self.conflicts.keys():
#                         self.conflicts[self.conflict_iterator].append((i, j))
#                     else:
#                         self.conflicts[self.conflict_iterator] = [(i, j)]
#         # the line below checks if there is there are any conflicts at the current iteration
#         if self.conflict_iterator in self.conflicts.keys():
#             # these are matplotlib.patch.Patch properties
#             bounding_box = dict(
#                 boxstyle="round", facecolor="skyblue", edgecolor="r", alpha=1
#             )
#             # self.bounding_box['edgecolor'] = 'r'
#             # self.bounding_box['facecolor'] = 'skyblue'
#             textstr = f"Conflict detected!\nDrones {[drones for drones in self.conflicts[self.conflict_iterator]]}"
#             # place a text box in upper left in axes coords
#             # info_box = ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
#             #        verticalalignment='top', bbox=bounding_box,color = 'g')
#             ###########
#             self.info_box.set_text(textstr)
#             self.info_box.set_c("k")
#             self.info_box.set_bbox(bounding_box)
#             ############
#             # print(f"there is a conflict, slider value = {val}")

#             for conflict in self.conflicts[self.conflict_iterator]:
#                 if int(self.conflict_iterator - 1) in self.conflicts.keys():
#                     # print(self.conflict_iterator,self.conflicts[self.conflict_iterator],self.conflicts[self.conflict_iterator-1])
#                     if conflict not in self.conflicts[self.conflict_iterator - 1]:
#                         # print("Conflict already addressed, not stopping simulation.")
#                         self.stop()
#                 else:
#                     # print("No conflicts previously, should stop now")
#                     self.stop()
#         else:
#             # no conflicts, set box to safe
#             bounding_box = dict(
#                 boxstyle="round", facecolor="wheat", edgecolor="g", alpha=1
#             )
#             textstr = f"Safe"
#             # info_box = ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
#             #        verticalalignment='top', bbox=bounding_box,color = 'g')

#             #######
#             self.info_box.set_text(textstr)
#             self.info_box.set_bbox(bounding_box)
#             self.info_box.set_c("k")
#             #######

#         self.conflict_iterator += 1
#         return None

#     # anim.event_source.stop()
#     def play(self, event):
#         """Function that is called every time the play button is pressed. It will alternate between play and pause and start/stop the animation"""
#         # running is not a default attribute of the FuncAnimation object, but we have defined it ourselves lower down
#         if self.animation_running:
#             self.anim.event_source.stop()
#             self.play_button.label.set_text("Play")
#             self.animation_running = False
#         else:
#             self.anim.event_source.start()
#             self.play_button.label.set_text("Pause")
#             self.animation_running = True
#         # this line seems to update the plot. Without it, the Play and Pause will not update until the mouse leaves the button area.
#         # plt.pause(0.1)
#         self.fig.canvas.draw_idle()
#         return None

#     # anim.event_source.stop()
#     def stop(self):
#         """function that can be called in the code to stop the animation"""
#         # running is not a default attribute of the FuncAnimation object, but we have defined it ourselves lower down
#         # self.animation_running:
#         self.anim.event_source.stop()
#         self.play_button.label.set_text("Play")
#         self.animation_running = False
#         # else:
#         #     self.anim.event_source.start()
#         #     self.play_button.label.set_text("Pause")
#         #     self.animation_running = True
#         # this line seems to update the plot. Without it, the Play and Pause will not update until the mouse leaves the button area.
#         # plt.pause(0.1)
#         self.fig.canvas.draw_idle()
#         return None

#     def on_press(self, event):
#         """Allows the user to pause and play the animation with the spacebar"""
#         sys.stdout.flush()
#         if event.key == " ":
#             self.play(event=None)
#             self.fig.canvas.draw()
#         return None

#     def animate(self, i):
#         """Function that updates the slider and calls the update function. i iterates from 0 to the number of frames"""
#         # obtain the slider value to 2dp
#         current_slider_value = round(self.slider.val, 2)
#         # set i to the slider value so that the simulation stops when the slider reaches the end
#         # it is 100x the slider value because the slider goes from 0 to 1 and the i from 0 to 100
#         i = int(100 * current_slider_value)
#         # print(f"i={i}")
#         # increment the slider by 0.01 for every frame
#         self.slider.set_val((current_slider_value + 0.01) % (self.slider.valmax + 0.01))
#         # stop the animation when the slider reaches the end
#         if i == 99:
#             # calling the play function while the animation is running stops the animation
#             self.play(event=None)
#         # nothing to return I'm pretty sure :)
#         return None

#     def show(self):
#         # show the plot
#         plt.show()
#         return None





class PlotTrajectories:
    """Same as above but trying to use the FuncAnimation for the play button implementation which supposedly uses less CPU"""
    # UPDATE_INTERVAL = 5
    SLIDER_ANIMATION_INTERVAL = 0.01
    FIG_SIZE = (8, 8)
    AXIS_LIMITS = (-5, 5)
    GOAL_THRESHOLD = 0.2
    FRAMES = 101
    UPDATE_INTERVAL = 50

    def __init__(self, case: Case, update_every: int):
        self.case = case
        self.Arena = case.arena
        self.ArenaR = case.arena
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
        # Create the animation object, it starts automatically against my will BUG
        self.anim = FuncAnimation(
            self.fig,
            self.animate,
            interval=self.UPDATE_INTERVAL,
            frames=self.FRAMES,
            init_func=None,
            blit=False,
            repeat=True,
            repeat_delay=1000,
        )

        # tell the slider to update the plot when it is moved
        self.slider.on_changed(self.update)
        # call the play function when the button is pressed (to play or pause the animation)
        self.play_button.on_clicked(self.play)

        # again this line updates the plot, without it, the animation starts by default even though we have anim.event_source.stop()
        # perhaps there is a better way of doing this that I am not aware of.
        # plt.pause(0.1)
        # the line below also appears to do the trick, and better
        self.fig.canvas.draw()

        # these three lines are a bit of a hack to stop the simulation which for some reason automatically starts BUG
        self.animation_running = True
        self.play(event=None)
        self.slider.set_val(0.0)
        # fig.canvas.draw_idle()

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
            valstep=0.001,
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
            # print(f"building vertices are {(building.vertices[:,0],building.vertices[0,0])}")
            ax.plot(
                np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
                np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
                "salmon",
                alpha=0.5,
            )
            ax.fill(
                np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
                np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
                "salmon",
                alpha=0.5,
            )
        for buildingR in ArenaR.buildings:
            ax.plot(
                np.hstack((buildingR.vertices[:, 0], buildingR.vertices[0, 0])),
                np.hstack((buildingR.vertices[:, 1], buildingR.vertices[0, 1])),
                "m",
            )
            ax.fill(
                np.hstack((buildingR.vertices[:, 0], buildingR.vertices[0, 0])),
                np.hstack((buildingR.vertices[:, 1], buildingR.vertices[0, 1])),
                "m",
            )
        return None

    def get_max_timesteps(self, vehicle_list):
        # these few lines obtain the maximum length of any path for all the drones, aka the time taken for the last drone to reach its destination
        # maybe there's a neater way of doing this but it isn't computationally expensive so for now it's fine
        # max_timesteps stores the maximum amount of timesteps for any drone to reach its destination. time_steps_max*dt = t_max
        max_timesteps = max(len(vehicle.path[:,0]) for vehicle in vehicle_list)
        return max_timesteps

    def initial_plot(self, vehicle_list, ax):
        for v_idx, _ in enumerate(vehicle_list):
            # define the current coordinates of the drone
            x, y, z = (
                vehicle_list[v_idx].path[-1, 0],
                vehicle_list[v_idx].path[-1, 1],
                vehicle_list[v_idx].path[-1, 2],
            )
            self.positions[v_idx] = [x, y, z]
            # print(positions, type(positions))
            # Plot default data
            # note that the comma operator is mandatory, it turns the ax.plot object into a tuple
            (drone_path,) = ax.plot(
                vehicle_list[v_idx].path[: self.time_steps_max, 0],
                vehicle_list[v_idx].path[: self.time_steps_max, 1],
                linewidth=2,
            )
            # the line below is for adding an icon to the current vehicle position
            # also the 'x' at the end is the position marker, can be changed to other things
            (drone_icon,) = ax.plot(x, y, "x")

            # plot the default warning circles
            # define the circle
            warning_circle = plt.Circle(
                (x, y),
                self.case.collision_threshold / 2,
                fill=False,
                edgecolor="r",
                linewidth=2,
            )
            # add the circle to the plot
            ax.add_artist(warning_circle)

            self.warning_circles.append(warning_circle)

            self.plot_list.append(drone_path)
            # append the references to the drone icons to the drone icon list
            self.drone_list.append(drone_icon)
            # the following two lines plot the start and end points
            ax.plot(vehicle_list[v_idx].path[0, 0], vehicle_list[v_idx].path[0, 1], "")
            ax.plot(vehicle_list[v_idx].goal[0], vehicle_list[v_idx].goal[1], "*")
        return None



    def update(self,val):
        #val self.slider.val is the same as val
        plot_until = int(np.floor(val * self.time_steps_max))
        self.update_plot(plot_until)
        self.update_drone_positions(plot_until)
        self.update_warning_circles(plot_until)
        self.collision_handling()

    def update_plot(self, plot_until):
        for i in range(len(self.plot_list)):
            self.plot_list[i].set_data(
                self.vehicle_list[i].path[:plot_until, 0],
                self.vehicle_list[i].path[:plot_until, 1],
            )
            self.plot_list[i].set_data(self.vehicle_list[i].path[:plot_until, 0], self.vehicle_list[i].path[:plot_until, 1])

    def update_drone_positions(self, plot_until):
        for i in range(len(self.drone_list)):
            if plot_until == 0:
                x, y, z = self.vehicle_list[i].path[0, :3]
            elif plot_until < len(self.vehicle_list[i].path[:, 0]):
                x, y, z = self.vehicle_list[i].path[plot_until - 1, :3]
            else:
                x, y, z = self.vehicle_list[i].path[-1, :3]
            self.drone_list[i].set_data(x, y)
            self.positions[i] = [x, y, z]

    def update_warning_circles(self, plot_until):
        for i in range(len(self.warning_circles)):
            if plot_until == 0:
                self.warning_circles[i].set_edgecolor("b")
            elif plot_until < len(self.vehicle_list[i].path[:, 0]):
                self.warning_circles[i].set_fill(False)
                show_communication = plot_until%self.update_every in range(5)
                if show_communication:
                    self.warning_circles[i].set_edgecolor("g")
                    self.warning_circles[i].set_fill(True)
                    self.warning_circles[i].set_facecolor("lightblue")
                else:
                    self.warning_circles[i].set_fill(False)
                    self.warning_circles[i].set_edgecolor("gray")
            else:
                self.warning_circles[i].set_fill(True)
                self.warning_circles[i].set_facecolor("skyblue")
                self.warning_circles[i].set_edgecolor("b")
            self.warning_circles[i].center = self.positions[i][:2]


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

    def calculate_distance_matrix(self):
        """Calculate the Euclidean distance matrix between drones."""
        return np.sqrt(np.sum((self.positions[:, np.newaxis] - self.positions) ** 2, axis=-1))

    def has_reached_goal(self, drone_index):
        """Check if a drone has reached its goal."""
        return np.linalg.norm(self.vehicle_list[drone_index].goal - self.positions[drone_index]) < self.GOAL_THRESHOLD

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
        bounding_box = dict(boxstyle="round", facecolor="skyblue", edgecolor="r", alpha=1)
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
        self.fig.canvas.draw_idle()
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
        self.fig.canvas.draw_idle()
        return None

    def on_press(self, event):
        """Allows the user to pause and play the animation with the spacebar"""
        sys.stdout.flush()
        if event.key == " ":
            self.play(event=None)
            self.fig.canvas.draw()
        return None

    def animate(self, i):
        """Function that updates the slider and calls the update function. i iterates from 0 to the number of frames"""
        # obtain the slider value to 2dp
        current_slider_value = round(self.slider.val, 2)
        # set i to the slider value so that the simulation stops when the slider reaches the end
        # it is 100x the slider value because the slider goes from 0 to 1 and the i from 0 to 100
        i = int((self.FRAMES-1) * current_slider_value)
        # print(f"i={i}")
        # increment the slider by 0.01 for every frame
        self.slider.set_val((current_slider_value + self.SLIDER_ANIMATION_INTERVAL) % (self.slider.valmax + self.SLIDER_ANIMATION_INTERVAL))
        # stop the animation when the slider reaches the end
        if i == self.FRAMES-2:
            # calling the play function while the animation is running stops the animation
            self.play(event=None)
        # nothing to return I'm pretty sure :)
        return None

    def show(self):
        # show the plot
        plt.show()
        return None


















class plot_trajectories3:
    """Same as above but trying to use the FuncAnimation for the play button implementation which supposedly uses less CPU"""

    def __init__(self, Arena, ArenaR, Vehicle_list):
        self.Arena = Arena
        self.ArenaR = ArenaR
        self.vehicle_list: List[Vehicle] = Vehicle_list
        # plt.close('all')
        self.fig, self.ax = self.plot_setup()
        self.slider: Slider = self.create_slider(fig=self.fig)
        self.play_button = self.create_button(fig=self.fig)
        self.info_box = self.create_info_box(ax=self.ax)
        self.plot_buildings(ax=self.ax, Arena=self.Arena, ArenaR=self.ArenaR)
        self.time_steps_max = self.get_max_timesteps(self.vehicle_list)

        self.stream = None
        # plot_list is a list that will hold the references to each trajectory plot
        self.plot_list = []
        # list to store (the references to) the drone icon plots
        self.drone_list = []
        # self.ghost_drone_list = []
        # same as above, but display these only when certain separation minima are not respected
        self.warning_circles = []
        # self.ghost_warning_circles = []
        # initialize empty array to store vehicle positions
        self.positions = np.zeros((len(Vehicle_list), 3))
        # self.ghost_positions = np.zeros((len(Vehicle_list), 3))

        self.initial_plot(Vehicle_list=self.vehicle_list, ax=self.ax)

        # this variable will increase by 1 every time a collision is detected
        self.conflict_iterator = 0
        self.conflicts = {}
        self.conflicts["addressed"] = []
        # create new set to hold the conflicts that have already caused the simulation to pause:
        # addressed_conflicts = set()
        # connect the action of pressing the spacebar to the result we want it to have
        self.fig.canvas.mpl_connect("key_press_event", self.on_press)
        # Create the animation object, it starts automatically against my will BUG
        self.anim = FuncAnimation(
            self.fig,
            self.animate,
            interval=50,
            frames=101,
            init_func=None,
            blit=False,
            repeat=True,
            repeat_delay=1000,
        )

        # tell the slider to update the plot when it is moved
        self.slider.on_changed(self.update)
        # call the play function when the button is pressed (to play or pause the animation)
        self.play_button.on_clicked(self.play)

        # again this line updates the plot, without it, the animation starts by default even though we have anim.event_source.stop()
        # perhaps there is a better way of doing this that I am not aware of.
        # plt.pause(0.1)
        # the line below also appears to do the trick, and better
        self.fig.canvas.draw()

        # these three lines are a bit of a hack to stop the simulation which for some reason automatically starts BUG
        self.animation_running = True
        self.play(event=None)
        self.slider.set_val(0.0)
        # fig.canvas.draw_idle()

    def plot_setup(self):
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111)
        fig.subplots_adjust(bottom=0.1, top=0.9)

        ax.set_xlim([-5, 5])
        ax.set_ylim([-5, 5])
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
            valinit=5.0,
            valstep=0.001,
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

    def plot_buildings(self, ax, Arena, ArenaR):
        for building in Arena.buildings:
            # print(f"building vertices are {(building.vertices[:,0],building.vertices[0,0])}")
            ax.plot(
                np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
                np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
                "salmon",
                alpha=0.5,
            )
            ax.fill(
                np.hstack((building.vertices[:, 0], building.vertices[0, 0])),
                np.hstack((building.vertices[:, 1], building.vertices[0, 1])),
                "salmon",
                alpha=0.5,
            )
        for buildingR in ArenaR.buildings:
            ax.plot(
                np.hstack((buildingR.vertices[:, 0], buildingR.vertices[0, 0])),
                np.hstack((buildingR.vertices[:, 1], buildingR.vertices[0, 1])),
                "m",
            )
            ax.fill(
                np.hstack((buildingR.vertices[:, 0], buildingR.vertices[0, 0])),
                np.hstack((buildingR.vertices[:, 1], buildingR.vertices[0, 1])),
                "m",
            )
        return None

    def get_max_timesteps(self, Vehicle_list):
        # these few lines obtain the maximum length of any path for all the drones, aka the time taken for the last drone to reach its destination
        # maybe there's a neater way of doing this but it isn't computationally expensive so for now it's fine
        list_of_point_lengths = []
        for i in range(len(Vehicle_list)):
            n_points = len(Vehicle_list[i].path[:, 0])
            list_of_point_lengths.append(n_points)
        # time_steps_max stores the maximum amount of timesteps for any drone to reach its destination. time_steps_max*dt = t_max
        return max(list_of_point_lengths)

    def initial_plot(self, Vehicle_list, ax):
        for _v in range(len(Vehicle_list)):
            # define the current coordinates of the drone
            x, y, z = (
                Vehicle_list[_v].path[-1, 0],
                Vehicle_list[_v].path[-1, 1],
                Vehicle_list[_v].path[-1, 2],
            )
            self.positions[_v] = [x, y, z]
            # self.ghost_positions[_v] = [x,y,z]
            # print(positions, type(positions))
            # Plot default data
            # note that the comma operator is mandatory, it turns the ax.plot object into a tuple
            (f_d,) = ax.plot(
                Vehicle_list[_v].path[: self.time_steps_max, 0],
                Vehicle_list[_v].path[: self.time_steps_max, 1],
                linewidth=2,
            )
            # the line below is for adding an icon to the current vehicle position
            # also the 'x' at the end is the position marker, can be changed to other things
            (drone_icon,) = ax.plot(x, y, "x")
            # (ghost_drone_icon,) = ax.plot(x, y, "x")

            # plot the default warning circles
            # define the circle
            warning_circle = plt.Circle(
                (x, y), 0.25, fill=False, edgecolor="r", linewidth=2
            )
            # ghost_warning_circle = plt.Circle(
            #     (x, y), 0.25, fill=False, edgecolor="y", linewidth=2#,linestyle = "--"
            # )

            # add the circle to the plot
            ax.add_artist(warning_circle)
            # ax.add_artist(ghost_warning_circle)

            self.warning_circles.append(warning_circle)
            # self.ghost_warning_circles.append(ghost_warning_circle)

            self.plot_list.append(f_d)
            # append the references to the drone icons to the drone icon list
            self.drone_list.append(drone_icon)
            # self.ghost_drone_list.append(ghost_drone_icon)
            # the following two lines plot the start and end points
            ax.plot(Vehicle_list[_v].path[0, 0], Vehicle_list[_v].path[0, 1], "")
            ax.plot(Vehicle_list[_v].goal[0], Vehicle_list[_v].goal[1], "*")
        # Create your streamplot on the same axes
        X, Y, U, V = self.streamlines(plot_index=10000)
        self.stream = ax.streamplot(X, Y, U, V, color="b", linewidth=0.5)
        return None

    def streamlines(self, plot_index):
        drone_index = 2
        # Define your space
        X, Y = np.meshgrid(np.linspace(-5, 5, 100), np.linspace(-5, 5, 100))

        # Start with a zero potential field
        U = np.zeros_like(X)
        V = np.zeros_like(Y)

        # Let's assume we have the positions of other drones and the vehicle in two lists:
        # drones (list of tuples) and vehicle (a tuple)
        vehicle_1 = self.vehicle_list[drone_index]
        # all_drones = [v.position[:2] for v in vehicle_1.personal_vehicle_list]
        # print(self.vehicle_list[1].path[:plot_index])
        drones = [v.path[: plot_index + 1][-1][:2] for v in self.vehicle_list]

        drones = drones[:drone_index] + drones[drone_index + 1 :]
        # drones = [(x1, y1), (x2, y2), ..., (xn, yn)]  # Replace with actual positions
        vehicle_goal = vehicle_1.goal[:2]  # Replace with actual goal position

        # Define potential field parameters
        k_source = 1.0  # Source field strength (drones)
        k_sink = -5.0  # Sink field strength (vehicle's goal)

        # Calculate potential field due to each drone (source)
        for drone in drones:
            r = np.sqrt((X - drone[0]) ** 2 + (Y - drone[1]) ** 2)
            U += k_source * (X - drone[0]) / r**2
            V += k_source * (Y - drone[1]) / r**2

        # Calculate potential field due to vehicle's goal (sink)
        r = np.sqrt((X - vehicle_goal[0]) ** 2 + (Y - vehicle_goal[1]) ** 2)
        U += k_sink * (X - vehicle_goal[0]) / r**2
        V += k_sink * (Y - vehicle_goal[1]) / r**2

        return X, Y, U, V

    # Update values
    def update(self, val):
        # self.time_steps_max stores the maximum number of iterations it took for a drone to reach its destination. This is equivalent to time if ...
        # ...travelling at a constant speed. plot_until therefore is the current time value of the simulation.
        # Remove the old streamplot
        # self.ax.clear()
        # keep = lambda x: not isinstance(x, FancyArrowPatch)
        # self.ax.patches = [patch for patch in self.ax.patches if keep(patch)]
        # self.ax.patches = [patch for patch in self.ax.patches if not isinstance(patch, FancyArrowPatch)]
        # self.ax.patches = []
        # self.ax.patches.clear()
        plot_until = int(np.floor(self.slider.val * self.time_steps_max))
        # Draw the new streamplot
        # print(f"plot_until = {plot_until}")

        # self.stream.remove()
        # self.stream = stream
        for i in range(len(self.plot_list)):
            # we are now telling the code to plot the drone trajectories only until the value of the slider (or time)
            self.plot_list[i].set_data(
                self.vehicle_list[i].path[:plot_until, 0],
                self.vehicle_list[i].path[:plot_until, 1],
            )

            if plot_until == 0:
                # X,Y,U,V = self.streamlines(plot_index=plot_until)
                # self.stream = self.ax.streamplot(X, Y, U, V, color='b')
                # here is what we plot when the drones are at their starting positions
                # if t=0 we want to draw the drone icons at their starting points
                x, y, z = self.vehicle_list[i].path[0, :3]
                self.warning_circles[i].set_edgecolor("b")
            elif plot_until < len(self.vehicle_list[i].path[:, 0]):
                # here is what we plot during drone transit
                # if t < the time it takes for this drone to reach its destination, show the drone icon at its current position
                x, y, z = self.vehicle_list[i].path[plot_until - 1, :3]
                self.warning_circles[i].set_fill(False)
                self.warning_circles[i].set_edgecolor("g")
            else:
                # here is where we plot what we want once the drone is at its destination
                # if t >= time taken for the drone to reach its destination, ensure the drone icon is shown at its destination
                # to avoid indexing errors
                x, y, z = self.vehicle_list[i].path[-1, :3]
                # plt.Circle object has severable attributes that can be dynamically modified
                self.warning_circles[i].set_fill(True)
                self.warning_circles[i].set_facecolor("skyblue")
                self.warning_circles[i].set_edgecolor("b")
            self.drone_list[i].set_data(x, y)
            self.warning_circles[i].center = (x, y)
            self.positions[i] = [x, y, z]
        # now detect and handle collisions
        self.collision_handling()
        return self.plot_list + self.drone_list + self.warning_circles

    def collision_handling(self):
        """Figure out if there is a collision and what to display when collisions are encountered"""
        distance_matrix = np.sqrt(
            np.sum((self.positions[:, np.newaxis] - self.positions) ** 2, axis=-1)
        )
        # set collision threshold
        collision_threshold = 0.5
        for i in range(distance_matrix.shape[0]):
            for j in range(i + 1, distance_matrix.shape[1]):
                if distance_matrix[i, j] < collision_threshold:
                    # print(f"Collision detected between drones {i} and {j}")
                    self.warning_circles[i].set_edgecolor("r")
                    self.warning_circles[j].set_edgecolor("r")
                    # conflicts.update([i,j])
                    if self.conflict_iterator in self.conflicts.keys():
                        self.conflicts[self.conflict_iterator].append((i, j))
                    else:
                        self.conflicts[self.conflict_iterator] = [(i, j)]
        # the line below checks if there is there are any conflicts at the current iteration
        if self.conflict_iterator in self.conflicts.keys():
            # these are matplotlib.patch.Patch properties
            bounding_box = dict(
                boxstyle="round", facecolor="skyblue", edgecolor="r", alpha=1
            )
            # self.bounding_box['edgecolor'] = 'r'
            # self.bounding_box['facecolor'] = 'skyblue'
            textstr = f"Conflict detected!\nDrones {[drones for drones in self.conflicts[self.conflict_iterator]]}"
            # place a text box in upper left in axes coords
            # info_box = ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            #        verticalalignment='top', bbox=bounding_box,color = 'g')
            self.info_box.set_text(textstr)
            self.info_box.set_c("k")
            self.info_box.set_bbox(bounding_box)
            # print(f"there is a conflict, slider value = {val}")

            previous_conflicts = self.conflicts.get(self.conflict_iterator - 1)
            current_conflicts = self.conflicts.get(self.conflict_iterator)
            for conflict in current_conflicts:
                if self.conflict_iterator - 1 in self.conflicts:
                    # print(self.conflict_iterator,self.conflicts[self.conflict_iterator],self.conflicts[self.conflict_iterator-1])
                    if conflict not in previous_conflicts:
                        # print("Conflict already addressed, not stopping simulation.")
                        self.stop()
                else:
                    # print("No conflicts previously, should stop now")
                    self.stop()
        else:
            # no conflicts, set box to safe
            bounding_box = dict(
                boxstyle="round", facecolor="wheat", edgecolor="g", alpha=1
            )
            textstr = "Safe"
            # info_box = ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            #        verticalalignment='top', bbox=bounding_box,color = 'g')
            self.info_box.set_text(textstr)
            self.info_box.set_bbox(bounding_box)
            self.info_box.set_c("k")

        self.conflict_iterator += 1
        return None

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
        self.fig.canvas.draw_idle()
        return None

    # anim.event_source.stop()
    def stop(self):
        """function that can be called in the code to stop the animation"""
        # running is not a default attribute of the FuncAnimation object, but we have defined it ourselves lower down
        # self.animation_running:
        self.anim.event_source.stop()
        self.play_button.label.set_text("Play")
        self.animation_running = False
        # else:
        #     self.anim.event_source.start()
        #     self.play_button.label.set_text("Pause")
        #     self.animation_running = True
        # this line seems to update the plot. Without it, the Play and Pause will not update until the mouse leaves the button area.
        # plt.pause(0.1)
        self.fig.canvas.draw_idle()
        return None

    def on_press(self, event):
        """Allows the user to pause and play the animation with the spacebar"""
        sys.stdout.flush()
        if event.key == " ":
            self.play(event=None)
            self.fig.canvas.draw()
        return None

    def animate(self, i):
        """Function that updates the slider and calls the update function. i iterates from 0 to the number of frames"""
        # obtain the slider value to 2dp
        current_slider_value = round(self.slider.val, 2)
        # set i to the slider value so that the simulation stops when the slider reaches the end
        # it is 100x the slider value because the slider goes from 0 to 1 and the i from 0 to 100
        i = int(100 * current_slider_value)
        # print(f"i={i}")
        # increment the slider by 0.01 for every frame
        self.slider.set_val((current_slider_value + 0.01) % (self.slider.valmax + 0.01))
        # stop the animation when the slider reaches the end
        if i == 99:
            # calling the play function while the animation is running stops the animation
            self.play(event=None)
        # nothing to return I'm pretty sure :)
        return None

    def show(self):
        # show the plot
        plt.show()
        return None
