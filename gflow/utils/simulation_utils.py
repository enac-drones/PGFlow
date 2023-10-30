# from .. import vehicle, cases, panel_flow
from gflow.vehicle import Vehicle, PersonalVehicle
from gflow.cases import Case
from typing import List
import numpy as np
import time
# from gflow.panel_flow import Flow_Velocity_Calculation

# from gflow_local.panel_flow import Flow_Velocity_Calculation


def set_new_attribute(case: Case, attribute_name: str, new_attribute_value):
    """change attributes such as sink strength for every vehicle in a case"""
    if not hasattr(Vehicle(ID="hi"), attribute_name):
        print(f"Attribute {attribute_name} does not exist in the Vehicle class.")
        return None
    v_list = case.vehicle_list
    for vehicle in v_list:
        # vehicle.sink_strength = 5*4/3
        setattr(vehicle, attribute_name, new_attribute_value)
        # vehicle.source_strength = new_attribute_value
    case.vehicle_list = v_list

    return True


# def valid_vehicle_dict(
#     vehicle: Vehicle, case_vehicle_list: List[Vehicle], max_avoidance_distance
# ):
#     # First, convert personal_vehicle_list to a dictionary
#     # i.e. store my current knowledge of other drones
#     # personal_vehicle_dict = {v.ID: v for v in vehicle.personal_vehicle_list}

#     # case_vehicle_list is emulating the information that is available to me via radio etc
#     for v in case_vehicle_list:
#         # overall options are: keep my previous knowledge, update it, or remove the drone entirely
#         if v.ID in vehicle.personal_vehicle_dict:
#             # This is my own information, update my knowledge of myself with my own info
#             # This behaviour might be different when dealing with real drones
#             vehicle.personal_vehicle_dict[v.ID] = PersonalVehicle(*v.basic_properties())
#             continue

#         if v.transmitting == True:
#             # other vehicle is transmitting so either take the newer vehicle info or remove it entirely if too far or arrived
#             if v.state == 1:
#                 # arrived, so remove from list, we don't care about it
#                 # pass
#                 vehicle.personal_vehicle_dict.pop(v.ID, None)

#             else:
#                 # not arrived, check if close enough
#                 if (
#                     np.linalg.norm(v.position - vehicle.position)
#                     > max_avoidance_distance
#                 ):
#                     # too far, remove
#                     vehicle.personal_vehicle_dict.pop(v.ID, None)
#                 else:
#                     # not too far, update or add
#                     vehicle.personal_vehicle_dict[v.ID] = PersonalVehicle(*v.basic_properties())
#         else:
#             # not transmitting, keep the old, aka do nothing
#             pass

#     # Convert back to a list if necessary #FIXME should really have it as a dictionary the whole time let's be honest
#     # valid_personal_vehicle_list = list(personal_vehicle_dict.values())
#     return vehicle.personal_vehicle_dict


def step_simulation(case_vehicle_list: List[Vehicle], max_avoidance_distance=2):
    """'Step the simulation by one timstep, list_of_vehicles is case.vehicle_list"""
    for vehicle in case_vehicle_list:
        # if the current vehicle has arrived, do nothing, continue looking at the other vehicles
        if vehicle.state == 1:
            continue

        # update the vehicle's personal knowledge of other drones by only keeping those that meet specific conditions:
        # not too far, have not arrived yet, and are transmitting.
        # vehicle.personal_vehicle_dict = valid_vehicle_dict(
        #     vehicle, case_vehicle_list, max_avoidance_distance
        # )
        vehicle.update_personal_vehicle_dict(case_vehicle_list,max_avoidance_distance)

        # update my position in the case_vehicle_list
        vehicle.run_simple_sim()

    return None

# def step_simulation1(case_vehicle_list: List[Vehicle], max_avoidance_distance=2):
#     """'Step the simulation by one timstep, list_of_vehicles is case.vehicle_list"""
#     flow_vels = Flow_Velocity_Calculation(case_vehicle_list,case_vehicle_list[0].arena,"Vortex")
#     for index, vehicle in enumerate(case_vehicle_list):
#         # if the current vehicle has arrived, do nothing, continue looking at the other vehicles
#         if vehicle.state == 1:
#             continue

#         # # update the vehicle's personal knowledge of other drones by only keeping those that meet specific conditions:
#         # # not too far, have not arrived yet, and are transmitting.
#         # vehicle.personal_vehicle_list = valid_vehicle_list(
#         #     vehicle, case_vehicle_list, max_avoidance_distance
#         # )

#         # update my position in the case_vehicle_list
#         vehicle.Update_Velocity(flow_vels[index],vehicle.arena)

#     return None





# def update_positions(case_vehicle_list: List[Vehicle]):
#     """Go through case.vehicle_list and update each drone's personal vehicle list with
#     its own current position and the positions of any other drones that are transmitting"""
#     for _, vehicle in enumerate(case_vehicle_list):
#         # the following updates my own position within my own vehicle list (I am the current vehicle)
#         current_vehicle = next(
#             (p_v for p_v in vehicle.personal_vehicle_list if p_v.ID == vehicle.ID), None
#         )
#         if current_vehicle is not None:
#             current_vehicle.position = vehicle.position

#         # now update the rest of the current vehicle's personal vehicle list with the drones that are transmitting
#         for _, personal_vehicle in enumerate(vehicle.personal_vehicle_list):

#             other_vehicle = next(
#                 (
#                     v
#                     for v in case_vehicle_list
#                     if v.ID == personal_vehicle.ID and v.ID != vehicle.ID
#                 ),
#                 None,
#             )
#             # other_vehicle = case_vehicle_list[idx]
#             if other_vehicle is not None and other_vehicle.transmitting:
#                 personal_vehicle.position = other_vehicle.position
#     return None


def run_simulation(
    case: Case,
    t=500,
    update_every: int = 1,
    stop_at_collision=False,
    max_avoidance_distance=20,
):
    """function which runs the simulation for t seconds while updating the drone positions wrt each other every update_time seconds
    Returns true if simulation run to the end without collistions, False if there is a collision. Note the collision threshold
    is an attribute of the Case class and can be set with case.collision_threshold = 5 for updates every 5 seconds"""
    collisions = False
    # arrived = set()
    # case_vehicle_list = case.vehicle_list
    start_time = time.time()
    for i in range(t):
        # Step the simulation
        # step_simulation(case.vehicle_list,max_avoidance_distance)

        # this is faster than step_simulation, it avoids personal vehicle lists
        step_simulation(case.vehicle_list, max_avoidance_distance)

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

    end_time = time.time()
    print(f"Simulation took {end_time - start_time} seconds")
    if collisions:
        return False
    return True



