from gflow.vehicle import Vehicle
from gflow.cases import Case
from typing import List
import time



def set_new_attribute(case: Case, attribute_name: str, new_attribute_value):
    """change attributes such as sink strength for every vehicle in a case"""
    if not hasattr(Vehicle(), attribute_name):
        print(f"Attribute {attribute_name} does not exist in the Vehicle class.")
        return None
    v_list = case.vehicle_list
    for vehicle in v_list:
        setattr(vehicle, attribute_name, new_attribute_value)
    case.vehicle_list = v_list

    return True





def step_simulation(case:Case):
    case_vehicle_list = case.vehicle_list
    max_avoidance_distance = case.max_avoidance_distance
    """'Step the simulation by one timstep, list_of_vehicles is case.vehicle_list"""
    for vehicle in case_vehicle_list:
        # if the current vehicle has arrived, do nothing, continue looking at the other vehicles
        if vehicle.state == 1:
            continue
        # update the vehicle's personal knowledge of other drones by only keeping those that meet specific conditions:
        # not too far, have not arrived yet, and are transmitting.
        vehicle.update_personal_vehicle_dict(case_vehicle_list,max_avoidance_distance)
        vehicle.update_nearby_buildings(threshold = case.building_detection_threshold) #meters
        # print(vehicle.relevant_obstacles)

        # update my position in the case_vehicle_list
        vehicle.run_simple_sim()

    return None


def run_simulation(
    case: Case,
    t=500,
    update_every: int = 1,
    stop_at_collision=False
):
    """function which runs the simulation for t seconds while updating the drone positions wrt each other every update_time seconds
    Returns true if simulation run to the end without collistions, False if there is a collision. Note the collision threshold
    is an attribute of the Case class and can be set with case.collision_threshold = 5 for updates every 5 seconds"""
    collisions = False
    start_time = time.time()
    for i in range(t):
        # Step the simulation
        step_simulation(case)

        if case.colliding():
            # a collision has been detected, do whatever you want
            collisions = True
            if stop_at_collision:
                return False
        # Communication Block
        for vehicle in case.vehicle_list:
            if i % update_every == 0:
                vehicle.transmitting = True
            else:
                vehicle.transmitting = False

    end_time = time.time()
    print(f"Simulation took {end_time - start_time} seconds")
    if collisions:
        return False
    return True



