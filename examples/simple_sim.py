import PGFlow.utils.plot_utils as ut
from PGFlow.cases import Cases
from time import time
from PGFlow.utils.simulation_utils import run_simulation, set_new_attribute

if __name__ == "__main__":
    file_name = "examples/scenebuilder.json"
    case_name="default"

    # file_name = "examples/gui_testing.json"
    # case_name="voliere"

    case = Cases.get_case(filename=file_name, case_name=case_name)

    set_new_attribute(case, "source_strength", new_attribute_value=1)
    set_new_attribute(case, "sink_strength", new_attribute_value=5)
    # set_new_attribute(case, "max_speed", new_attribute_value=1)
    set_new_attribute(case, "delta_t", new_attribute_value=1 / 50)
    set_new_attribute(case, "turn_radius", new_attribute_value=0.1)
    # set_new_attribute(case, "transmitting", new_attribute_value=True)


    delta_t = case.vehicle_list[0].delta_t
    update_frequency = 50  # Hz
    update_time_period = max(int(1 / (update_frequency * delta_t)), 1)

    ######################################
    # this variable controls how many time steps occur between every communication of position
    # update_time_period = 10
    ######################################

    print(f"update every = {update_time_period}")

    case.max_avoidance_distance = 3

    start_time = time()
    result = run_simulation(
        case,
        t=2000,
        update_every=update_time_period,
        stop_at_collision=False,
        max_avoidance_distance=case.max_avoidance_distance,
    )

    time_taken = time() - start_time
    print(f"Simulation was safe: {result}")

    print(f"Time for simulation is {time_taken}")

    trajectory_plot = ut.PlotTrajectories(case, update_every=update_time_period)

    trajectory_plot.show()

# EOF