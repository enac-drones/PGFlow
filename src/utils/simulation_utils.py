from src.vehicle import Vehicle
from typing import List
from src.cases import Case

def step_simulation(list_of_vehicles: List[Vehicle]):
    """'Step the simulation by one timstep"""
    for vehicle in list_of_vehicles:
        if vehicle.state != 1:
            vehicle.run_simple_sim()
    return None


def update_positions(case_vehicle_list: List[Vehicle]):
    """Go through case.vehicle_list and update each drone's personal vehicle list with
    its own current position and the positions of any other drones that are transmitting"""
    for index, vehicle in enumerate(case_vehicle_list):
        # the following updates my own position within my own vehicle list (I am the current vehicle)
        me_according_to_me = vehicle.personal_vehicle_list[index]
        me_according_to_me.position = vehicle.position
        # now update the rest of the current vehicle's personal vehicle list with the drones that are transmitting
        for idx, personal_vehicle in enumerate(vehicle.personal_vehicle_list):
            other_vehicle = case_vehicle_list[idx]
            if other_vehicle.transmitting and idx != index:
                personal_vehicle.position = case_vehicle_list[idx].position
    return None





def run_simulation(case: Case, t=500, update_every: int = 1, stop_at_collision = False):
    """function which runs the simulation for t seconds while updating the drone positions wrt each other every update_time seconds
    Returns true if simulation run to the end without collistions, False if there is a collision. Note the collision threshold
    is an attribute of the Case class and can be set with case.collision_threshold = 5 for updates every 5 seconds"""
    collisions = False
    for i in range(t):
        # Step the simulation
        step_simulation(case.vehicle_list)
        if case.colliding():
            # a collision has been detected, do whatever you want
            collisions = True
            if stop_at_collision:
                return False
        # Communication Block
        # Update positions
        for vehicle in case.vehicle_list:
            if i % update_every == 0:
                vehicle.transmitting = True
            else:
                vehicle.transmitting = False

        update_positions(case.vehicle_list)

        # if vehicle.state == 1:
        #     # print('Vehicle ', str(index), 'has reached the goal', i)
        #     pass
    if collisions:
        return False
    return True

