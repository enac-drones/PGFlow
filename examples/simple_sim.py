# from gflow.arena import ArenaMap
# from gflow.building import Building
# from src.vehicle import Vehicle
import src.utils.plot_utils as ut
from src.cases import Cases
from time import sleep, time
import numpy as np
from src.utils.simulation_utils import run_simulation
from examples.data_collection import set_new_attribute
# import multiprocessing
# from src.panel_flow import vortex_calculation_time
# from gflow.smart_input import create_buildings


# from cases import Cases
# Case = Cases(117,Arena,'manual')
# Case = Cases(13,Arena,'manual')
# Case.arena  = ArenaMap(6,)
# Case.arenaR = ArenaMap(6,)
# Case.arena.Inflate(radius = 0.2) #0.1
# Case.arena.Panelize(size= 0.01) #0.08
# Case.arena.Calcula te_Coef_Matrix(method = 'Vortex')


# buildings = create_buildings()
# print(f"buildings are {buildings}")


# case1 = Cases()

# case1.add_case("d",1,1)

NUM_PROC = 2


if __name__ == "__main__":
    # case = Cases.get_case(
    #     filename="bug_fixing/performance_enhancement.json", case_name="8_drones_2_buildings"
    # )
    # case = Cases.get_case(filename="bug_fixing/performance_enhancement.json", case_name="8_drones")
    # case = Cases.get_case(filename="examples/cases.json", case_name="alpha1")
    n_drones   = 9
    case_number = 1
    case = Cases.get_case(filename=f"data/random{n_drones}.json", case_name=f"random{n_drones}_{case_number}")
    set_new_attribute(case, "source_strength", new_attribute_value=0.7)
    t0 = 0
 
    start_time = time()
    run_simulation(case, t=2000,update_every=1, stop_at_collision=False)
    time_taken = time() - start_time


    print(f"Time for simulation is {time_taken}")
    # print(f"vortex calc time is {vortex_calculation_time}")
    # print(case.vehicle_list[0].personal_vehicle_list[1].path.shape)
    asdf = ut.plot_trajectories2(case.arena, case.arena, case.vehicle_list)
    asdf.show()

# EOF
