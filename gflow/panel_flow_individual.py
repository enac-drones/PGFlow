from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

from shapely.geometry import Point, Polygon
from shapely.prepared import prep


# from datetime import datetime
from itertools import compress
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from vehicle import Vehicle, PersonalVehicle
    from building import Building

from gflow_local.arena import ArenaMap
import time



"""# Velocity Calculation"""

class PanelFlow:
    def __init__(self, position:ArrayLike, goal:ArrayLike, source_strength:float, sink_strength:float,imag_source_strength:float) -> None:
        self.position = position
        self.goal = goal
        self.source_strength = source_strength
        self.sink_strength = sink_strength
        self.imag_source_strength = imag_source_strength


    # def create_other_vehicles_list(self, vehicles:dict[str,PersonalVehicle], v_id: str):
    #     # return vehicles[:current_index] + vehicles[current_index + 1 :]
    #     return [vehicle for vehicle in vehicles.values() if vehicle.ID != v_id]


    def calculate_vortex_strengths(self,vehicles:dict[str,PersonalVehicle], arenamap: ArenaMap, method:str):
        # Remove current vehicle from vehicle list.
        # othervehicleslist = self.create_other_vehicles_list(vehicles, v_id)
        # Remove buildings with heights below cruise altitue:
        vehicle.altitude_mask = self.altitude_mask(vehicle, arenamap)
        # related_buildings keeps only the buildings for which the altitude_mask is 1, ie buildings that are higher than the altitude
        # of the vehicle in question
        related_buildings:list[Building] = list(compress(arenamap.buildings, vehicle.altitude_mask))
        # Vortex strength calculation (related to panels of each building):
        for building in related_buildings:
            building.gamma_calc(vehicle, othervehicleslist)


    def altitude_mask(self,vehicle:PersonalVehicle, arenamap: ArenaMap):
        mask = np.zeros((len(arenamap.buildings)))
        for index, panelledbuilding in enumerate(arenamap.buildings):
            if (panelledbuilding.vertices[:, 2] > vehicle.position[2]).any():
                mask[index] = 1
        return mask


    def pre_calculation(self,vehicles:list[Vehicle])->None:
        self.vehicle_positions = np.array([v.position for v in vehicles])
        self.sink_strengths = np.array([v.sink_strength for v in vehicles])
        self.vehicle_source_strengths = np.array([v.source_strength for v in vehicles])
        self.vehicle_vortex_strengths = self.vehicle_source_strengths / 4
        self.sink_positions = np.array(
            [v.goal for v in vehicles]
        )  # Assuming the sink position is stored in 'goal' attribute

        # Calculate position differences and distances
        self.position_diff_3D = self.vehicle_positions - self.sink_positions
        self.position_diff_2D = self.position_diff_3D[:, :2]
        self.squared_distances = np.sum(self.position_diff_2D**2, axis=-1)
        self.power4_distances = np.sum(self.position_diff_2D**4, axis=-1)


        # # Extend dimensions for broadcasting
        # vehicle_positions_extended = vehicle_positions[:, np.newaxis, :]
        # vehicle_vortex_strengths_extended = vehicle_vortex_strengths[:, np.newaxis]

        # # Calculate position differences and distances
        # position_diff_3D_extended = vehicle_positions_extended - vehicle_positions
        # position_diff_2D_extended = position_diff_3D_extended[:, :, :2]
        # perpendicular_array = np.zeros_like(position_diff_2D_extended)
        # perpendicular_array[..., 0] = -position_diff_2D_extended[..., 1]  # replace x with y
        # perpendicular_array[..., 1] = position_diff_2D_extended[..., 0]  # replace y with -x

        # power4_distances_extended = np.sum(position_diff_2D_extended**4, axis=-1)

        # # Replace zero self-distances with ones to avoid division by zero
        # np.fill_diagonal(power4_distances_extended, 1)

    def calculate_all_induced_sink_velocities(self,vehicles:dict[str,PersonalVehicle]):

        vehicle_positions = np.array([v.position for v in vehicles.values()])
        sink_strengths = np.array([v.sink_strength for v in vehicles.values()])
        sink_positions = np.array(
            [v.goal for v in vehicles.values()]
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


    def calculate_all_induced_source_velocities(self, vehicles:dict[str,PersonalVehicle]):
        """_summary_

        Args:
            vehicles (_type_): _description_

        Returns:
            _type_: _description_
        """
        vehicle_positions = np.array([v.position for v in vehicles.values()])
        vehicle_source_strengths = np.array([v.source_strength for v in vehicles.values()])

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


    def calculate_all_induced_vortex_velocities(self, vehicles:dict[str,PersonalVehicle])->ArrayLike:
        vehicle_positions = np.array([v.position for v in vehicles.values()])
        vehicle_source_strengths = np.array([v.source_strength for v in vehicles.values()])
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

    # def calculate_uv_gamma(self, vehicle:Vehicle,building:Building)->ArrayLike:
    #     if not vehicle.ID in building.gammas.keys():
    #         return
    #     # Velocity induced by vortices on each panel:
    #     squared_distances = (
    #         vehicle.position[0] - building.pcp[:, 0]
    #     ) ** 2 + (vehicle.position[1] - building.pcp[:, 1]) ** 2
    #     # vortex strengths normalised by 2pi
    #     gammas = building.gammas[vehicle.ID][:].T / (2 * np.pi)

    #     # numerators of u and v, shape (2, nop)
    #     numerators = np.array(
    #         [
    #             (vehicle.position[1] - building.pcp[:, 1]),
    #             -(vehicle.position[0] - building.pcp[:, 0]),
    #         ]
    #     )

    #     # array of u and v
    #     uv = gammas * numerators / squared_distances

    #     return uv

    
    def gamma_calculation(self,vehicles:dict[str,PersonalVehicle],arena:ArenaMap):
        n_vehicles:int = len(vehicles)
        #######################################################################################################################################
        # Determine the number of buildings and the maximum number of panels in any building
        num_buildings:int = len(arena.buildings)
        max_num_panels:int = max(building.nop for building in arena.buildings)

        # Initialize the all_pcp array with zeros
        all_pcp = np.zeros((num_buildings, max_num_panels, 2))

        # Populate the all_pcp array
        for i, building in enumerate(arena.buildings):
            num_panels = building.nop  # Number of panels in the current building
            all_pcp[i, :num_panels, :] = building.pcp[:num_panels, :2]  # Take only the first two dimensions

        #  all_pcp is now a 3D array of shape (num_buildings, max_num_panels, 2)
        #######################################################################################################################################

        # Initialize the vehicle_positions array with zeros
        vehicle_positions = np.zeros((n_vehicles, 2))

        # Populate the vehicle_positions array
        for i, vehicle in enumerate(vehicles.values()):
            vehicle_positions[i, :] = vehicle.position[:2]
            # vehicle_positions = vehicle_positions[:,:2]

        # vehicle_positions is now a 2D array of shape (num_vehicles, 2)
        #######################################################################################################################################
        # Initialize the all_gammas array with zeros or NaNs
        # NaNs might make it easier to identify if something goes wrong
        all_gammas = np.zeros((n_vehicles, num_buildings, max_num_panels))

        # Populate the all_gammas array
        for i, building in enumerate(arena.buildings):
            num_panels = building.nop  # Number of panels in the current building
            for j, vehicle in enumerate(vehicles.values()):
                if vehicle.ID in building.gammas:
                    # all_gammas[j, i, :num_panels] = building.gammas[vehicle.ID][:num_panels]
                    all_gammas[j, i, :num_panels] = building.gammas[vehicle.ID][:num_panels].ravel()


        # all_gammas is now a 3D array of shape (num_vehicles, num_buildings, max_num_panels)
        #######################################################################################################################################
        # Assuming vehicle_positions is of shape (num_vehicles, 2)  
        # and all_pcp is of shape (num_buildings, num_panels, 2)
        diff = vehicle_positions[:, np.newaxis, np.newaxis, :] - all_pcp[np.newaxis, :, :, :]
        squared_distances = np.sum(diff**2, axis=-1)  # shape: (num_vehicles, num_buildings, num_panels)

        # Create the numerators for all vehicles and all buildings
        numerators = np.zeros((n_vehicles, num_buildings, max_num_panels, 2))
        numerators[:, :, :, 0] = vehicle_positions[:, np.newaxis, np.newaxis, 1] - all_pcp[np.newaxis, :, :, 1]
        numerators[:, :, :, 1] = -(vehicle_positions[:, np.newaxis, np.newaxis, 0] - all_pcp[np.newaxis, :, :, 0])

        # Assuming all_gammas is of shape (num_vehicles, num_buildings, num_panels)
        all_gammas_normalized = all_gammas / (2 * np.pi)

        # uv calculations, exploiting broadcasting
        uv = all_gammas_normalized[:, :, :, np.newaxis] * numerators / squared_distances[:, :, :, np.newaxis]

        V_gamma_all = np.sum(uv, axis=(1, 2))  # Summing across num_buildings and num_panels axes
        #######################################################################################################################################
        return V_gamma_all
    
    def Flow_Velocity_Calculation(self,
        vehicles:dict[str,PersonalVehicle], arenamap: ArenaMap, method="Vortex"
    )->ArrayLike:
        n_vehicles = len(vehicles)
        two_dim_shape = (n_vehicles, 2)
        one_dim_shape = (n_vehicles, 1)

        V_gamma, V_sink, V_source, V_vortex, V_sum, V_normal, V_flow = [
            np.zeros(two_dim_shape) for _ in range(7)
        ]
        V_norm, W_sink, W_source, W_flow, W_sum, W_norm, W_normal = [
            np.zeros(one_dim_shape) for _ in range(7)
        ]
        V_gamma_all = self.gamma_calculation(vehicles,arenamap)
        

        # Filter vehicles based on the state
        
        # when simple_sim is called, vehicles is self.personal_vehicle_list, ie the current vehicle's own list of vehicles

        # Calculating unknown vortex strengths using panel method:
        t = time.time()
        self.calculate_vortex_strengths(vehicles, arenamap, method)
        t1 = time.time()
        # --------------------------------------------------------------------
        # Flow velocity calculation given vortex strengths:
        flow_vels = np.zeros([len(vehicles), 3])



        source_gain = 0

        # calculate all effects of vehicles onto each other (sinks, sources, vortices etc)
        # Velocity induced by 2D point sink, eqn. 10.2 & 10.3 in Katz & Plotkin:

        V_sink = self.calculate_all_induced_sink_velocities(vehicles)
        # W_sink = self.calculate_all_induced_sink_velocities3D(vehicles)[:, 2]
        # Velocity induced by 2D point source, eqn. 10.2 & 10.3 in Katz & Plotkin:
        V_source = self.calculate_all_induced_source_velocities(vehicles)
        # TODO everything involving W_source is super dodgy, why are we only using the z component, weird... needs serious testing
        # Velocity induced by 3-D point sink. Katz&Plotkin Eqn. 3.25
        # W_source = source_gain * self.calculate_all_induced_source_velocities3D(vehicles)[:, 2]
        V_vortex = self.calculate_all_induced_vortex_velocities(vehicles)

        t = time.time()
        # Pre-calculate the arrays
    
        
        #########################################################################################################################
        # FIXME remove the for loop later and replace with this when it works
        # # Summing the effects for all vehicles at once
        V_gamma = V_gamma_all
        V_sum = V_gamma + V_sink + V_source + V_vortex

        # Normalization and flow calculation for all vehicles
        V_norm = np.linalg.norm(V_sum, axis=1, keepdims=True)
        V_normal = V_sum / (V_norm + 1e-10)  # Added a small constant to avoid division by zero
        V_flow = V_normal / (V_norm + 1e-10)
        #########################################################################################################################
        # TODO Removed 3D components for now, it was dodgy anyway
        # For W components
        # W_sum = W_sink + W_source
        # W_norm = np.abs(W_sum)
        # W_normal = W_sum / (W_norm + 1e-10)  # Added a small constant to avoid division by zero
        # W_flow = np.clip(W_normal / (W_norm + 1e-10), -0.07, 0.07)
        #########################################################################################################################
        # Finally, populate flow_vels for all vehicles at once
        # flow_vels = np.hstack([V_flow, W_flow.reshape(-1, 1)])

        flow_vels = V_flow
        #########################################################################################################################

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
