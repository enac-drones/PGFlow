from src.vehicle import Vehicle
from typing import List
from src.cases import Case

def step_simulation(case_vehicle_list:List[Vehicle]):
    """'Step the simulation by one timstep, list_of_vehicles is case.vehicle_list"""
    # case_vehicle_list:List[Vehicle] = case.vehicle_list
    for idx,vehicle in enumerate(case_vehicle_list):
        if vehicle.state != 1:
            vehicle.run_simple_sim()
            # if vehicle.state==1:
                # print(case_vehicle_list[idx].state)
        # if the current vehicle has reached its destination, tell the global vehicle list that it has (this is a bit dodgy but it works for now)
        # print([v.state for v in vehicle.personal_vehicle_list])
        if vehicle.personal_vehicle_list[idx].state == 1:
            vehicle.state=1
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
                personal_vehicle.position = other_vehicle.position
    return None





def run_simulation(case: Case, t=500, update_every: int = 1, stop_at_collision = False):
    """function which runs the simulation for t seconds while updating the drone positions wrt each other every update_time seconds
    Returns true if simulation run to the end without collistions, False if there is a collision. Note the collision threshold
    is an attribute of the Case class and can be set with case.collision_threshold = 5 for updates every 5 seconds"""
    collisions = False
    # case_vehicle_list = case.vehicle_list
    for i in range(t):
        # Step the simulation
        step_simulation(case.vehicle_list)
        print([v.state for v in case.vehicle_list])
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

        # case.vehicle_list = case_vehicle_list
        # if vehicle.state == 1:
        #     # print('Vehicle ', str(index), 'has reached the goal', i)
        #     pass
    if collisions:
        return False
    return True

