from __future__ import annotations

import numpy as np

# from numpy import linalg
# import math
# import matplotlib.pyplot as plt
# import pyclipper
from shapely.geometry import Point, Polygon
from shapely.prepared import prep


# from datetime import datetime
from itertools import compress
from typing import List

# from .building import Building

# from gflow_local.vehicle import Vehicle
from gflow_local.arena import ArenaMap
# from .building import Building
import time

# from numba import jit


# from vehicle import Vehicle
# import pdb

# from scipy.spatial import ConvexHull

"""# Velocity Calculation"""


def create_other_vehicles_list(vehicles, current_index: int):
    return vehicles[:current_index] + vehicles[current_index + 1 :]


# def other_vehicle_positions(other_vehicles):
#     other_vehicles_positions = np.array([other_vehicle.position for other_vehicle in other_vehicles])
#     return other_vehicles_positions

# def other_vehicle_source_strengths(other_vehicles):
#     other_vehicles_source_strengths = np.array([other_vehicle.source_strength for other_vehicle in other_vehicles])
#     return other_vehicles_source_strengths


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
        if (panelledbuilding.vertices[:, 2] > vehicle.position[2]).any():
            mask[index] = 1
    return mask



def calculate_all_induced_sink_velocities(vehicles):

    vehicle_positions = np.array([v.position for v in vehicles])
    sink_strengths = np.array([v.sink_strength for v in vehicles])
    sink_positions = np.array(
        [v.goal for v in vehicles]
    )  # Assuming the sink position is stored in 'goal' attribute

    # Calculate position differences and distances
    position_diff_3D = vehicle_positions - sink_positions
    position_diff_2D = position_diff_3D[:, :2]
    squared_distances = np.sum(position_diff_2D**2, axis=-1)

    # Avoid division by zero (in case the vehicle is exactly at the sink)
    squared_distances[squared_distances == 0] = 1

    # Calculate induced velocity
    induced_v = (
        -sink_strengths[:, np.newaxis]
        * position_diff_2D
        / (2 * np.pi * squared_distances[:, np.newaxis])
    )

    return induced_v


def calculate_all_induced_sink_velocities3D(vehicles):

    vehicle_positions = np.array([v.position for v in vehicles])
    sink_strengths = np.array([v.sink_strength for v in vehicles])
    sink_positions = np.array(
        [v.goal for v in vehicles]
    )  # Assuming the sink position is stored in 'goal' attribute

    # Calculate position differences and distances
    position_diff_3D = vehicle_positions - sink_positions
    squared_distances = np.sum(position_diff_3D**2, axis=-1)

    # Avoid division by zero (in case the vehicle is exactly at the sink)
    squared_distances[squared_distances == 0] = 1

    # Calculate induced velocity
    induced_v = (
        -sink_strengths[:, np.newaxis]
        * position_diff_3D
        / (2 * np.pi * squared_distances[:, np.newaxis])
    )

    return induced_v


def calculate_all_induced_source_velocities(vehicles):
    """_summary_

    Args:
        vehicles (_type_): _description_

    Returns:
        _type_: _description_
    """
    # print(f"states are {vehicle_states}")
    # vehicles = [v for v in vehicles if v.state == 0]
    # print(len(vehicles))
    # print(len(vehicles))
    vehicle_positions = np.array([v.position for v in vehicles])
    vehicle_source_strengths = np.array([v.source_strength for v in vehicles])

    # Extend dimensions for broadcasting
    vehicle_positions_extended = vehicle_positions[:, np.newaxis, :]
    vehicle_source_strengths_extended = vehicle_source_strengths[:, np.newaxis]

    # Calculate position differences and distances
    position_diff_3D = vehicle_positions_extended - vehicle_positions
    position_diff_2D = position_diff_3D[:, :, :2]
    squared_distances = np.sum(np.abs(position_diff_2D) ** 4, axis=-1)

    # Replace zero self-distances with ones to avoid division by zero
    np.fill_diagonal(squared_distances, 1)

    # Calculate induced velocity
    induced_v = (
        vehicle_source_strengths_extended
        * position_diff_2D
        / (2 * np.pi * squared_distances[..., np.newaxis])
    )

    # Remove self-interaction (diagonal elements in the array)
    for i in range(2):
        np.fill_diagonal(induced_v[..., i], 0)

    # Sum over all interactions
    V_source = np.sum(induced_v, axis=1)

    return V_source


