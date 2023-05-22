# from gflow.arena import ArenaMap
# from gflow.building import Building

import os

import gflow.utils as ut
from gflow.cases import Cases
from gflow.vehicle import Vehicle

# from gflow.smart_input import create_buildings
# from cases import Cases
# Case = Cases(117,Arena,'manual')
# Case = Cases(13,Arena,'manual')
# Case.arena  = ArenaMap(6,)
# Case.arenaR = ArenaMap(6,)
# Case.arena.Inflate(radius = 0.2) #0.1
# Case.arena.Panelize(size= 0.01) #0.08
# Case.arena.Calculate_Coef_Matrix(method = 'Vortex')
# buildings = create_buildings()
# print(f"buildings are {buildings}")
# print("hi")
# case1 = Cases()
abs_file = os.path.dirname(os.path.abspath(__file__))
# case1.add_case("d",1,1)
generator = Cases()
# generator.generate_random_case(case_name="random10", n_drones=10)
case = Cases.get_case(filename=f"{abs_file}/cases.json", case_name="random10")
# print("Hi")
# v_list = case.vehicle_list
# for vehicle in v_list:
#     vehicle.sink_strength = 15

# print("hi")
# case.vehicle_list = v_list

# print(case.vehicle_list[0].sink_strength)


for i in range(2500):
    # print(i)
    # Step the simulation
    for index, vehicle in enumerate(case.vehicle_list):
        if vehicle.state != 1:
            # print(vehicle.sink_strength)
            vehicle.run_simple_sim()
            # print(vehicle.pos)

    # Communication Block
    # Update positions
    for index, vehicle in enumerate(case.vehicle_list):
        # Update only self position
        vehicle.vehicle_list[index].position = vehicle.position

        # Update the listed vehicle numbers wrt every one
        # the numbers in the if statement within the list, separated by commas indicate which drones are providing their position
        if index in []:
            for list_index in range(len(vehicle.vehicle_list)):
                vehicle.vehicle_list[list_index].position = case.vehicle_list[
                    list_index
                ].position  # calling case.Vehicle is not nice here... 1 unneccessary element update

        if vehicle.state == 1:
            # print('Vehicle ', str(index), 'has reached the goal', i)
            pass


asdf = ut.plot_trajectories2(case.arena, case.arena, case.vehicle_list)
asdf.show()

# EOF
