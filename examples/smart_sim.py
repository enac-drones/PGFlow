# from gflow.arena import ArenaMap
# from gflow.building import Building
from src.vehicle import Vehicle
import src.utils.plot_utils as ut
from src.cases import Cases, Case
from time import sleep
import numpy as np
from src.arena import ArenaMap

from experimental.smart_input import create_buildings
from src.utils.simulation_utils import run_simulation


# from cases import Cases
# Case = Cases(117,Arena,'manual')
# Case = Cases(13,Arena,'manual')
# Case.arena  = ArenaMap(6,)
# Case.arenaR = ArenaMap(6,)
# Case.arena.Inflate(radius = 0.2) #0.1
# Case.arena.Panelize(size= 0.01) #0.08
# Case.arena.Calculate_Coef_Matrix(method = 'Vortex')


buildings = create_buildings()
print(f"buildings are {buildings}")
# case = Case("smart_case")


# case1 = Cases()

# case1.add_case("d",1,1)

file_name = "bug_fixing/cases.json"
generator = Cases(filename=file_name)
case = generator.get_case(filename=file_name, case_name="twodrones")
# case = Cases.get_case(filename="data/random8.json", case_name="random8_13")

case.buildings = buildings
case.arena = ArenaMap(buildings)
case.name = "bug1"

generator.add_case(case)

simulation_success = run_simulation(
    case, t=500, update_every=1, stop_at_collision=False
)


asdf = ut.plot_trajectories2(case.arena, case.arena, case.vehicle_list)
asdf.show()

# EOF
