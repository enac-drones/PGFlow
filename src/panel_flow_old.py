import numpy as np

# from numpy import linalg
# import math
# import matplotlib.pyplot as plt
# import pyclipper
from shapely.geometry import Point, Polygon

# from datetime import datetime
from itertools import compress
from typing import List

from src.building import Building

# from src.vehicle import Vehicle
from src.arena import ArenaMap
from src.building import Building

# from vehicle import Vehicle
# import pdb

# from scipy.spatial import ConvexHull

"""# Velocity Calculation"""


def create_other_vehicles_list(vehicles, current_index: int):
    return vehicles[:current_index] + vehicles[current_index + 1 :]


def calculate_vortex_strengths(vehicles, arenamap: ArenaMap, method):
    for f, vehicle in enumerate(vehicles):
        # Remove current vehicle from vehicle list.
        othervehicleslist = create_other_vehicles_list(vehicles, current_index=f)
        # Remove buildings with heights below cruise altitue:
        vehicle.altitude_mask = altitude_mask(vehicle, arenamap)
        # related_buildings keeps only the buildings for which the altitude_mask is 1, ie buildings that are higher than the altitude...
        # ... of the vehicle in question
        related_buildings = list(compress(arenamap.buildings, vehicle.altitude_mask))
        # Vortex strength calculation (related to panels of each building):
        for building in related_buildings:
            building.gamma_calc(vehicle, othervehicleslist, arenamap, method=method)


def altitude_mask(vehicle, arenamap: ArenaMap):
    mask = np.zeros((len(arenamap.buildings)))
    for index, panelledbuilding in enumerate(arenamap.buildings):
        if (panelledbuilding.vertices[:, 2] > vehicle.altitude).any():
            mask[index] = 1
    return mask


def squared_distance_to_sink2D(vehicle):
    vector2d = (vehicle.position - vehicle.goal)[:2]
    return squared_vector_magnitude(vector2d)


def squared_distance_to_sink3D(vehicle):
    vector3d = vehicle.position - vehicle.goal
    return squared_vector_magnitude(vector3d)


def vector_to_sink(vehicle):
    return vehicle.position - vehicle.goal


def induced_sink_velocity2D(vehicle):
    induced_v = (
        -vehicle.sink_strength
        * vector_to_sink(vehicle)[:2]
        / (2 * np.pi * squared_distance_to_sink2D(vehicle))
    )
    return induced_v


def induced_sink_velocity3D(vehicle):
    induced_v = (-vehicle.sink_strength * (vector_to_sink(vehicle))) / (
        4 * np.pi * (squared_distance_to_sink3D(vehicle) ** 1.5)
    )
    return induced_v


def squared_distance_between_vehicles2D(vehicle1, vehicle2):
    position_diff = vehicle1.position[:2] - vehicle2.position[:2]
    squared_distance = squared_vector_magnitude(position_diff)
    return squared_distance


def vector_between_vehicles(vehicle1, vehicle2):
    """Returns the np array FROM vehicle2 TO vehicle1"""
    return vehicle1.position - vehicle2.position


def squared_vector_magnitude(vector):
    return np.sum(vector**2)


def induced_source_velocity2D(affected_vehicle, source_vehicle):
    vector_from_source_to_affected = vector_between_vehicles(
        affected_vehicle, source_vehicle
    )[:2]
    squared_distance = squared_vector_magnitude(vector_from_source_to_affected)
    induced_v = (source_vehicle.source_strength * vector_from_source_to_affected) / (
        2 * np.pi * squared_distance
    )
    return induced_v


def induced_source_velocity3D(affected_vehicle, source_vehicle):
    vector_from_source_to_affected = vector_between_vehicles(
        affected_vehicle, source_vehicle
    )
    squared_distance = squared_vector_magnitude(vector_from_source_to_affected)
    induced_v = (source_vehicle.source_strength * vector_from_source_to_affected) / (
        4 * np.pi * squared_distance ** (3 / 2)
    )
    return induced_v


def induced_vortex_velocity(affected_vehicle, source_vehicle):
    """this is not a real mathematical vortex, it just points perpendicular"""
    vector_from_source_to_affected = vector_between_vehicles(
        affected_vehicle, source_vehicle
    )[:2]
    squared_distance = squared_vector_magnitude(vector_from_source_to_affected)
    induced_v = (source_vehicle.source_strength / 4.0 / (2 * np.pi)) * (
        vector_from_source_to_affected / squared_distance
    )
    # make the vector point perpendicular
    return induced_v[::-1]


