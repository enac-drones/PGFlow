import numpy as np
import matplotlib.pyplot as plt


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
