from __future__ import annotations
import numpy as np
# import scipy
# from numpy import linalg
from typing import List
from numpy.typing import ArrayLike
# from .panel_flow import Flow_Velocity_Calculation
from PGFlow.panel_flow_individual import PanelFlow
from PGFlow.arena import ArenaMap



"""##Vehicles"""

from dataclasses import dataclass, field

@dataclass(slots=True)
class PersonalVehicle:
    """Vehicle with the minimal required information: position, velocity, altitude, state etc"""
    ID:str
    position:ArrayLike
    goal:ArrayLike
    source_strength:float
    sink_strength:float
    imag_source_strength:float = 0.75
    #state is unnused in PersonalVehicle
    state:int = 0
    # not sure what V_inf is for
    V_inf: List[float] = field(default_factory=lambda: [0, 0]) 


class Vehicle:
    _id_counter = 0

    def __init__(
        self, ID=1, source_strength:float=0, imag_source_strength:float=0.75):
        self.ID = f"V{Vehicle._id_counter}"
        Vehicle._id_counter += 1
        self._position=np.zeros(3)
        self.goal = np.zeros(3)
        self.source_strength:float =source_strength
        self.sink_strength:float=0
        self.imag_source_strength:float = imag_source_strength
        
        self.max_avoidance_distance:float = 20
        self.panel_flow = PanelFlow(self)
        
        self.t = 0
        self._arena:ArenaMap = None
        
        self.desiredpos = np.zeros(3)
        self.correction = np.zeros(3)
        self.velocity = np.zeros(3)
        # self.gamma = 0
        # self.altitude_mask = None
        # self.ID = ID
        self.path = []
        # FIXME there is a magic number of 0.2 for the destination, fix this
        self.state = 0
        self.distance_to_destination = None
        # originally 1/50
        self.delta_t = 1 / 50  # 1/300 or less for vortex method, 1/50 for hybrid
        self.velocity_desired = np.zeros(3)
        self.velocity_corrected = np.zeros(3)
        self.vel_err = np.zeros(3)
        #self.correction_type = correction_type
        self.personal_vehicle_dict: dict[str,Vehicle] = []
        self.transmitting = True
        self.max_speed = 0.8
        self.ARRIVAL_DISTANCE = 0.2
        self.safety = None
        self.AoA = None
        self.altitude = None
        self.Vinfmag = None
        self.V_inf = [0,0]
        self.has_landed = False
        self.turn_radius:float = 0.5 #max turn radius in meters

    @property
    def arena(self):
        return self._arena

    @arena.setter
    def arena(self, arena):
        self._arena = arena


    # @property
    # def personal_vehicle_dict(self):
    #     return self._personal_vehicle_dict

    # @personal_vehicle_dict.setter
    # def personal_vehicle_dict(self, vehicle_list:list[Vehicle]):
    #     self._personal_vehicle_dict = vehicle_list

    def update_personal_vehicle_dict(self,case_vehicle_list:list[Vehicle], max_avoidance_distance:float=100.)->None:
        for v in case_vehicle_list:
            # overall options are: keep my previous knowledge, update it, or remove the drone entirely
            if v.ID == self.ID:
                # we should not be in our own list, so remove us if we are
                # TODO in future we should never be added in the first place so FIXME
                self.personal_vehicle_dict.pop(self.ID, None)
                # self.personal_vehicle_dict[self.ID] = PersonalVehicle(**v.basic_properties())
                continue
            if v.transmitting == True:
                # other vehicle is transmitting so either take the newer vehicle info or remove it entirely if too far or arrived
                if v.state == 1:
                    # arrived, so remove from list, we don't care about it
                    # pass
                    self.personal_vehicle_dict.pop(v.ID, None)

                else:
                    # not arrived, check if close enough
                    if (
                        np.linalg.norm(v.position - self.position)
                        > max_avoidance_distance
                    ):
                        # too far, remove
                        self.personal_vehicle_dict.pop(v.ID, None)
                    else:
                        # not too far, update or add
                        self.personal_vehicle_dict[v.ID] = PersonalVehicle(**v.basic_properties())
            else:
                # not transmitting, keep the old, aka do nothing
                pass

        # Convert back to a list if necessary #FIXME should really have it as a dictionary the whole time let's be honest
        # valid_personal_vehicle_list = list(personal_vehicle_dict.values())
        return None

    def basic_properties(self):
        return {
            'ID': self.ID,
            'position': self.position,
            'goal': self.goal,
            'source_strength': self.source_strength,
            'sink_strength': self.sink_strength,
        }

    def set_initial_position(self, pos):
        self.position = np.array(pos)
        self.path = np.array(pos)
        self.path = self.path.reshape(1, 3)
        if self.arrived(self.ARRIVAL_DISTANCE):
            self.state=1

    def Set_Position(self, pos):
        self.position = np.array(pos)
        self.path = np.array(pos)
        self.path = self.path.reshape(1, 3)
        if np.all(self.goal) is not None:
            self.distance_to_destination = np.linalg.norm(
                np.array(self.goal) - np.array(self.position)
            )
            if np.all(self.distance_to_destination) < 0.2:
                self.state = 1

    def Set_Velocity(self, vel):
        self.velocity = vel

    def Set_Goal(self, goal, goal_strength):
        self.goal = np.array(goal)  # or just goal...FIXME
        self.sink_strength = goal_strength
        # self.safety = safety
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
        flow_vels = self.panel_flow.Flow_Velocity_Calculation(self,
            self.personal_vehicle_dict, method="Vortex"
        )
        # now update my own velocity
        # index = next(
        #     (
        #         index
        #         for index, p_v in enumerate(self.personal_vehicle_dict.values())
        #         if p_v.ID == self.ID
        #     ),
        #     None,
        # )

        # self.update_position(flow_vels[index], self.arena)
        
        # self.update_position_clipped(flow_vels)
        self.update_position_max_radius(flow_vels)


    def update_position(self, flow_vel):
        """Updates my position within the global vehicle_list given the induced flow from other vehicles onto me, self.velocity is used, so that the movement is less brutal"""

        # K is vehicle speed coefficient, a design parameter
        # flow_vels = flow_vels * self.delta_t
        V_des = flow_vel
        # magnitude of the induced velocity vector
        mag = np.linalg.norm(V_des)
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

        self.position = self.position + np.array(delta_s)

        self.path = np.vstack((self.path, self.position))
        if self.arrived(arrival_distance=self.ARRIVAL_DISTANCE):  # 0.1 for 2d
            self.state = 1


        return self.position

    def update_position_clipped(self, flow_vel):
        """Updates my position within the global vehicle_list given the induced flow from other vehicles onto me"""

        
            # import sys
            # sys.exit()
        # K is vehicle speed coefficient, a design parameter
        # flow_vels = flow_vels * self.delta_t
        #########################################
        #TODO currently array is 2D, so add a third dimension for compatibility
        # V_des = flow_vel
        V_des = np.append(flow_vel, 0)
        #########################################
        # magnitude of the induced velocity vector
        mag = np.linalg.norm(V_des)
        # induced velocity unit vector
        # if mag == 0 or np.isnan(mag):
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
        self.velocity = V_des_unit * self.max_speed
        delta_s = self.velocity * self.delta_t   # use unit velocity
        
        self.position = self.position + np.array(delta_s)

        self.path = np.vstack((self.path, self.position))

        if self.arrived(arrival_distance = self.ARRIVAL_DISTANCE):
            print("goal is reached")
            # goal has been reached
            self.state = 1
        return self.position
    
    def update_position_max_radius(self, flow_vel):
        """Updates my position within the global vehicle_list given the induced flow from other vehicles onto me"""

        
            # import sys
            # sys.exit()
        # K is vehicle speed coefficient, a design parameter
        # flow_vels = flow_vels * self.delta_t
        #########################################
        #TODO currently array is 2D, so add a third dimension for compatibility
        # V_des = flow_vel
        #########################################
        # magnitude of the induced velocity vector in 2D
        mag = np.linalg.norm(flow_vel)
        # induced velocity unit vector
        # if mag == 0 or np.isnan(mag):
        unit_new_velocity = flow_vel / mag

        speed = np.linalg.norm(self.velocity)
        unit_old_velocity= self.velocity[:2]/np.linalg.norm(speed)
        # min_cos = (1-(speed*self.delta_t/self.turn_radius)**2)/(1+(speed*self.delta_t/self.turn_radius)**2)
        
        min_cos = 1-0.5*(speed*self.delta_t/self.turn_radius)**2
        # Calculate the angle in radians, and then convert it to degrees
        # The np.clip is used to handle potential floating-point arithmetic issues that might push the dot product 
        # slightly outside the range [-1, 1], which would cause np.arccos to return NaN
        cos_angle = (np.clip(np.dot(unit_new_velocity, unit_old_velocity), -1.0, 1.0))

        if cos_angle < min_cos:
            max_theta = np.arccos(np.clip(min_cos, -1.0, 1.0))
            #in numpy cross product of two 2d vectors returns the z component of the resulting vector
            cross_product = np.cross(unit_new_velocity, unit_old_velocity)

            # print(cross_product,unit_new_velocity,unit_old_velocity)
            if cross_product>0:
                #clockwise
                theta = -max_theta
            else:
                #anti_clockwise
                theta = max_theta
            
            # Create the rotation matrix
            rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)], 
                                [np.sin(theta),  np.cos(theta)]])
            
            # Rotate the vector
            unit_new_velocity = np.dot(rotation_matrix, unit_old_velocity)

        unit_new_velocity = np.append(unit_new_velocity, 0)



        # set z component to 0 TODO removed for now because focusing on 2d
        #########################################
        # V_des_unit[2] = 0
        #########################################
        # force mag to lie between 0 and 1
        # multiply the flow velocity by some predefined constant to set max speed 
        self.velocity = unit_new_velocity * self.max_speed
        delta_s = self.velocity * self.delta_t   # use unit velocity
        
        self.position = self.position + np.array(delta_s)

        self.path = np.vstack((self.path, self.position))

        if self.arrived(arrival_distance = self.ARRIVAL_DISTANCE):
            print("goal is reached")
            # goal has been reached
            self.state = 1
        return self.position

    def arrived(self, arrival_distance):
        """Similar to state but using the current live position"""
        arrived = np.linalg.norm(self.goal - self.position) < arrival_distance
        return arrived  # 0.1 for 2d
        # self.state = 1


if __name__ == "__main__":
    import pickle

    vehicle_instance = Vehicle(ID="v1")  # Replace with whatever constructor arguments you use

    try:
        serialized = pickle.dumps(vehicle_instance)
        print("Vehicle is pickleable!")
    except (pickle.PicklingError, AttributeError, TypeError) as e:
        print(f"Vehicle is not pickleable! Error: {e}")

