from gflow.arena import ArenaMap
from gflow.building import Building
from gflow.vehicle import Vehicle
from gflow.panel_flow import Flow_Velocity_Calculation
from time import sleep
import pdb
import numpy as np
import matplotlib.pyplot as plt

from cases import Cases

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


Arena  = ArenaMap(6,)
ArenaR = ArenaMap(6,)
Arena.Inflate(radius = 0.2) #0.1
Arena.Panelize(size= 0.01) #0.08
Arena.Calculate_Coef_Matrix(method = 'Vortex')

Case = Cases(117,Arena,'manual')
# Case = Cases(13,Arena,'manual')
Vehicle_list = Case.Vehicle_list

current_vehicle_list = Vehicle_list
for i in range (700):

    Flow_Vels = Flow_Velocity_Calculation(current_vehicle_list,Arena,method = 'Vortex')
    for index,vehicle in enumerate(current_vehicle_list):
        if vehicle.t >= i:
            pass
        else:
            pass
        vehicle.Update_Velocity(Flow_Vels[index],Arena)
        vehicle.Go_to_Goal(1.5,0,0,vehicle.Vinfmag)
        #vehicle.Go_to_Goal(1.5,(-1)**(index))
        #print('Vehicle ', str(index), 'AoA ', str(vehicle.AoA*180/np.pi) )
        if vehicle.state == 1:
            current_vehicle_list = current_vehicle_list[:index] + current_vehicle_list[index+1:]
            print(str(i))
            print('Vehicle ', str(index), 'has reached the goal')

plot_trajectories(Arena, ArenaR, Vehicle_list)
#EOF