def Flow_Velocity_Calculation(
    vehicles, arenamap, method="Vortex", update_velocities=True
):
    # when simple_sim is called, vehicles is self.vehicle_list, ie the current vehicle's own list of vehicles
    # starttime = datetime.now()

    # Calculating unknown vortex strengths using panel method:
    calculate_vortex_strengths(vehicles, arenamap, method)

    # --------------------------------------------------------------------
    # Flow velocity calculation given vortex strengths:
    flow_vels = np.zeros([len(vehicles), 3])

    # Wind velocity
    # U_wind = arenamap.wind[0] #* np.ones([len(vehicles),1])
    # V_wind = arenamap.wind[1] #* np.ones([len(vehicles),1])

    V_gamma = np.zeros([len(vehicles), 2])  # Velocity induced by vortices
    V_sink = np.zeros([len(vehicles), 2])  # Velocity induced by sink element
    V_source = np.zeros([len(vehicles), 2])  # Velocity induced by source elements
    V_vortex = np.zeros(
        [len(vehicles), 2]
    )  # Velocity induced by votex elements of the vehicles
    V_sum = np.zeros([len(vehicles), 2])  # V_gamma + V_sink + V_source +V_vortex
    V_normal = np.zeros([len(vehicles), 2])  # Normalized velocity
    V_flow = np.zeros(
        [len(vehicles), 2]
    )  # Normalized velocity inversly proportional to magnitude
    V_norm = np.zeros([len(vehicles), 1])  # L2 norm of velocity vector

    W_sink = np.zeros([len(vehicles), 1])  # Velocity induced by 3-D sink element
    W_source = np.zeros([len(vehicles), 1])  # Velocity induced by 3-D source element
    W_flow = np.zeros(
        [len(vehicles), 1]
    )  # Vertical velocity component (to be used in 3-D scenarios)
    W_sum = np.zeros([len(vehicles), 1])
    W_norm = np.zeros([len(vehicles), 1])
    W_normal = np.zeros([len(vehicles), 1])

    for f, vehicle in enumerate(vehicles):
        # Remove current vehicle from vehicle list
        othervehicleslist = create_other_vehicles_list(vehicles, f)
        # Velocity induced by 2D point sink, eqn. 10.2 & 10.3 in Katz & Plotkin:
        V_sink[f] = induced_sink_velocity2D(vehicle)
        # V_sink[f, 1] = induced_sink_velocity2D(vehicle, dimension = 1)
        # Velocity induced by 3-D point sink. Katz&Plotkin Eqn. 3.25
        # BUG why is only this one 3D?
        W_sink[f, 0] = induced_sink_velocity3D(vehicle)[2]

        # Velocity induced by 2D point source, eqn. 10.2 & 10.3 in Katz & Plotkin:
        source_gain = 0
        for othervehicle in othervehicleslist:
            V_source[f] += induced_source_velocity2D(vehicle, othervehicle)
            W_source[f] += (
                source_gain * induced_source_velocity3D(vehicle, othervehicle)[2]
            )
            # Adding vortex elements attached to the vehicles. Using vortex strengths as 1/4 of the defined vehicle source_strength. FIXME to make it a design variable...
            V_vortex[f] += induced_vortex_velocity(vehicle, othervehicle)
            # V_vortex[f, 1] += induced_vortex_velocity(vehicle,othervehicle,dimension=0)

        if method == "Vortex":
            for building in arenamap.buildings:
                u = np.zeros((building.nop, 1))
                v = np.zeros((building.nop, 1))
                polygon = Polygon(building.vertices)
                point = Point(vehicle.position[0], vehicle.position[1])
                # print('Vehicle' + str(f))
                # print(point)
                # print(polygon)
                if polygon.contains(point) is True:
                    # this code does nothing, what is it?
                    V_gamma[f, 0] = V_gamma[f, 0] + 0
                    V_gamma[f, 1] = V_gamma[f, 1] + 0

                elif polygon.contains(point) is False:
                    if vehicle.ID in building.gammas.keys():
                        # Velocity induced by vortices on each panel:

                        u = (building.gammas[vehicle.ID][:].T / (2 * np.pi)) * (
                            (vehicle.position[1] - building.pcp[:, 1])
                            / (
                                (vehicle.position[0] - building.pcp[:, 0]) ** 2
                                + (vehicle.position[1] - building.pcp[:, 1]) ** 2
                            )
                        )
                        v = (-building.gammas[vehicle.ID][:].T / (2 * np.pi)) * (
                            (vehicle.position[0] - building.pcp[:, 0])
                            / (
                                (vehicle.position[0] - building.pcp[:, 0]) ** 2
                                + (vehicle.position[1] - building.pcp[:, 1]) ** 2
                            )
                        )
                        V_gamma[f, 0] = V_gamma[f, 0] + np.sum(u)
                        V_gamma[f, 1] = V_gamma[f, 1] + np.sum(v)

        elif method == "Source":
            for building in arenamap.buildings:
                u = np.zeros((building.nop, 1))
                v = np.zeros((building.nop, 1))
                polygon = Polygon(building.vertices)
                point = Point(vehicle.position[0], vehicle.position[1])
                # print('Vehicle' + str(f))
                # print(point)
                # print(polygon)
                if polygon.contains(point):
                    # print(polygon.contains(point))
                    V_gamma[f, 0] = V_gamma[f, 0] + 0
                    V_gamma[f, 1] = V_gamma[f, 1] + 0
                    # print(polygon.contains(point))
                elif polygon.contains(point) is False:
                    # print(polygon.contains(point))
                    if vehicle.ID in building.gammas.keys():
                        # Velocity induced by vortices on each panel:

                        u = (building.gammas[vehicle.ID][:].T / (2 * np.pi)) * (
                            (vehicle.position[1] - building.pcp[:, 1])
                            / (
                                (vehicle.position[0] - building.pcp[:, 0]) ** 2
                                + (vehicle.position[1] - building.pcp[:, 1]) ** 2
                            )
                        )
                        v = (-building.gammas[vehicle.ID][:].T / (2 * np.pi)) * (
                            (vehicle.position[0] - building.pcp[:, 0])
                            / (
                                (vehicle.position[0] - building.pcp[:, 0]) ** 2
                                + (vehicle.position[1] - building.pcp[:, 1]) ** 2
                            )
                        )
                        V_gamma[f, 0] = V_gamma[f, 0] + np.sum(u)
                        V_gamma[f, 1] = V_gamma[f, 1] + np.sum(v)
        elif method == "Hybrid":
            pass

        # !!!!!!FIX THIS!!!!!!!
        # 0*vehicle.V_inf[0]

        # Total velocity induced by all elements on map:
        V_sum[f, 0] = (
            V_gamma[f, 0]
            + V_sink[f, 0]
            + 0 * vehicle.V_inf[0]
            + V_source[f, 0]
            + V_vortex[f, 0]
        )
        V_sum[f, 1] = (
            V_gamma[f, 1]
            + V_sink[f, 1]
            + 0 * vehicle.V_inf[1]
            + V_source[f, 1]
            + V_vortex[f, 1]
        )

        # L2 norm of flow velocity:
        V_norm[f] = (V_sum[f, 0] ** 2 + V_sum[f, 1] ** 2) ** 0.5
        # Normalized flow velocity:
        V_normal[f, 0] = V_sum[f, 0] / V_norm[f]
        V_normal[f, 1] = V_sum[f, 1] / V_norm[f]

        # Flow velocity inversely proportional to velocity magnitude:
        V_flow[f, 0] = V_normal[f, 0] / V_norm[f]
        V_flow[f, 1] = V_normal[f, 1] / V_norm[f]

        # Add wind disturbance
        # V_flow[f,0] = V_flow[f,0] + U_wind
        # V_flow[f,1] = V_flow[f,0] + V_wind

        W_sum[f] = W_sink[f] + W_source[f]
        if W_sum[f] != 0.0:
            W_norm[f] = (W_sum[f] ** 2) ** 0.5
            W_normal[f] = W_sum[f] / W_norm[f]
            W_flow[f] = W_normal[f] / W_norm[f]
            W_flow[f] = np.clip(W_flow[f], -0.07, 0.07)
        else:
            W_flow[f] = W_sum[f]

        flow_vels[f, :] = [V_flow[f, 0], V_flow[f, 1], W_flow[f, 0]]
        # flow_vels[f,:] = [V_flow[f,0] + arenamap.wind[0]/(1.35*1.35), V_flow[f,1] + arenamap.wind[1]/(1.35*1.35), W_flow[f,0]]

    return flow_vels
