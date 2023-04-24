import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
# Import animation package
from matplotlib.animation import FuncAnimation
# Import slider package
from matplotlib.widgets import Slider, Button
from mpl_interactions import *
import time
import sys



def plot_trajectories(Arena, ArenaR, Vehicle_list):
    fig = plt.figure(figsize=(5,5))
    minx = -5
    maxx = 5
    miny = -5
    maxy = 5
    plt.grid(color = 'k', linestyle = '-.', linewidth = 0.5)
    for building in Arena.buildings:
        plt.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
        plt.fill(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
    for buildingR in ArenaR.buildings:
        plt.plot(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
        plt.fill(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
    for _v in range(len(Vehicle_list)):
        plt.plot(Vehicle_list[_v].path[:,0],Vehicle_list[_v].path[:,1], linewidth = 2)
        plt.plot(Vehicle_list[_v].path[0,0],Vehicle_list[_v].path[0,1],'o')
        plt.plot(Vehicle_list[_v].goal[0],Vehicle_list[_v].goal[1],'x')
    plt.xlabel('East-direction --> (m)')
    plt.ylabel('North-direction --> (m)')
    plt.xlim([minx, maxx])
    plt.ylim([miny, maxy])
    plt.show()


def plot_trajectories1(Arena, ArenaR, Vehicle_list):
    #limit is the percentage of the plot you would like to have
    #plt.close('all')
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111)
    fig.subplots_adjust(bottom=0.1, top=0.9)

    
    

    # Create axes for sliders
    #variable inside add_axes is left, bottom, width, height
    ax_prog = fig.add_axes([0.3, 0.92, 0.4, 0.05])
    ax_prog.spines['top'].set_visible(True)
    ax_prog.spines['right'].set_visible(True)

    # Create sliders
    slider = Slider(ax=ax_prog, label='Progress ',valinit=5.0, valstep=0.001, valmin=0, valmax=1.0, valfmt=' %1.1f ', facecolor='#cc7000')

    # create the play button
    #play_ax = plt.axes([0.8, 0.92, 0.1, 0.05])
    play_ax = fig.add_axes([0.8, 0.92, 0.1, 0.05])
    play_button = Button(play_ax, 'Play', color='0.8', hovercolor='0.95')

    
    #####################################################################################
    #these control the size of the slider for some reason (at least in x)
    # minx = 0
    # maxx = 1
    # miny = -5
    # maxy = 5
    
    for building in Arena.buildings:
        print(f"building vertices are {(building.vertices[:,0],building.vertices[0,0])}")
        ax.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
        ax.fill(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
    for buildingR in ArenaR.buildings:
        ax.plot(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
        ax.fill(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
    
    #plot_list_dict = {}
    list_of_point_lengths = []
    for i in range(len(Vehicle_list)):
        n_points = len(Vehicle_list[i].path[:,0])
        list_of_point_lengths.append(n_points)
    n = max(list_of_point_lengths)

    #plot_list is a list that will hold the references to each trajectory plot
    plot_list = []
    #list to store (the references to) the drone icon plots 
    drone_list = []
    #same as above, but display these only when certain separation minima are not respected
    warning_circles = []
    for _v in range(len(Vehicle_list)):
        #define the current coordinates of the drone
        x, y = Vehicle_list[_v].path[-1,0],Vehicle_list[_v].path[-1,1]
        # Plot default data
        f_d, = ax.plot(Vehicle_list[_v].path[:n,0],Vehicle_list[_v].path[:n,1], linewidth = 2)
        #the line below is for adding an icon to the current vehicle position
        #also the 'x' at the end is the position marker, can be changed to other things
        drone_icon, = ax.plot(Vehicle_list[_v].path[-1,0],Vehicle_list[_v].path[-1,1],'x')
        #plot the default warning circles
        #circle1 = plt.Circle((x, y), 0.2, color = "r")
        # plot the circle
        warning_circle = plt.Circle((x, y), 0.2, fill=False, edgecolor="r", linewidth=2)
        ax.add_artist(warning_circle)
        #warning_circle, = ax.plot(x, y, 'ro')

        #warning_circle = ax.add_patch( circle1 )
        warning_circles.append(warning_circle)

        plot_list.append(f_d)
        #also uncomment the line below once drone_icon is fixed
        drone_list.append(drone_icon)
        #the following two lines plot the start and end points
        ax.plot(Vehicle_list[_v].path[0,0],Vehicle_list[_v].path[0,1],'')
        ax.plot(Vehicle_list[_v].goal[0],Vehicle_list[_v].goal[1],'*')

    # Update values
    def update(val):
        # scale val to be between 0 and 1 while the problem with the slider is not fixed
        # temp stores the current value of the slider (a float between 0 and 1)
        temp= slider.val
        # n stores the maximum number of iterations it took for a drone to reach its destination. This is equivalent to time if ...
        # travelling at a constant speed. plot_until therefore is the current time value of the simulation.
        plot_until = int(np.floor(temp*n))
        #print(f"plot_until is currently {plot_until}")
        for i in range(len(plot_list)):
            # we are now telling the code to plot the drone trajectories only until the value of the slider (or time)
            plot_list[i].set_data(Vehicle_list[i].path[:plot_until,0],Vehicle_list[i].path[:plot_until,1])
            if plot_until == 0:
                # if t=0 we want to draw the drone icons at their starting points
                drone_list[i].set_data(Vehicle_list[i].path[0,0],Vehicle_list[i].path[0,1])
                warning_circles[i].center = (Vehicle_list[i].path[0,0],Vehicle_list[i].path[0,1])
                #warning_circles[i].set_data(Vehicle_list[i].path[0,0],Vehicle_list[i].path[0,1])
            elif plot_until < len(Vehicle_list[i].path[:,0]):
                # if t < the time it takes for this drone to reach its destination, show the drone icon at its current position
                drone_list[i].set_data(Vehicle_list[i].path[plot_until-1,0],Vehicle_list[i].path[plot_until-1,1])
                warning_circles[i].center = (Vehicle_list[i].path[plot_until-1,0],Vehicle_list[i].path[plot_until-1,1])
                warning_circles[i].set_fill(False)
                warning_circles[i].set_edgecolor("g")
            else:
                # here is where we plot what we want once the drone is at its destination
                # if t >= time taken for the drone to reach its destination, ensure the drone icon is shown at its destination
                # to avoid indexing errors
                drone_list[i].set_data(Vehicle_list[i].path[-1,0],Vehicle_list[i].path[-1,1])
                # plt.Circle object has severable attributes that can be dynamically modified
                warning_circles[i].center = (Vehicle_list[i].path[-1,0],Vehicle_list[i].path[-1,1])
                warning_circles[i].set_fill(True)
                warning_circles[i].set_facecolor("b")

        fig.canvas.draw_idle()

    # define play function
    def play(event):
        for val in np.linspace(0, 1, 100):
            slider.set_val(val)
            update(val)
            #fig.canvas.draw_idle()
            plt.pause(0.01)
        #play(event)

    slider.on_changed(update)
    play_button.on_clicked(play)
    




    #everything with plt. is not necessarily working due to the subfigure situation, will fix
    #plt.xlabel('East-direction --> (m)')
    #plt.ylabel('North-direction --> (m)')
    #plt.xlim([minx, maxx])
    #plt.ylim([miny, maxy])
    ax.set_xlim([-5, 5])
    ax.set_ylim([-5, 5])
    ax.set_box_aspect(1)
    ax.set_xlabel('East --> (m)')
    ax.set_ylabel('North --> (m)')
    #print("we are here")
    ax.grid(color = 'k', linestyle = '-', linewidth = 0.5,which = "major")
    ax.grid(color = 'k', linestyle = ':', linewidth = 0.5,which = "minor")
    #ax.grid(True)
    ax.minorticks_on()
    plt.show()


###################################################################################

class plot_trajectories2:
    '''Same as above but trying to use the FuncAnimation for the play button implementation which supposedly uses less CPU'''
    def __init__(self, Arena, ArenaR, Vehicle_list):
        self.Arena = Arena
        self.ArenaR = ArenaR
        self.Vehicle_list = Vehicle_list
        #plt.close('all')
        self.fig,self.ax = self.plot_setup()
        self.slider = self.create_slider(fig = self.fig)
        self.play_button = self.create_button(fig=self.fig)
        self.info_box = self.create_info_box(ax = self.ax)
        self.plot_buildings(ax=self.ax,Arena = self.Arena, ArenaR = self.ArenaR)
        self.time_steps_max=self.get_max_timesteps(self.Vehicle_list)

        #plot_list is a list that will hold the references to each trajectory plot
        self.plot_list = []
        #list to store (the references to) the drone icon plots 
        self.drone_list = []
        #same as above, but display these only when certain separation minima are not respected
        self.warning_circles = []
        #initialize empty array to store vehicle positions
        self.positions = np.zeros((len(Vehicle_list), 3))
        self.initial_plot(Vehicle_list=self.Vehicle_list,ax= self.ax)

        #this variable will increase by 1 every time a collision is detected
        self.conflict_iterator = 0
        self.conflicts = {}
        self.conflicts["addressed"] = []
        #create new set to hold the conflicts that have already caused the simulation to pause:
        #addressed_conflicts = set()
        #connect the action of pressing the spacebar to the result we want it to have
        self.fig.canvas.mpl_connect('key_press_event', self.on_press)
        # Create the animation object, it starts automatically against my will BUG
        self.anim = FuncAnimation(self.fig, self.animate, interval=50, frames = 101,init_func=None,blit = False,repeat=True, repeat_delay=1000)
    
        #tell the slider to update the plot when it is moved
        self.slider.on_changed(self.update)
        #call the play function when the button is pressed (to play or pause the animation)
        self.play_button.on_clicked(self.play)
        
        #again this line updates the plot, without it, the animation starts by default even though we have anim.event_source.stop()
        #perhaps there is a better way of doing this that I am not aware of. 
        #plt.pause(0.1)
        #the line below also appears to do the trick, and better
        self.fig.canvas.draw()

        #these three lines are a bit of a hack to stop the simulation which for some reason automatically starts BUG
        self.animation_running = True
        self.play(event=None)
        self.slider.set_val(0.0)
        #fig.canvas.draw_idle()

    def plot_setup(self):
        fig = plt.figure(figsize=(8,8))
        ax = fig.add_subplot(111)
        fig.subplots_adjust(bottom=0.1, top=0.9)
        
        ax.set_xlim([-5, 5])
        ax.set_ylim([-5, 5])
        ax.set_box_aspect(1)
        ax.set_xlabel('East --> (m)')
        ax.set_ylabel('North --> (m)')
        ax.grid(color = 'k', linestyle = '-', linewidth = 0.5,which = "major")
        ax.grid(color = 'k', linestyle = ':', linewidth = 0.5,which = "minor")
        #ax.grid(True)
        ax.minorticks_on()
        return fig,ax
    
    def create_slider(self,fig):
        # Create axes for sliders
        #variable inside add_axes is left, bottom, width, height
        ax_prog = fig.add_axes([0.3, 0.92, 0.4, 0.05])
        ax_prog.spines['top'].set_visible(True)
        ax_prog.spines['right'].set_visible(True)

        # Create slider object to iterate through the plot
        slider = Slider(ax=ax_prog, label='Progress ',valinit=5.0, valstep=0.001, valmin=0, valmax=1.0, valfmt=' %1.1f ', facecolor='#cc7000')
        return slider
    
    def create_button(self, fig):
        # create the play button axis object
        play_ax = fig.add_axes([0.8, 0.92, 0.1, 0.05])
        #create a play button at the location of the axis object
        play_button = Button(play_ax, 'Play', color='0.8', hovercolor='0.95')
        return play_button
    
    def create_info_box(self, ax):
        # these are matplotlib.patch.Patch properties
        bounding_box = dict(boxstyle='round', facecolor='wheat',edgecolor = 'g', alpha=1)
        textstr = 'Safe'
        # place a text box in upper left in axes coords
        info_box = ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
                verticalalignment='top', bbox=bounding_box,color = 'g')
        return info_box
    
    def plot_buildings(self,ax,Arena,ArenaR):
        for building in Arena.buildings:
            print(f"building vertices are {(building.vertices[:,0],building.vertices[0,0])}")
            ax.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
            ax.fill(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'salmon', alpha=0.5 )
        for buildingR in ArenaR.buildings:
            ax.plot(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
            ax.fill(     np.hstack((buildingR.vertices[:,0],buildingR.vertices[0,0]))  , np.hstack((buildingR.vertices[:,1],buildingR.vertices[0,1] )) ,'m' )
        return None
        
    def get_max_timesteps(self,Vehicle_list):
        #these few lines obtain the maximum length of any path for all the drones, aka the time taken for the last drone to reach its destination
        #maybe there's a neater way of doing this but it isn't computationally expensive so for now it's fine
        list_of_point_lengths = []
        for i in range(len(Vehicle_list)):
            n_points = len(Vehicle_list[i].path[:,0])
            list_of_point_lengths.append(n_points)
        #time_steps_max stores the maximum amount of timesteps for any drone to reach its destination. time_steps_max*dt = t_max
        return max(list_of_point_lengths)
    
    def initial_plot(self,Vehicle_list,ax):
        for _v in range(len(Vehicle_list)):
            #define the current coordinates of the drone
            x, y, z = Vehicle_list[_v].path[-1,0],Vehicle_list[_v].path[-1,1],Vehicle_list[_v].path[-1,2]
            self.positions[_v] = [x,y,z]
            #print(positions, type(positions))
            # Plot default data
            #note that the comma operator is mandatory, it turns the ax.plot object into a tuple
            f_d, = ax.plot(Vehicle_list[_v].path[:self.time_steps_max,0],Vehicle_list[_v].path[:self.time_steps_max,1], linewidth = 2)
            #the line below is for adding an icon to the current vehicle position
            #also the 'x' at the end is the position marker, can be changed to other things
            drone_icon, = ax.plot(x,y,'x')

            #plot the default warning circles
            # define the circle
            warning_circle = plt.Circle((x, y), 0.25, fill=False, edgecolor="r", linewidth=2)
            #add the circle to the plot
            ax.add_artist(warning_circle)

            self.warning_circles.append(warning_circle)

            self.plot_list.append(f_d)
            #append the references to the drone icons to the drone icon list
            self.drone_list.append(drone_icon)
            #the following two lines plot the start and end points
            ax.plot(Vehicle_list[_v].path[0,0],Vehicle_list[_v].path[0,1],'')
            ax.plot(Vehicle_list[_v].goal[0],Vehicle_list[_v].goal[1],'*')
        return None
    # Update values
    def update(self,val):
        # scale val to be between 0 and 1 while the problem with the slider is not fixed
        # temp stores the current value of the slider (a float between 0 and 1)
        temp= self.slider.val
        # n stores the maximum number of iterations it took for a drone to reach its destination. This is equivalent to time if ...
        # ...travelling at a constant speed. plot_until therefore is the current time value of the simulation.
        plot_until = int(np.floor(temp*self.time_steps_max))
        #print(f"plot_until is currently {plot_until}")
        for i in range(len(self.plot_list)):
            # we are now telling the code to plot the drone trajectories only until the value of the slider (or time)
            self.plot_list[i].set_data(self.Vehicle_list[i].path[:plot_until,0],self.Vehicle_list[i].path[:plot_until,1])

            if plot_until == 0:
                # here is what we plot when the drones are at their starting positions
                # if t=0 we want to draw the drone icons at their starting points
                x,y,z = self.Vehicle_list[i].path[0,:3]
                self.warning_circles[i].set_edgecolor("b")
            elif plot_until < len(self.Vehicle_list[i].path[:,0]):
                #here is what we plot during drone transit
                # if t < the time it takes for this drone to reach its destination, show the drone icon at its current position
                x,y,z = self.Vehicle_list[i].path[plot_until-1,:3]
                self.warning_circles[i].set_fill(False)
                self.warning_circles[i].set_edgecolor("g")
            else:
                # here is where we plot what we want once the drone is at its destination
                # if t >= time taken for the drone to reach its destination, ensure the drone icon is shown at its destination
                # to avoid indexing errors
                x,y,z = self.Vehicle_list[i].path[-1,:3]
                # plt.Circle object has severable attributes that can be dynamically modified
                self.warning_circles[i].set_fill(True)
                self.warning_circles[i].set_facecolor("skyblue")
                self.warning_circles[i].set_edgecolor("b")
            self.drone_list[i].set_data(x,y)
            self.warning_circles[i].center = (x,y)
            self.positions[i] = [x,y,z]
        distance_matrix = np.sqrt(np.sum((self.positions[:, np.newaxis] - self.positions) ** 2, axis=-1))
        # set collision threshold
        collision_threshold = 0.5
        
        for i in range(distance_matrix.shape[0]):
            for j in range(i+1, distance_matrix.shape[1]):
                if distance_matrix[i,j] < collision_threshold:
                    #print(f"Collision detected between drones {i} and {j}")
                    self.warning_circles[i].set_edgecolor("r")
                    self.warning_circles[j].set_edgecolor("r")
                    #conflicts.update([i,j])
                    if self.conflict_iterator in self.conflicts.keys():
                        self.conflicts[self.conflict_iterator].append((i,j))
                    else:
                        self.conflicts[self.conflict_iterator]=[(i,j)]
        #the line below checks if there is there are any conflicts at the current iteration                
        if self.conflict_iterator in self.conflicts.keys():
            # these are matplotlib.patch.Patch properties
            bounding_box = dict(boxstyle='round', facecolor='skyblue',edgecolor = 'r', alpha=1)
            #self.bounding_box['edgecolor'] = 'r'
            #self.bounding_box['facecolor'] = 'skyblue'
            textstr = f"Conflict detected!\nDrones {[drones for drones in self.conflicts[self.conflict_iterator]]}"
            # place a text box in upper left in axes coords
            #info_box = ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            #        verticalalignment='top', bbox=bounding_box,color = 'g')
            self.info_box.set_text(textstr)
            self.info_box.set_c("k")
            self.info_box.set_bbox(bounding_box)
            #print(f"there is a conflict, slider value = {val}")

            for conflict in self.conflicts[self.conflict_iterator]:
                if int(self.conflict_iterator-1) in self.conflicts.keys():
                    #print(self.conflict_iterator,self.conflicts[self.conflict_iterator],self.conflicts[self.conflict_iterator-1])
                    if conflict in self.conflicts[self.conflict_iterator-1]:
                        #print("Conflict already addressed, not stopping simulation.")
                        pass
                    else:
                        #self.conflicts["addressed"].append(conflict)
                        #this will pause the simulation to draw attention to the conflict
                        #print(f"Animation is running? {self.animation_running}")
                        print("simulation should stop")
                        self.stop()
                else:
                    print("No conflicts previously, should stop now")
                    self.stop()
        else:
            #self.bounding_box['edgecolor'] = 'g'
            #self.bounding_box['facecolor'] = 'wheat'
            bounding_box = dict(boxstyle='round', facecolor='wheat',edgecolor = 'g', alpha=1)
            textstr = f"Safe"
            #info_box = ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            #        verticalalignment='top', bbox=bounding_box,color = 'g')
            self.info_box.set_text(textstr)
            self.info_box.set_bbox(bounding_box)
            self.info_box.set_c("k")
        
        self.conflict_iterator+=1
        return self.plot_list + self.drone_list + self.warning_circles

    
    #anim.event_source.stop()
    def play(self,event):
        '''Function that is called every time the play button is pressed. It will alternate between play and pause and start/stop the animation'''
        #running is not a default attribute of the FuncAnimation object, but we have defined it ourselves lower down
        if self.animation_running:
            self.anim.event_source.stop()
            self.play_button.label.set_text("Play")
            self.animation_running = False
        else:
            self.anim.event_source.start()
            self.play_button.label.set_text("Pause")
            self.animation_running = True
        # this line seems to update the plot. Without it, the Play and Pause will not update until the mouse leaves the button area.
        #plt.pause(0.1)
        self.fig.canvas.draw_idle()
        return None

    #anim.event_source.stop()
    def stop(self):
        '''function that can be called in the code to stop the animation'''
        #running is not a default attribute of the FuncAnimation object, but we have defined it ourselves lower down
        #self.animation_running:
        self.anim.event_source.stop()
        self.play_button.label.set_text("Play")
        self.animation_running = False
        # else:
        #     self.anim.event_source.start()
        #     self.play_button.label.set_text("Pause")
        #     self.animation_running = True
        # this line seems to update the plot. Without it, the Play and Pause will not update until the mouse leaves the button area.
        #plt.pause(0.1)
        self.fig.canvas.draw_idle()
        return None

    def on_press(self,event):
        '''Allows the user to pause and play the animation with the spacebar'''
        sys.stdout.flush()
        if event.key == ' ':
            self.play(event=None)
            self.fig.canvas.draw()
        return None

    


    def animate(self,i):
        '''Function that updates the slider and calls the update function. i iterates from 0 to the number of frames'''
        #obtain the slider value to 2dp
        current_slider_value = round(self.slider.val,2)
        #set i to the slider value so that the simulation stops when the slider reaches the end
        #it is 100x the slider value because the slider goes from 0 to 1 and the i from 0 to 100
        i = int(100*current_slider_value)
        #print(f"i={i}")
        #increment the slider by 0.01 for every frame
        self.slider.set_val((current_slider_value + 0.01) % (self.slider.valmax+0.01))
        #stop the animation when the slider reaches the end
        if i==99:
            #calling the play function while the animation is running stops the animation
            self.play(event=None)
        #nothing to return I'm pretty sure :)
        return None

    def show(self):
        #show the plot
        plt.show()
        return None

