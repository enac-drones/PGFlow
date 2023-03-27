
import numpy as np
from numpy import linalg
import math
import matplotlib.pyplot as plt
import pyclipper
from shapely.geometry import Point, Polygon
from datetime import datetime
from itertools import compress

from building import Building
# from vehicle import Vehicle
import pdb

from scipy.spatial import ConvexHull

"""# Velocity Calculation"""

def Flow_Velocity_Calculation(vehicles, arenamap, method = 'Vortex', update_velocities = True):

    starttime = datetime.now()

    # Calculating unknown vortex strengths using panel method:
    for f,vehicle in enumerate(vehicles):
        # Remove current vehicle from vehicle list.
        othervehicleslist = vehicles[:f] + vehicles[f+1:]

        # Remove buildings with heights below cruise altitue:
        vehicle.altitude_mask = np.zeros(( len(arenamap.buildings) )) #, dtype=int)
        for index,panelledbuilding in enumerate(arenamap.buildings):
            if (panelledbuilding.vertices[:,2] > vehicle.altitude).any():
                vehicle.altitude_mask[index] = 1
        related_buildings = list(compress(arenamap.buildings,vehicle.altitude_mask))

        # Vortex strenght calculation (related to panels of each building):
        for building in related_buildings:
            building.gamma_calc(vehicle,othervehicleslist,arenamap,method = method)

    #--------------------------------------------------------------------
    # Flow velocity calculation given vortex strengths:
    flow_vels = np.zeros([len(vehicles),3])

    # Wind velocity
    #U_wind = arenamap.wind[0] #* np.ones([len(vehicles),1])
    #V_wind = arenamap.wind[1] #* np.ones([len(vehicles),1])

    V_gamma   = np.zeros([len(vehicles),2]) # Velocity induced by vortices
    V_sink    = np.zeros([len(vehicles),2]) # Velocity induced by sink element
    V_source  = np.zeros([len(vehicles),2]) # Velocity induced by source elements
    V_sum     = np.zeros([len(vehicles),2]) # V_gamma + V_sink + V_source
    V_normal  = np.zeros([len(vehicles),2]) # Normalized velocity
    V_flow    = np.zeros([len(vehicles),2]) # Normalized velocity inversly proportional to magnitude
    V_norm    = np.zeros([len(vehicles),1]) # L2 norm of velocity vector

    W_sink    = np.zeros([len(vehicles),1]) # Velocity induced by 3-D sink element
    W_source  = np.zeros([len(vehicles),1]) # Velocity induced by 3-D source element
    W_flow    = np.zeros([len(vehicles),1]) # Vertical velocity component (to be used in 3-D scenarios)
    W_sum     = np.zeros([len(vehicles),1])
    W_norm    = np.zeros([len(vehicles),1])
    W_normal  = np.zeros([len(vehicles),1])

    for f,vehicle in enumerate(vehicles):

        # Remove current vehicle from vehicle list
        othervehicleslist = vehicles[:f] + vehicles[f+1:]

        # Velocity induced by 2D point sink, eqn. 10.2 & 10.3 in Katz & Plotkin:
        V_sink[f,0] = (-vehicle.sink_strength*(vehicle.position[0]-vehicle.goal[0]))/(2*np.pi*((vehicle.position[0]-vehicle.goal[0])**2+(vehicle.position[1]-vehicle.goal[1])**2))
        V_sink[f,1] = (-vehicle.sink_strength*(vehicle.position[1]-vehicle.goal[1]))/(2*np.pi*((vehicle.position[0]-vehicle.goal[0])**2+(vehicle.position[1]-vehicle.goal[1])**2))
        # Velocity induced by 3-D point sink. Katz&Plotkin Eqn. 3.25
        W_sink[f,0] = (-vehicle.sink_strength*(vehicle.position[2]-vehicle.goal[2]))/(4*np.pi*(((vehicle.position[0]-vehicle.goal[0])**2+(vehicle.position[1]-vehicle.goal[1])**2+(vehicle.position[2]-vehicle.goal[2])**2)**1.5))

        # Velocity induced by 2D point source, eqn. 10.2 & 10.3 in Katz & Plotkin:
        source_gain = 0
        for othervehicle in othervehicleslist:
            V_source[f,0] += (othervehicle.source_strength*(vehicle.position[0]-othervehicle.position[0]))/(2*np.pi*((vehicle.position[0]-othervehicle.position[0])**2+(vehicle.position[1]-othervehicle.position[1])**2))
            V_source[f,1] += (othervehicle.source_strength*(vehicle.position[1]-othervehicle.position[1]))/(2*np.pi*((vehicle.position[0]-othervehicle.position[0])**2+(vehicle.position[1]-othervehicle.position[1])**2))
            W_source[f,0] += (source_gain*othervehicle.source_strength*(vehicle.position[2]-othervehicle.position[2]))/(4*np.pi*((vehicle.position[0]-othervehicle.position[0])**2+(vehicle.position[1]-othervehicle.position[1])**2+(vehicle.position[2]-othervehicle.position[2])**2)**(3/2))

        if method == 'Vortex':
            for building in arenamap.buildings:
                u = np.zeros((building.nop,1))
                v = np.zeros((building.nop,1))
                polygon = Polygon(building.vertices)
                point = Point(vehicle.position[0],vehicle.position[1])
                #print('Vehicle' + str(f))
                #print(point)
                #print(polygon)
                if polygon.contains(point) == True:
                    #print(polygon.contains(point))
                    V_gamma[f,0] = V_gamma[f,0] + 0
                    V_gamma[f,1] = V_gamma[f,1] + 0
                    #print(polygon.contains(point))
                elif polygon.contains(point) == False:
                    #print(polygon.contains(point))
                    if vehicle.ID in building.gammas.keys():
                        # Velocity induced by vortices on each panel:

                        u = ( building.gammas[vehicle.ID][:].T/(2*np.pi))  *((vehicle.position[1]-building.pcp[:,1]) /((vehicle.position[0]-building.pcp[:,0])**2+(vehicle.position[1]-building.pcp[:,1])**2)) ####
                        v = (-building.gammas[vehicle.ID][:].T/(2*np.pi))  *((vehicle.position[0]-building.pcp[:,0]) /((vehicle.position[0]-building.pcp[:,0])**2+(vehicle.position[1]-building.pcp[:,1])**2))
                        V_gamma[f,0] = V_gamma[f,0] + np.sum(u)
                        V_gamma[f,1] = V_gamma[f,1] + np.sum(v)

        elif method == 'Source':
            for building in arenamap.buildings:
                u = np.zeros((building.nop,1))
                v = np.zeros((building.nop,1))
                polygon = Polygon(building.vertices)
                point = Point(vehicle.position[0],vehicle.position[1])
                #print('Vehicle' + str(f))
                #print(point)
                #print(polygon)
                if polygon.contains(point) == True:
                    #print(polygon.contains(point))
                    V_gamma[f,0] = V_gamma[f,0] + 0
                    V_gamma[f,1] = V_gamma[f,1] + 0
                    #print(polygon.contains(point))
                elif polygon.contains(point) == False:
                    #print(polygon.contains(point))
                    if vehicle.ID in building.gammas.keys():
                        # Velocity induced by vortices on each panel:

                        u = ( building.gammas[vehicle.ID][:].T/(2*np.pi))  *((vehicle.position[1]-building.pcp[:,1]) /((vehicle.position[0]-building.pcp[:,0])**2+(vehicle.position[1]-building.pcp[:,1])**2)) ####
                        v = (-building.gammas[vehicle.ID][:].T/(2*np.pi))  *((vehicle.position[0]-building.pcp[:,0]) /((vehicle.position[0]-building.pcp[:,0])**2+(vehicle.position[1]-building.pcp[:,1])**2))
                        V_gamma[f,0] = V_gamma[f,0] + np.sum(u)
                        V_gamma[f,1] = V_gamma[f,1] + np.sum(v)
        elif method == 'Hybrid':
            pass