def calculate_all_induced_source_velocities3D(vehicles):
    vehicle_positions = np.array([v.position for v in vehicles])
    vehicle_source_strengths = np.array([v.source_strength for v in vehicles])

    # Extend dimensions for broadcasting
    vehicle_positions_extended = vehicle_positions[:, np.newaxis, :]
    vehicle_source_strengths_extended = vehicle_source_strengths[:, np.newaxis]

    # Calculate position differences and distances
    position_diff_3D = vehicle_positions_extended - vehicle_positions
    # position_diff_2D = position_diff_3D[:, :, :2]
    squared_distances = np.sum(position_diff_3D**2, axis=-1)

    # Replace zero self-distances with ones to avoid division by zero
    np.fill_diagonal(squared_distances, 1)

    # Calculate induced velocity
    induced_v = (
        vehicle_source_strengths_extended
        * position_diff_3D
        / (4 * np.pi * squared_distances[..., np.newaxis] ** 1.5)
    )

    # Remove self-interaction (diagonal elements in the array)
    for i in range(2):
        np.fill_diagonal(induced_v[..., i], 0)

    # Sum over all interactions
    V_source = np.sum(induced_v, axis=1)

    return V_source


def calculate_all_induced_vortex_velocities(vehicles):
    vehicle_positions = np.array([v.position for v in vehicles])
    vehicle_source_strengths = np.array([v.source_strength for v in vehicles])
    vehicle_vortex_strengths = vehicle_source_strengths / 4

    # Extend dimensions for broadcasting
    vehicle_positions_extended = vehicle_positions[:, np.newaxis, :]
    vehicle_vortex_strengths_extended = vehicle_vortex_strengths[:, np.newaxis]

    # Calculate position differences and distances
    position_diff_3D = vehicle_positions_extended - vehicle_positions
    position_diff_2D = position_diff_3D[:, :, :2]
    perpendicular_array = np.zeros_like(position_diff_2D)
    perpendicular_array[..., 0] = -position_diff_2D[..., 1]  # replace x with y
    perpendicular_array[..., 1] = position_diff_2D[..., 0]  # replace y with -x

    squared_distances = np.sum(position_diff_2D**4, axis=-1)

    # Replace zero self-distances with ones to avoid division by zero
    np.fill_diagonal(squared_distances, 1)

    # Calculate induced velocity
    induced_v = (
        vehicle_vortex_strengths_extended
        * perpendicular_array
        / (2 * np.pi * squared_distances[..., np.newaxis])
    )

    # Remove self-interaction (diagonal elements in the array)
    for i in range(2):
        np.fill_diagonal(induced_v[..., i], 0)

    # Sum over all interactions
    V_vortex = np.sum(induced_v, axis=1)
    # swap the x and y coordinates (whoops bug)
    return V_vortex  # [:,::-1]



