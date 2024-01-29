from __future__ import annotations
import numpy as np
# import scipy
# from numpy import linalg
from typing import List
from numpy.typing import ArrayLike
# from .panel_flow import Flow_Velocity_Calculation
from gflow.panel_flow import PanelFlow
from gflow.arena import ArenaMap
from gflow.building import PersonalBuilding, Building
from shapely.geometry import Point
from gflow.PIDcontroller import VehicleDynamics, PIDController
# from gflow.panel_flow_class import PanelFlow


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
    #state is unnused in PersonalVehicle FIXME for now
    state:int = 0


class Vehicle:
    _id_counter = 0

    def __init__(
        self, source_strength:float=0, imag_source_strength:float=0.75):
        self.ID = f"V{Vehicle._id_counter}"
        Vehicle._id_counter += 1
        self._position=np.zeros(3)
        self.goal = np.zeros(3)
        self.source_strength:float =source_strength
        self.sink_strength:float=0
        self.imag_source_strength:float = imag_source_strength
        
        self.max_avoidance_distance:float = 20
        self.panel_flow = PanelFlow(self)
        Kp, Ki, Kd = 40, 0.1, 30
        self.dynamics = VehicleDynamics(mass = 1, min_accel=-2, max_accel=2)
        self.pid_x = PIDController(Kp, Ki, Kd, self.dynamics.min_accel, self.dynamics.max_accel)
        self.pid_y = PIDController(Kp, Ki, Kd, self.dynamics.min_accel, self.dynamics.max_accel)
        self.desired_vectors = []
        self.pid_output = []

        self.arena:ArenaMap = None
        
        # self.desiredpos = np.zeros(3)
        self.velocity = np.zeros(3)
        self.path = np.zeros((1,3))
        # FIXME there is a magic number of 0.2 for the destination, fix this
        self.state = 0
        # originally 1/50
        self.delta_t = 1 / 50  # 1/300 or less for vortex method, 1/50 for hybrid
        self.personal_vehicle_dict: dict[str,PersonalVehicle] = []
        self.relevant_obstacles:list[Building] = []
        self.transmitting = True
        self.max_speed = 0.8
        self.ARRIVAL_DISTANCE = 0.2

        self.has_landed = False
        self.turn_radius:float = 0.1 #max turn radius in meters
        self.v_free_stream:np.ndarray = np.zeros(2) #velocity constantly pushing the vehicle towards its goal

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_position):
        self._position = new_position
        vector_to_goal = (self.goal - new_position)[:2]
        if np.all(vector_to_goal==0):
            # non zero vector of ones in case the vehicle is exactly on the goal
            self.v_free_stream = np.ones(2)
        else:
            self.v_free_stream = 0.5*vector_to_goal/np.linalg.norm(vector_to_goal)



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
        return None
    
    def update_nearby_buildings(self, threshold:float = 5)->None:
        # position = Point(self.position)
        self.relevant_obstacles = self.arena.get_nearby_buildings(self.position, threshold)
        for building in self.relevant_obstacles:
            if building.K_inv is None:
                
                building.panelize(self.arena.size)
                building.calculate_coef_matrix()
        # print(self.relevant_obstacles)
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

    def Set_Goal(self, goal, goal_strength):
        self.goal = np.array(goal)
        self.sink_strength = goal_strength
     
    def run_simple_sim(self, mode:str):
        '''run one iteration of the simulation
        mode:str (standard | radius | pid)'''
        # these are the flow velocities induced on every vehicle (based off the personal vehicle list), stored as a list
        flow_vels = self.panel_flow.Flow_Velocity_Calculation(self)
        
        if mode == 'radius':
            self.update_position_max_radius(flow_vels)
        elif mode == 'pid':
            self.update_position_pid(flow_vels)
        else:
            self.update_position_clipped(flow_vels)


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
        self.desired_vectors.append(V_des_unit[:2].tolist())


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
    
    def update_position_max_radius(self, flow_vel:np.ndarray):
        """Updates my position within the global vehicle_list given the induced flow from other vehicles onto me"""
        # print(f"{flow_vel=}")
        # magnitude of the induced velocity vector in 2D
        mag = np.linalg.norm(flow_vel)
        # induced velocity unit vector
        # if mag == 0 or np.isnan(mag):
        unit_new_velocity = flow_vel / mag
        self.desired_vectors.append(unit_new_velocity.tolist())

        speed = np.linalg.norm(self.velocity[:2])
        if speed == 0:
            # initial velocity is just new velocity at start of simulation
            unit_old_velocity = unit_new_velocity
        else:
            unit_old_velocity= self.velocity[:2]/speed
        
        if not self.turn_radius < self.max_speed*self.delta_t/2:

            # this can be below -1 if the radius is less than vdt/2 which makes the turn radius mathematically unachievable 
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
        
        # multiply the flow velocity by some predefined constant to set max speed 
        self.velocity = unit_new_velocity * self.max_speed
        # print(self.velocity)
        delta_s = self.velocity * self.delta_t   # use unit velocity
        
        self.position = self.position + np.array(delta_s)

        self.path = np.vstack((self.path, self.position))

        if self.arrived(arrival_distance = self.ARRIVAL_DISTANCE):
            print("goal is reached")
            # goal has been reached
            self.state = 1
        return self.position
    
    def update_position_pid(self, flow_vel:ArrayLike)->None:
        """Updates my position within the global vehicle_list given the induced flow from other vehicles onto me"""

        # magnitude of the induced velocity vector in 2D
        mag = np.linalg.norm(flow_vel)
        # induced velocity unit vector
        # if mag == 0 or np.isnan(mag):
        unit_new_velocity = flow_vel / mag

        # print(f"{self.ID}, {unit_new_velocity=}")
        self.desired_vectors.append(unit_new_velocity.tolist())
        # speed = np.linalg.norm(self.velocity[:2])

        #define desired position
        desired_position = self.position[:2] + unit_new_velocity*self.delta_t*10


        x_desired, y_desired = desired_position[0], desired_position[1]
        # vx_desired, vy_desired = unit_new_velocity[0], unit_new_velocity[1]

        #define current position and velocity
        x, y = self.position[0], self.position[1]
        vx,vy = self.velocity[0], self.velocity[1]

        #obtain error
        error_x = x_desired - x
        error_y = y_desired - y

        # error_x = vx_desired - vx
        # error_y = vy_desired - vy

        #obtain desired accelerations from pid controllers
        ax = self.pid_x.update(error_x, self.delta_t) 
        ay = self.pid_y.update(error_y, self.delta_t)

        #define velocity limits
        min_velocity, max_velocity = -1,1,

        # Adjust acceleration based on current velocity and limits
        # print(vx, ax, max_velocity, min_velocity, self.delta_t)
        ax = self.pid_x.adjust_acceleration(vx, ax, max_velocity, min_velocity, self.delta_t)
        ay = self.pid_y.adjust_acceleration(vy, ay, max_velocity, min_velocity, self.delta_t)

        self.pid_output.append([ax,ay])
        # x, vx, y, vy = update_drone_state(x, vx, y, vy, ax, ay, dt)
        x, vx, y, vy = self.dynamics.update_state_verlet(x, vx, y, vy, ax, ay, self.delta_t)
        #set vehicle state to new state
        self.position = np.array([x, y,self.position[2]])  
        # self.position = np.array([x,y,self.position[2]])
        # print(self.position)
        self.velocity[0], self.velocity[1] = vx, vy 
        # print(vx,vy)
        # print(np.linalg.norm(self.velocity[:2]))
        # print(vx,vy)

        self.path = np.vstack((self.path, self.position))

        if self.arrived(arrival_distance = self.ARRIVAL_DISTANCE):
            print("goal is reached")
            # goal has been reached
            self.state = 1
        

    def arrived(self, arrival_distance):
        """Similar to state but using the current live position"""
        arrived = np.linalg.norm(self.goal - self.position) < arrival_distance
        return arrived  # 0.1 for 2d
        # self.state = 1


# if __name__ == "__main__":
#     import pickle

#     vehicle_instance = Vehicle(ID="v1")  # Replace with whatever constructor arguments you use

#     try:
#         serialized = pickle.dumps(vehicle_instance)
#         print("Vehicle is pickleable!")
#     except (pickle.PicklingError, AttributeError, TypeError) as e:
#         print(f"Vehicle is not pickleable! Error: {e}")