########## !!!!!!FIX THIS!!!!!!!##########
##########  0*vehicle.V_inf[0] ###########
##########################################

        # Total velocity induced by all elements on map:
        V_sum[f,0] = V_gamma[f,0] + V_sink[f,0] + 0*vehicle.V_inf[0] + V_source[f,0]
        V_sum[f,1] = V_gamma[f,1] + V_sink[f,1] + 0*vehicle.V_inf[1] + V_source[f,1]

        # L2 norm of flow velocity:
        V_norm[f] = (V_sum[f,0]**2 + V_sum[f,1]**2)**0.5
        # Normalized flow velocity:
        V_normal[f,0] = V_sum[f,0]/V_norm[f]
        V_normal[f,1] = V_sum[f,1]/V_norm[f]

        # Flow velocity inversely proportional to velocity magnitude:
        V_flow[f,0] = V_normal[f,0]/V_norm[f]
        V_flow[f,1] = V_normal[f,1]/V_norm[f]

        # Add wind disturbance
        #V_flow[f,0] = V_flow[f,0] + U_wind
        #V_flow[f,1] = V_flow[f,0] + V_wind

        W_sum[f] = W_sink[f] + W_source[f]
        if W_sum[f] != 0.:
                W_norm[f] = (W_sum[f]**2)**0.5
                W_normal[f] = W_sum[f] /W_norm[f]
                W_flow[f] = W_normal[f]/W_norm[f]
                W_flow[f] = np.clip(W_flow[f],-0.07, 0.07)
        else:
                W_flow[f] = W_sum[f]

        flow_vels[f,:] = [V_flow[f,0], V_flow[f,1], W_flow[f,0]]
        #flow_vels[f,:] = [V_flow[f,0] + arenamap.wind[0]/(1.35*1.35), V_flow[f,1] + arenamap.wind[1]/(1.35*1.35), W_flow[f,0]]


    return flow_vels
