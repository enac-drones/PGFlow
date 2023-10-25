from __future__ import annotations
import numpy as np
# import scipy
# from numpy import linalg
from typing import List
from .panel_flow import Flow_Velocity_Calculation
from gflow.panel_flow_class import PanelFlow

"""##Vehicles"""


class PersonalVehicle:
    """Vehicle with the minimal required information: position, velocity, altitude, state etc"""

    def __init__(self, ID, position, source_strength, sink_strength, goal) -> None:
        self.ID = ID
        self.position = position
        self.source_strength = source_strength
        self.imag_source_strength = 0.75
        self.sink_strength = sink_strength
        self.goal = goal
        self.state = 0
        self.V_inf = [0, 0]
        
        # self.max_speed = 1.0
        # self.delta_t = 1 / 50


# from dataclasses import dataclass

# @dataclass
# class VehicleSerializer:
#     ID:str
#     position:tuple

#     def __init__(self,instance:Vehicle) -> None:
#         self.serialize(instance)
#         self.instance=instance

#     def serialize(instance:Vehicle):
#         ...

#     def data()->Dict:
#         return {

#         }

# v= VehicleSerializer(instance=vehicle,**vehicle.basic_attrs)


class Vehicle:
    def __init__(
        self, ID, source_strength=0, imag_source_strength=0.75, correction_type="none"
    ):
        self.t = 0
        self._arena = None
        self.position = np.zeros(3)
        self.desiredpos = np.zeros(3)
        self.correction = np.zeros(3)
        self.velocity = np.zeros(3)
        self.goal = np.zeros(3)
        self.source_strength = source_strength
        self.sink_strength = 0
        self.imag_source_strength = imag_source_strength
        self.gamma = 0
        self.altitude_mask = None
        self.ID = ID
        self.path = []
        # FIXME there is a magic number of 0.2 for the destination, fix this
        self.state = 0
        self.distance_to_destination = None
        # originally 1/50
        self.delta_t = 1 / 50  # 1/300 or less for vortex method, 1/50 for hybrid
        self.velocity_desired = np.zeros(3)
        self.velocity_corrected = np.zeros(3)
        self.vel_err = np.zeros(3)
        self.correction_type = correction_type
        self._personal_vehicle_list: List["Vehicle"] = []
        self.transmitting = True
        self.max_speed = 0.5
        self.panel_flow = PanelFlow(self.personal_vehicle_list, self.arena,"Vortex")

    @property
    def arena(self):
        return self._arena

    @arena.setter
    def arena(self, arena):
        self._arena = arena


    @property
    def personal_vehicle_list(self):
        return self._personal_vehicle_list

    @personal_vehicle_list.setter
    def personal_vehicle_list(self, vehicle_list):
        # print("personal setter is called")
        self._personal_vehicle_list = vehicle_list

    def basic_properties(self):
        return (
            self.ID,
            self.position,
            self.source_strength,
            self.sink_strength,
            self.goal,
        )

    def Set_Position(self, pos):
        self.position = np.array(pos)
        self.path = np.array(pos)
        self.path = self.path.reshape(1, 3)
        # print(f"path = {self.path.shape}")
        # print('GOOOAAALLL : ', self.goal)
        if np.all(self.goal) is not None:
            self.distance_to_destination = np.linalg.norm(
                np.array(self.goal) - np.array(self.position)
            )
            if np.all(self.distance_to_destination) < 0.2:
                self.state = 1

    def Set_Velocity(self, vel):
        self.velocity = vel

    def Set_Goal(self, goal, goal_strength, safety):
        self.goal = np.array(goal)  # or just goal...FIXME
        self.sink_strength = goal_strength
        self.safety = safety
        # self.aoa = np.arctan2(self.goal[1]-self.position[1],self.goal[0]-self.position[0]) # Do we still need this ? FIXME

    def Set_Next_Goal(self, goal, goal_strength=5):
        self.state = 0
        self.goal = goal
        # self.sink_strength = goal_strength NOT USED FOR NOW

    def Go_to_Goal(self, altitude=1.5, AoAsgn=0, t_start=0, Vinfmag=0):
        self.AoA = (
            np.arctan2(self.goal[1] - self.position[1], self.goal[0] - self.position[0])
        ) + AoAsgn * np.pi / 2

        """
        print( " AoA "    +  str( self.AoA*180/np.pi ) )
        print( " goal "   +  str( self.goal ) )
        print( " pos "    +  str( self.position ) )
        print( " AoAsgn " +  str( AoAsgn ) )
        print( " arctan " +  str( (np.arctan2(self.goal[1]-self.position[1],self.goal[0]-self.position[0]))*180/np.pi ) )
        """
        self.altitude = altitude
        self.Vinfmag = Vinfmag  # Cruise altitude
        self.V_inf = np.array(
            [self.Vinfmag * np.cos(self.AoA), self.Vinfmag * np.sin(self.AoA)]
        )  # Freestream velocity. AoA is measured from horizontal axis, cw (+)tive
        self.t = t_start

    def run_simple_sim(self):
        # these are the flow velocities induced on every vehicle (based off the personal vehicle list), stored as a list
        # print("before", [np.linalg.norm(v.position) for v in self.personal_vehicle_list])
        flow_vels = self.panel_flow.Flow_Velocity_Calculation(
            self.personal_vehicle_list, self.arena, method="Vortex"
        )
        # now update my own velocity
        index = next(
            (
                index
                for index, p_v in enumerate(self.personal_vehicle_list)
                if p_v.ID == self.ID
            ),
            None,
        )

        # self.update_position(flow_vels[index], self.arena)
        self.Update_Velocity(flow_vels[index], self.arena)

        # print("after ", [np.linalg.norm(v.position) for v in self.personal_vehicle_list])

    def update_position(self, flow_vel, arenamap):
        """Updates my position within the global vehicle_list given the induced flow from other vehicles onto me, self.velocity is used, so that the movement is less brutal"""

        # K is vehicle speed coefficient, a design parameter
        # flow_vels = flow_vels * self.delta_t
        V_des = flow_vel
        # magnitude of the induced velocity vector
        mag = np.linalg.norm(V_des)
        # print(f"magnitude = {mag}")
        # induced velocity unit vector
        V_des_unit = V_des / mag
        # set z component to 0
        V_des_unit[2] = 0
        # force mag to lie between 0 and 1
        mag_clipped = np.clip(mag, 0.0, self.max_speed)  # 0.3 tello 0.5 pprz
        # define new mag (rename for some reason)
        # mag_clipped = mag  # This is Tellos max speed 30Km/h
        # set the magnitude of the induced velocity vector to mag_converted (ie the clipped value between 0 and 1)
        clipped_velocity = V_des_unit * mag_clipped
        self.velocity += clipped_velocity
        self.velocity = self.velocity / np.linalg.norm(self.velocity)

        # multiply the flow velocity by some predefined constant, this is sort of like imposing the delaT
        # change in position = ds = v dt so velocitygain is actually dt here
        delta_s = self.velocity * self.delta_t
        # prevpos = self.position
        # self.desiredpos = self.position + np.array(delta_s)
        # print(f"{self.ID} was at {self.position}, ds = {delta_s}")
        # print(self.velocity)
        self.position = self.position + np.array(delta_s)
        # print(f"new position is {self.position}")

        self.path = np.vstack((self.path, self.position))
        # print(f"path = {self.path.shape}")
        # print(f"Drone {self.ID}, distance left = {np.linalg.norm(self.goal - self.position)}")
        if np.linalg.norm(self.goal - self.position) < 0.2:  # 0.1 for 2d
            self.state = 1
            # print(idx)
            # self.personal_vehicle_list[idx].state = 1
            # print([v.state for v in self.personal_vehicle_list])
            # print("Goal reached")
        return self.position

    def Update_Velocity(self, flow_vel, arenamap):
        """Updates my position within the global vehicle_list given the induced flow from other vehicles onto me"""

        # K is vehicle speed coefficient, a design parameter
        # flow_vels = flow_vels * self.delta_t
        #########################################
        #TODO currently array is 2D, so add a third dimension for compatibility
        # V_des = flow_vel
        V_des = np.append(flow_vel, 0)
        #########################################
        # magnitude of the induced velocity vector
        mag = np.linalg.norm(V_des)
        # print(f"magnitude = {mag}")
        # induced velocity unit vector
        V_des_unit = V_des / mag
        # set z component to 0 TODO removed for now because focusing on 2d
        #########################################
        # V_des_unit[2] = 0
        #########################################
        # force mag to lie between 0 and 1
        mag_clipped = np.clip(mag, 0.0, self.max_speed)  # 0.3 tello 0.5 pprz
        # define new mag (rename for some reason)
        # mag_clipped = mag  # This is Tellos max speed 30Km/h
        # set the magnitude of the induced velocity vector to mag_converted (ie the clipped value between 0 and 1)
        clipped_velocity = V_des_unit * mag_clipped
        # multiply the flow velocity by some predefined constant, this is sort of like imposing the delaT
        # change in position = ds = v dt so velocitygain is actually dt here
        # delta_s = clipped_velocity * self.delta_t
        delta_s = V_des_unit * self.delta_t * self.max_speed  # use unit velocity

        # print(f"{self.ID} was at {self.position}, ds = {delta_s}")
        # print(self.velocity)
        self.position = self.position + np.array(delta_s)
        # print(f"new position is {self.position}")

        self.path = np.vstack((self.path, self.position))

        if np.linalg.norm(self.goal - self.position) < 0.2:  # 0.1 for 2d
            # goal has been reached
            self.state = 1
        return self.position

    def arrived(self):
        """Similar to state but using the current live position"""
        arrived = np.linalg.norm(self.goal - self.position) < 0.2
        return arrived  # 0.1 for 2d
        # self.state = 1
