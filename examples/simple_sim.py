# from gflow.arena import ArenaMap
# from gflow.building import Building

import os

import gflow.utils as ut
from gflow.cases import Cases
from gflow.vehicle import Vehicle
from typing import List


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


def run_simulation(t = 500):

    for i in range(t):
        # Step the simulation
        step_simulation(case.vehicle_list)
        if case.colliding():
            # a collision has been detected, do whatever you want
            pass
        # Communication Block
        # Update positions

        # uncomment lines below to set transmitting to False whenever you want
        # case.vehicle_list[0].transmitting = False
        # case.vehicle_list[1].transmitting = False
        # case.vehicle_list[2].transmitting = False

        update_positions(case.vehicle_list)

        # if vehicle.state == 1:
        #     # print('Vehicle ', str(index), 'has reached the goal', i)
        #     pass


if __name__ == '__main__':
    # example run
    abs_file = os.path.dirname(os.path.abspath(__file__))

    # the two lines below allow you to generate a new random case with n drones
    if False:
        generator = Cases()
        generator.generate_random_case(case_name="random20", n_drones=20)

    case = Cases.get_case(filename=f"{abs_file}/cases.json", case_name="threedrones")

    #some code to show how to change sink_strengths or source_strengths once the case has been initialised
    v_list = case.vehicle_list
    for vehicle in v_list:
        vehicle.sink_strength = 5
        vehicle.source_strength = 0.5

    case.vehicle_list = v_list
    run_simulation(t=500)
    trajectory_plot = ut.plot_trajectories2(case.arena, case.arena, case.vehicle_list)
    trajectory_plot.show()

# EOF