def Flow_Velocity_Calculation(
    vehicles, arenamap: ArenaMap, method="Vortex", update_velocities=True
):
    
    n_vehicles = len(vehicles)
    two_dim_shape = (n_vehicles, 2)
    one_dim_shape = (n_vehicles, 1)

    V_gamma, V_sink, V_source, V_vortex, V_sum, V_normal, V_flow = [
        np.zeros(two_dim_shape) for _ in range(7)
    ]
    V_norm, W_sink, W_source, W_flow, W_sum, W_norm, W_normal = [
        np.zeros(one_dim_shape) for _ in range(7)
    ]

    # Filter vehicles based on the state
    
    # when simple_sim is called, vehicles is self.vehicle_list, ie the current vehicle's own list of vehicles

    # Calculating unknown vortex strengths using panel method:
    t = time.time()
    calculate_vortex_strengths(vehicles, arenamap, method)
    t1 = time.time()
    # print(f"Time to calculate vortex strengths: {t1-t}")
    # --------------------------------------------------------------------
    # Flow velocity calculation given vortex strengths:
    flow_vels = np.zeros([len(vehicles), 3])

    # V_gamma = np.zeros([len(vehicles), 2])  # Velocity induced by vortices
    # V_sink = np.zeros([len(vehicles), 2])  # Velocity induced by sink element
    # V_source = np.zeros([len(vehicles), 2])  # Velocity induced by source elements
    # V_vortex = np.zeros(
    #     [len(vehicles), 2]
    # )  # Velocity induced by votex elements of the vehicles
    # V_sum = np.zeros([len(vehicles), 2])  # V_gamma + V_sink + V_source +V_vortex
    # V_normal = np.zeros([len(vehicles), 2])  # Normalized velocity
    # V_flow = np.zeros(
    #     [len(vehicles), 2]
    # )  # Normalized velocity inversly proportional to magnitude
    # V_norm = np.zeros([len(vehicles), 1])  # L2 norm of velocity vector

    # W_sink = np.zeros([len(vehicles), 1])  # Velocity induced by 3-D sink element
    # W_source = np.zeros([len(vehicles), 1])  # Velocity induced by 3-D source element
    # W_flow = np.zeros(
    #     [len(vehicles), 1]
    # )  # Vertical velocity component (to be used in 3-D scenarios)
    # W_sum = np.zeros([len(vehicles), 1])
    # W_norm = np.zeros([len(vehicles), 1])
    # W_normal = np.zeros([len(vehicles), 1])

    source_gain = 0

    # calculate all effects of vehicles onto each other (sinks, sources, vortices etc)
    # Velocity induced by 2D point sink, eqn. 10.2 & 10.3 in Katz & Plotkin:

    V_sink = calculate_all_induced_sink_velocities(vehicles)
    W_sink = calculate_all_induced_sink_velocities3D(vehicles)[:, 2]
    # Velocity induced by 2D point source, eqn. 10.2 & 10.3 in Katz & Plotkin:
    V_source = calculate_all_induced_source_velocities(vehicles)
    # TODO everything involving W_source is super dodgy, why are we only using the z component, weird... needs serious testing
    # Velocity induced by 3-D point sink. Katz&Plotkin Eqn. 3.25
    W_source = source_gain * calculate_all_induced_source_velocities3D(vehicles)[:, 2]
    V_vortex = calculate_all_induced_vortex_velocities(vehicles)

    t = time.time()
    # Pre-calculate the arrays
   
    for f, vehicle in enumerate(vehicles):
        # Make sure the vehicle.ID is in all building.gammas keys
        # valid_indices = np.array([vehicle.ID in gammas for gammas in gammas_all_buildings])

        if method == "Vortex":
            for building in arenamap.buildings:
                # nop is number of panels (not vertices)
                u = np.zeros((building.nop, 1))
                v = np.zeros((building.nop, 1))
                polygon = Polygon(building.vertices)
                point = Point(vehicle.position[0], vehicle.position[1])

                if not polygon.contains(point):
                    # if vehicle is outside the building
                    if vehicle.ID in building.gammas.keys():
                        # Velocity induced by vortices on each panel:
                        # Velocity induced by vortices on each panel:
                        squared_distances = (
                            vehicle.position[0] - building.pcp[:, 0]
                        ) ** 2 + (vehicle.position[1] - building.pcp[:, 1]) ** 2
                        # vortex strengths normalised by 2pi
                        gammas = building.gammas[vehicle.ID][:].T / (2 * np.pi)

                        # numerators of u and v, shape (2, nop)
                        numerators = np.array(
                            [
                                (vehicle.position[1] - building.pcp[:, 1]),
                                -(vehicle.position[0] - building.pcp[:, 0]),
                            ]
                        )

                        # array of u and v
                        uv = gammas * numerators / squared_distances

                        V_gamma[f] += np.sum(uv, axis=1)

                # V_gamma = calculate_V_gamma(vehicles,arenamap)
                elif polygon.contains(point):
                    # if vehicle is inside the building
                    # this code does nothing, what is it?
                    V_gamma[f] += 0

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


    return flow_vels


# comments
# Remove current vehicle from vehicle list
# othervehicleslist = create_other_vehicles_list(vehicles, f)
# Velocity induced by 2D point sink, eqn. 10.2 & 10.3 in Katz & Plotkin:
# V_sink[f] = induced_sink_velocity2D(vehicle)
# Velocity induced by 3-D point sink. Katz&Plotkin Eqn. 3.25
# BUG why is only this one 3D?
# W_sink[f, 0] = induced_sink_velocity3D(vehicle)[2]

# Velocity induced by 2D point source, eqn. 10.2 & 10.3 in Katz & Plotkin:
# source_gain = 0
# other_vehicles_pos = other_vehicle_positions(othervehicleslist)
# other_vehicles_source_stren = other_vehicle_source_strengths(othervehicleslist)
# other_vehicles_pos = np.concatenate([vehicle_positions[:f], vehicle_positions[f + 1:]])
# other_vehicles_source_stren = np.concatenate([vehicle_source_strengths[:f], vehicle_source_strengths[f + 1:]])

# TODO these are fake vortex strengths based of the source strengths
# other_vehicles_vortex_stren = other_vehicles_source_stren/4

# Now add all the effect from other vehicles onto the current vehicle

# adding effect of 2d sources from other vehicles
# V_source[f] = np.sum(induced_source_velocity2D(vehicle, other_vehicles_pos, other_vehicles_source_stren), axis=0)
# TODO everything involving W_source is super dodgy, why are we only using the z component, weird... needs serious testing
# induced_velocity_vectors = induced_source_velocity3D(vehicle, other_vehicles_pos, other_vehicles_source_stren)
# W_source[f] = source_gain*np.sum(induced_velocity_vectors[:, 2])  # selecting the 3rd column, which corresponds to the z-components
# W_source[f] += np.sum(induced_source_velocity3D(vehicle, other_vehicles_pos, other_vehicles_source_stren)[:,2])
# V_vortex[f] += np.sum(induced_vortex_velocity(vehicle, other_vehicles_pos, other_vehicles_vortex_stren),axis=0)
