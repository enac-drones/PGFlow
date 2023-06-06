# from gflow.arena import ArenaMap
# from gflow.building import Building

import os

from src.utils.plot_utils import plot_trajectories2
from src.cases import Cases, Case
from src.vehicle import Vehicle
from typing import List
import time
from src.utils.json_utils import dump_to_json


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


def run_simulation(case: Case, t=500, update_every: int = 1):
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
            # uncomment this line if you want the simulation to continue after a collision
            # return False
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


def optional_plot(case: Case):
    plot = plot_trajectories2(case.arena, case.arena, case.vehicle_list)
    plot.slider.set_val(1.0)
    plot.ax.set_title(f"Case number {idx+1}/{n_cases}")
    plot.show()


def new_random_cases(n_cases, n_drones):
    base_case_name = f"random{n_drones}"
    file_name = f"data/{base_case_name}.json"

    for idx in range(n_cases):
        generator = Cases(filename=file_name)
        case_name = f"{base_case_name}_{idx}"
        generator.generate_random_case(case_name=case_name, n_drones=n_drones)
    return None


def set_new_attribute(case_instance: Case, attribute_name: str, new_attribute_value):
    """change attributes such as sink strength for every vehicle in a case"""
    if not hasattr(Vehicle(ID="hi"), attribute_name):
        print(f"Attribute {attribute_name} does not exist in the Vehicle class.")
        return None
    v_list = case_instance.vehicle_list
    for vehicle in v_list:
        # vehicle.sink_strength = 5*4/3
        vehicle.source_strength = 2
    case.vehicle_list = v_list
    return True


def run_specific_case(file_name, case_name, update_frequency):
    case = Cases.get_case(filename=file_name, case_name=case_name)
    # optional:
    set_new_attribute(case, "source_strength", new_attribute_value=20)
    print(f"case source_strength = {case.vehicle_list[0].source_strength}")
    print(
        f"personal source_strengths = {case.vehicle_list[0].personal_vehicle_list[0].source_strength}"
    )

    simulation_succeeded = run_simulation(
        case=case, t=500, update_every=update_frequency
    )
    optional_plot(case)
    return simulation_succeeded


#%%
if __name__ == "__main__":
    plot_done = False
    n_drones: int = 3
    base_case_name = f"random{n_drones}"
    file_name = f"data/{base_case_name}.json"
    n_cases = 1

    # new_random_cases(n_cases,n_drones)
    update_frequency = [1, 2, 3, 4, 5, 10, 50, 100, 200, 300, 400, 500]
    # update_every_cases = [10]
    corresponding_failures = {}
    for num in update_frequency:
        print("new update rate started")
        total_failures = 0
        for idx in range(n_cases):
            case = Cases.get_case(
                filename=file_name, case_name=f"{base_case_name}_{idx}"
            )

            print(f"running case {idx} for update rate every {num} seconds")

            # some code to show how to change sink_strengths or source_strengths once the case has been initialised
            set_new_attribute(case, "source_strength", new_attribute_value=20)
            # print(f"case source_strength = {case.vehicle_list[0].source_strength}")
            # print(f"personal source_strengths = {case.vehicle_list[0].personal_vehicle_list[0].source_strength}")

            simulation_succeeded = run_simulation(case=case, t=500, update_every=num)

            if not simulation_succeeded:
                failure_index = idx
                print(f"the case which failed was {base_case_name}_{idx}")
                # if not plot_done:
                #     optional_plot(case)
                #     plot_done = True
                total_failures += 1

        # print(f"There were {total_failures} failures out of {n_cases} when updating every {num} seconds")
        corresponding_failures[num] = total_failures
    print(corresponding_failures)
    dump_to_json(f"results/{base_case_name}.json", corresponding_failures)
    run_specific_case(
        file_name=file_name, case_name=f"{base_case_name}_3", update_frequency=1
    )


# EOF
# 3 drones:
# 1:38, 2: 41, 3:57/50, 4:49, 5:50,10:63,50:113, 100:145, 200: 202, 300:207, 400:231, 500:248

# %%
