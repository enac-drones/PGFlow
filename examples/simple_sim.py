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
# p rint(f"buildings are {buildings}")


# case1 = Cases()

# case1.add_case("d",1,1)

# NUM_PROC = 2


if __name__ == "__main__":
    # case = Cases.get_case(filename="bug_fixing/performance_enhancement.json", case_name="8_drones_2_buildings")
    # case = Cases.get_case(filename="bug_fixing/cases.json", case_name="ignore_arrived")
    case = Cases.get_case(filename="examples/cases.json", case_name="twodrones")
    # case = Cases.get_case(filename="bug_fixing/cases.json", case_name="close_to_sink")

    n_drones = 10
    case_number = 26
    # case = Cases.get_case(
    #     filename=f"data/random{n_drones}.json",
    #     case_name=f"random{n_drones}_{case_number}",
    # )
    set_new_attribute(case, "source_strength", new_attribute_value=1)
    set_new_attribute(case, "sink_strength", new_attribute_value=5)
    set_new_attribute(case, "max_speed", new_attribute_value=0.5)
    set_new_attribute(case, "delta_t", new_attribute_value=1 / 40)

    # set_new_attribute(case, "transmitting", new_attribute_value=True)

    print(case.name, [vehicle.transmitting for vehicle in case.vehicle_list])

    t0 = 0

    delta_t = case.vehicle_list[0].delta_t
    update_frequency = 0.1  # Hz
    update_time_period = max(int(1 / (update_frequency * delta_t)), 1)
    update_time_period = 1
    print(f"update every = {update_time_period}")

    v = 1.0

    start_time = time()
    result = run_simulation(
        case,
        t=2000,
        update_every=update_time_period,
        stop_at_collision=False,
        max_avoidance_distance=20,
    )
    time_taken = time() - start_time
    print(f"Simulation was safe: {result}")

    print(f"Time for simulation is {time_taken}")
    # print(f"vortex calc time is {vortex_calculation_time}")
    # print(case.vehicle_list[0].personal_vehicle_list[1].path.shape)
    asdf = ut.plot_trajectories2(case, update_every=update_time_period)
    # print([v.path[:,:2].shape for v in case.vehicle_list])
    path1 = np.array(case.vehicle_list[0].path[:, :2])
    path2 = np.array(case.vehicle_list[1].path[:, :2])
    np.save("/Users/adriandelser/Desktop/ENAC/DASC/plot_stuff/IdealPath1.npy", path1)
    np.save("/Users/adriandelser/Desktop/ENAC/DASC/plot_stuff/IdealPath2.npy", path2)
    # asdf.add_line(path1, color="red")
    # asdf.add_line(path2, color="blue")
    # asdf = ut.plot_trajectories2(case.arena, case.arena, case.vehicle_list)
    asdf.show()

# EOF
