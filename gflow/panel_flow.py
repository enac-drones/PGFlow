from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

from shapely.geometry import Point, Polygon
from shapely.prepared import prep


# from datetime import datetime
from itertools import compress
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from gflow.vehicle import Vehicle, PersonalVehicle
    from gflow.building import Building

# from gflow.arena import ArenaMap
import time

#vortexL lines 289, 232, 180


"""# Velocity Calculation"""

class PanelFlow:
    def __init__(self, vehicle:Vehicle) -> None:
        self.vehicle = vehicle

    def calculate_unknown_vortex_strengths(self,vehicle:Vehicle)->None:
        '''vehicles are the personal_vehicle_list containing all other vehicles'''
        # vehicles = vehicle.personal_vehicle_dict
        # arenamap = vehicle.arena
        buildings = vehicle.relevant_obstacles

        # Remove buildings with heights below cruise altitude:
        altitude_mask = self.altitude_mask(vehicle)
        # related_buildings keeps only the buildings for which the altitude_mask is 1, ie buildings that are higher than the altitude
        # of the vehicle in question
        related_buildings:list[Building] = list(compress(buildings, altitude_mask))
        # Vortex strength calculation (related to panels of each building):
        for building in related_buildings:
            self.gamma_calc(building, self.vehicle)


    def altitude_mask(self, vehicle: Vehicle):
        # arenamap = vehicle.arena
        buildings = vehicle.relevant_obstacles
        mask = np.zeros((len(buildings)))
        for index, panelledbuilding in enumerate(buildings):
            if (panelledbuilding.vertices[:, 2] > vehicle.position[2]).any():
                mask[index] = 1
        return mask


    def calculate_induced_sink_velocity(self,vehicle:Vehicle):

        
        position_diff_3D = vehicle.position - vehicle.goal
        position_diff_2D = position_diff_3D[:2]
        squared_distance = np.linalg.norm(position_diff_2D)**2

        # Avoid division by zero (in case the vehicle is exactly at the sink)
        # squared_distances[squared_distances == 0] = 1

        # Calculate induced velocity
        induced_v = (
            -vehicle.sink_strength
            * position_diff_2D
            / (2 * np.pi * squared_distance)
        )

        return induced_v

    # def distance_effect_function(self, distance: float, max_distance:float) -> float:
    #     """Drop-off effect based on distance."""
    #     # max_distance = self.vehicle.max_avoidance_distance
    #     ratio = distance/max_distance
    #     linear_dropoff = 1-distance/max_distance
    #     exponential_dropoff = 1/(1+np.e**(10*(ratio-0.7)))
    #     effect = (1/(2 * np.pi * distance**4)) * exponential_dropoff

    #     return effect
    
    def distance_effect_function(self, distance_array: np.ndarray, max_distance:float) -> np.ndarray:
        """Drop-off effect based on distance, accepting an array of distances."""
        max_distance = 3
        ratio = distance_array / max_distance
        linear_dropoff = 1 - ratio
        exponential_dropoff = 1 / (1 + np.exp(10 * (ratio - 0.7)))
        
        effect = np.zeros_like(distance_array)  # Initialize array to store results

        # Apply conditions
        near_indices = distance_array < 1
        far_indices = ~near_indices  # Elements not satisfying the 'near' condition

        effect[near_indices] = (1 / (2 * np.pi * distance_array[near_indices] ** 4))
        effect[far_indices] = (1 / (2 * np.pi * distance_array[far_indices] ** 2)) * exponential_dropoff[far_indices]

        return effect
    
    def calculate_induced_source_velocities_on_main_vehicle(self, main_vehicle: Vehicle):
        # Get positions and source strengths of other vehicles
        other_vehicles = main_vehicle.personal_vehicle_dict
        other_positions = np.array([v.position[:2] for v in other_vehicles.values()])

        other_source_strengths = np.array([v.source_strength for v in other_vehicles.values()])
        # Calculate position differences and distances

        position_diff_2D = main_vehicle.position[:2] - other_positions 
        distances = np.linalg.norm(position_diff_2D, axis=1)
        effect = self.distance_effect_function(distances, main_vehicle.max_avoidance_distance)
        
        # Calculate induced velocity
        induced_v = other_source_strengths[:, np.newaxis] * position_diff_2D * effect[:, np.newaxis]
        # Sum over all interactions to get total induced velocity on the main vehicle
        V_source = np.sum(induced_v, axis=0)
        
        return V_source




    # def calculate_induced_vortex_velocities_on_main_vehicle(self, main_vehicle: Vehicle):
    #     # Get positions and vortex strengths of other vehicles
    #     other_vehicles = main_vehicle.personal_vehicle_dict

    #     other_positions = np.array([v.position[:2] for v in other_vehicles.values()])
    #     other_vortex_strengths = np.array([v.source_strength for v in other_vehicles.values()]) / 4
        
    #     # Calculate position differences and distances
    #     position_diff_2D =  main_vehicle.position[:2] - other_positions
    #     perpendicular_array = np.zeros_like(position_diff_2D)
    #     perpendicular_array[:, 0] = -position_diff_2D[:, 1]  # replace x with -y
    #     perpendicular_array[:, 1] = position_diff_2D[:, 0]   # replace y with x
        
    #     # squared_distances = np.sum(np.abs(position_diff_2D) ** 4, axis=1)
    #     distances = np.linalg.norm(position_diff_2D, axis=1)
    #     effect = self.distance_effect_function(distances, main_vehicle.max_avoidance_distance)

    #     # squared_distances = distances**4
        
    #     # Calculate induced velocity
    #     induced_v = other_vortex_strengths[:, np.newaxis] * perpendicular_array * effect[:, np.newaxis]
        
    #     # Sum over all interactions to get total induced velocity on the main vehicle
    #     V_vortex = np.sum(induced_v, axis=0)
    #     return V_vortex


    
    def calculate_induced_building_velocity(self, main_vehicle: Vehicle):
        # arena = main_vehicle.arena
        buildings = main_vehicle.relevant_obstacles
        # Determine the number of buildings and the maximum number of panels in any building
        num_buildings = len(buildings)
        max_num_panels = max(building.nop for building in buildings)

        # Initialize the all_pcp array with zeros
        all_vp = np.zeros((num_buildings, max_num_panels, 2))

        # Populate the all_pcp array
        for i, building in enumerate(buildings):
            num_panels = building.nop  # Number of panels in the current building
            all_vp[i, :num_panels, :] = building.vp[:num_panels, :2]

        # Initialize the all_gammas array with zeros or NaNs
        all_gammas = np.zeros((num_buildings, max_num_panels))

        # Populate the all_gammas array
        for i, building in enumerate(buildings):
            num_panels = building.nop  # Number of panels in the current building
            if main_vehicle.ID in building.gammas:
                all_gammas[i, :num_panels] = building.gammas[main_vehicle.ID][:num_panels].ravel()

        # Get position of the main_vehicle
        main_vehicle_position = main_vehicle.position[:2]

        # Calculate position differences and distances
        diff = main_vehicle_position - all_vp
        squared_distances = np.sum(diff ** 2, axis=-1)

        # Create the numerator for all buildings
        vec_to_vehicle = np.zeros((num_buildings, max_num_panels, 2))

        #don't need to reshape, broadcasting is possible
        vec_to_vehicle =  main_vehicle_position - all_vp 

        # Normalize all_gammas
        all_gammas_normalized = all_gammas / (2 * np.pi)

        # uv calculations
        uv = all_gammas_normalized[:, :, np.newaxis] * vec_to_vehicle / squared_distances[:, :, np.newaxis]

        # Summing across num_buildings and num_panels axes
        V_gamma_main = np.sum(uv, axis=(0, 1))
        #set x to y and y to -x (rotate vec_to_vehicle by pi/2 clockwise)
        #rotate 90 degrees clockwise to corresponding to vortex effect
        V_gamma_main[0], V_gamma_main[1] = V_gamma_main[1], -V_gamma_main[0]

        return V_gamma_main

    
    
    
    def gamma_calc(self, building:Building, vehicle:Vehicle):
        """Calculate the unknown vortex strengths of the building panels

        Args:
            vehicle (Vehicle): _description_
            othervehicles (list[Vehicle]): _description_
        """

        othervehicles = vehicle.personal_vehicle_dict.values()
        othervehicles = [v for v in othervehicles if not building.contains_point(v.position[:2])]
        # Initialize arrays in case no other vehicles
        vel_sink = np.zeros((building.nop, 2))
        vel_source = np.zeros((building.nop, 2))
        vel_source_imag = np.zeros((building.nop, 2))
        vel_vortex = np.zeros((building.nop, 2))
        RHS = np.zeros((building.nop, 1))

        # Pre-calculate repeated terms
        sink_diff = building.pcp[:,:2] - vehicle.goal[:2]
        sink_sq_dist = np.sum(sink_diff ** 2, axis=-1)
        imag_diff = building.pcp[:,:2] - vehicle.position[:2]
        imag_sq_dist = np.sum(imag_diff ** 2, axis=-1)

        # Velocity calculations for sink and imag_source
        vel_sink = -vehicle.sink_strength * sink_diff / (2 * np.pi * sink_sq_dist)[:, np.newaxis]
        vel_source_imag = vehicle.imag_source_strength * imag_diff / (2 * np.pi * imag_sq_dist)[:, np.newaxis]

        ########
        if othervehicles:
            # Extract positions of all vehicles
            all_positions = np.array([other.position[:2] for other in othervehicles])
            # if not all_positions:
            #     break
            # Compute source differences
            source_diff = building.pcp[:, np.newaxis, :2] - all_positions

            # Compute squared distances
            source_sq_dist = np.sum(source_diff ** 2, axis=-1)
            # distances1 = np.sqrt(source_sq_dist)
            distances = np.linalg.norm(source_diff, axis=-1)


            # Extract all source strengths
            all_source_strengths = np.array([other.source_strength for other in othervehicles])

            # Compute velocities due to sources and vortices
            effect = self.distance_effect_function(distances, vehicle.max_avoidance_distance)
            alternative = all_source_strengths[:, np.newaxis] * source_diff * effect[..., np.newaxis]
            vel_source_contribs = (all_source_strengths[:, np.newaxis] * source_diff / (2 * np.pi * source_sq_dist[..., np.newaxis]))

            # Sum across the contributions of all vehicles
            vel_source = np.sum(vel_source_contribs, axis=1) #shape(nop, 2)
            # vel_source = np.sum(alternative, axis=1) #shape(nop, 2)

            # for vortex, just rotate by 90 degrees anticlockwise and divide by 4 #TODO, division by 4 is arbitrary
            vel_vortex = np.column_stack([-vel_source[...,1], vel_source[...,0]]) / 4

        ########
        # RHS calculation
        cos_pb = np.cos(building.pb)
        sin_pb = np.sin(building.pb)

        normal_vectors = np.array([cos_pb, sin_pb]).T
        
        # Combine all velocity components into a single array before summing
        total_velocity = (
            # effect from sink if using
            vel_sink +
            # free stream velocity
            vehicle.v_free_stream + 
            vel_source_imag + 
            # elements from other vehicles
            vel_source + 
            vel_vortex
        )

        RHS[:, 0] = -np.sum(total_velocity * normal_vectors, axis=1)
        # Solve for gammas
        #gammas is dictionary because a building might have different gammas for different vehicles
        building.gammas[vehicle.ID] = np.matmul(building.K_inv, RHS)
        

    def Flow_Velocity_Calculation(self,
        vehicle:Vehicle)->ArrayLike:
        vehicles = vehicle.personal_vehicle_dict

        V_gamma, V_sink, V_source, V_vortex, V_sum = [
            np.zeros(2) for _ in range(5)
        ]

        flow_vels = np.zeros([len(vehicles), 3])
        

        # Calculating unknown vortex strengths using panel method:
        if vehicle.relevant_obstacles:
            #calculates unknown building vortex strengths
            self.calculate_unknown_vortex_strengths(vehicle)
        # --------------------------------------------------------------------
            V_gamma = self.calculate_induced_building_velocity(vehicle)


        # Velocity induced by 2D point sink, eqn. 10.2 & 10.3 in Katz & Plotkin:
        #calculate effect of sink
        V_sink = self.calculate_induced_sink_velocity(vehicle)
        # V_sink = vehicle.v_free_stream

        # W_sink = self.calculate_all_induced_sink_velocities3D(vehicles)[:, 2]
        # Velocity induced by 2D point source, eqn. 10.2 & 10.3 in Katz & Plotkin:
        if vehicle.personal_vehicle_dict:
            V_source = self.calculate_induced_source_velocities_on_main_vehicle(vehicle)
            # V_source = self.experimental_induced_source(vehicle)
            # V_vortex = self.calculate_induced_vortex_velocities_on_main_vehicle(vehicle)
            V_vortex = np.array([-V_source[1], V_source[0]]) / 4
            # TODO everything involving W_source is super dodgy, why are we only using the z component, weird... needs serious testing
            # Velocity induced by 3-D point sink. Katz&Plotkin Eqn. 3.25

        t = time.time()
        # Pre-calculate the arrays
    
        
        #########################################################################################################################
        # FIXME remove the for loop later and replace with this when it works
        # # Summing the effects for all vehicles at once
        V_sum = V_gamma + V_sink + V_source + V_vortex + vehicle.v_free_stream
        # Added a small constant to avoid division by zero
        V_sum /= (np.linalg.norm(V_sum)+1e-10)
        # Normalization and flow calculation for all vehicles
        flow_vels = V_sum   # no need to normalise if this is done in vehicle, TODO could normalise here instead, need to decide
        #########################################################################################################################
        return flow_vels

