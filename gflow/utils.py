import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
# Import animation package
from matplotlib.animation import FuncAnimation
# Import slider package
from matplotlib.widgets import Slider


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
    fig = plt.figure(figsize=(5,5))
    ax = fig.add_subplot(111)
    fig.subplots_adjust(bottom=0.1, top=0.9)
    ax.set_xlim([-5, 5])
    ax.set_ylim([-5, 5])
    ax.set_box_aspect(1)

    # Create axes for sliders
    #variable inside add_axes is left, bottom, width, height
    #ax_prog = fig.add_axes([0.3, 0.85, 0.4, 0.05])
    #ax_prog.spines['top'].set_visible(True)
    #ax_prog.spines['right'].set_visible(True)
    #ax_prog.set_ylim([0, 1.0])
    ax_prog = fig.add_axes([0.3, 0.92, 0.4, 0.05])
    ax_prog.spines['top'].set_visible(True)
    ax_prog.spines['right'].set_visible(True)

    # Create sliders
    s_prog = Slider(ax=ax_prog, label='Progress ',valinit=5.0, valstep=0.01, valmin=0, valmax=1.0, valfmt=' %1.1f ', facecolor='#cc7000')

    #s_prog = Slider(ax=ax_prog, label='Temperature ', valmin=0, valmax=1, valinit=0.5, valfmt='%i K', facecolor='#cc7000')
    
    # Plot default data
    #x = np.linspace(-0, 1, 100)
    #Ef_0 = 0.5
    #T_0 = 100
    #y = fermi(x, Ef_0, T_0)
    #f_d, = ax.plot(x, y, linewidth=2.5)

    
    #s_T.on_changed(update)
    #####################################################################################
    minx = 0
    maxx = 1
    miny = -5
    maxy = 5
    plt.grid(color = 'k', linestyle = '-.', linewidth = 0.5)
    for building in Arena.buildings:
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
    drone_list = []
    for _v in range(len(Vehicle_list)):
        #n = len(Vehicle_list[_v].path[:,0])
        #plot_until = int(np.floor(limit*n))
        #print(f"length of path is {n}",f"we are plotting until {plot_until}")
        #the line below plots the path
        # Plot default data

        f_d, = ax.plot(Vehicle_list[_v].path[:n,0],Vehicle_list[_v].path[:n,1], linewidth = 2)
        #the line below is for adding an icon to the current vehicle position, it works but there are some issues to fix
        #so for now it is commented
        #drone_icon, = ax.plot(Vehicle_list[_v].path[-1,0],Vehicle_list[_v].path[-1,1],'o')
        plot_list.append(f_d)
        #also uncomment the line below once drone_icon is fixed
        #drone_list.append(drone_icon)
        #the following two lines plot the start and end points
        ax.plot(Vehicle_list[_v].path[0,0],Vehicle_list[_v].path[0,1],'o')
        ax.plot(Vehicle_list[_v].goal[0],Vehicle_list[_v].goal[1],'x')

    # Update values
    def update(val):
        #scale val to be between 0 and 1 while the problem with the slider is not fixed
        #temp = (s_prog.val+5)/10
        temp= s_prog.val
        #T = s_T.val
        #f_d.set_data(x, fermi(x, Ef, T))
        #list_of_point_lengths = []
        #for i in range(len(Vehicle_list)):
        #    n_points = len(Vehicle_list[i].path[:,0])
        #    list_of_point_lengths.append(n_points)
        #n = max(list_of_point_lengths)
        #n = len(Vehicle_list[_v].path[:,0])
        plot_until = int(np.floor(temp*n))
        for i in range(len(plot_list)):
            #f_d.set_data(Vehicle_list[_v].path[:plot_until,0],Vehicle_list[_v].path[:plot_until,1])
            plot_list[i].set_data(Vehicle_list[i].path[:plot_until,0],Vehicle_list[i].path[:plot_until,1])
            #drone_list[i].set_data(Vehicle_list[i].path[plot_until-1,0],Vehicle_list[i].path[plot_until-1,1])

        fig.canvas.draw_idle()

    s_prog.on_changed(update)

    plt.xlabel('East-direction --> (m)')
    plt.ylabel('North-direction --> (m)')
    plt.xlim([minx, maxx])
    plt.ylim([miny, maxy])
    #print("we are here")
    plt.show()
