# from gflow.arena import ArenaMap
# from gflow.building import Building
from src.vehicle import Vehicle
import src.utils.plot_utils as ut
from src.cases import Cases
from time import sleep, time
import numpy as np
from src.utils.simulation_utils import run_simulation

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
# case = Cases.get_case(filename="examples/cases.json", case_name="threedrones")
case = Cases.get_case(
    filename="bug_fixing/performance_enhancement.json", case_name="8_drones_1_building"
)
# case = Cases.get_case(filename="bug_fixing/performance_enhancement.json", case_name="8_drones")

t0 = 0

start_time = time()
run_simulation(case, update_every=1, stop_at_collision=False)
time_taken = time() - start_time
print(f"Time for simulation is {time_taken}")
# print(f"vortex calc time is {vortex_calculation_time}")
asdf = ut.plot_trajectories2(case.arena, case.arena, case.vehicle_list)
asdf.show()

# EOF