#vortexL lines 289, 232, 180

if __name__ == "__main__":
    def add_one(n:float)->float:
        return n+1
    
    def distance_effect_function(distance_array: np.ndarray) -> np.ndarray:
        """Drop-off effect based on distance, accepting an array of distances."""
        max_distance = 3
        ratio = distance_array / max_distance
        linear_dropoff = 1 - ratio
        exponential_dropoff = 1 / (1 + np.exp(10 * (ratio - 0.7)))
        
        effect = np.zeros_like(distance_array)  # Initialize array to store results

        # Apply conditions
        near_indices = distance_array < 1
        far_indices = ~near_indices  # Elements not satisfying the 'near' condition

        effect[near_indices] = (1 / (2 * np.pi * distance_array[near_indices] ** 4))
        effect[far_indices] = (1 / (2 * np.pi * distance_array[far_indices] ** 2)) * exponential_dropoff[far_indices]

        return effect
    
    x = np.arange(0.5,3,0.05)
    y = distance_effect_function(x)
    import matplotlib.pyplot as plt
    fig,ax = plt.subplots(figsize = (8,8))
    ax.plot(x,y)
    # ax.plot(x,1-x/3)
    # ax.plot(x,(1/(2 * np.pi * x**4)))
    # ax.plot(x,1/(1+np.e**(10*(x/3-0.7)))

    plt.show()
    
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
