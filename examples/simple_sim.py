import gflow.utils.plot_utils as ut
from gflow.cases import Cases
from time import time
from gflow.utils.simulation_utils import run_simulation, set_new_attribute
# from pprint import pprint

# from gflow.utils.better_plot import BetterPlot
if __name__ == "__main__":
    file_name = "examples/large_case_working.json"
    case_name="large_case"
    # case = Cases.get_case(filename="bug_fixing/cases.json", case_name="ignore_arrived")
    case = Cases.get_case(file_name=file_name, case_name=case_name)
    case = Cases.get_case(file_name="examples/cases.json", case_name="default")

    # case = Cases.get_case(filename="bug_fixing/cases.json", case_name="close_to_sink")
    set_new_attribute(case, "source_strength", new_attribute_value=10)
    set_new_attribute(case, "imag_source_strength", new_attribute_value=20)
    set_new_attribute(case, "sink_strength", new_attribute_value=5)
    set_new_attribute(case, "max_speed", new_attribute_value=1)
    set_new_attribute(case, "delta_t", new_attribute_value=1 / 50)
    set_new_attribute(case, "turn_radius", new_attribute_value=0.5)
    # set_new_attribute(case, "v_free_stream", new_attribute_value=0.02)



    # set_new_attribute(case, "transmitting", new_attribute_value=True)


    delta_t = case.vehicle_list[0].delta_t
    update_frequency = 50  # Hz
    update_time_period = max(int(1 / (update_frequency * delta_t)), 1)

    ######################################
    # this variable controls how many time steps occur between every communication of position
    update_time_period = 1
    ######################################

    print(f"update every = {update_time_period}")

    case.max_avoidance_distance = 10
    case.building_detection_threshold = 3
    case.mode = 'radius'

    start_time = time()
    result = run_simulation(
        case,
        t=3,
        update_every=update_time_period,
        stop_at_collision=False
        )

    case.to_dict(file_path="example_output.json")
    # print(case.vehicle_list[0].path)
    time_taken = time() - start_time
    print(f"Simulation was safe: {result}")

    print(f"Time for simulation is {time_taken}")

    trajectory_plot = ut.PlotTrajectories(case, update_every=update_time_period)
    # trajectory_plot.BUILDING_EDGE_COLOUR
    LIMS = (-10,10)
    trajectory_plot.ax.set_xlim(LIMS)
    trajectory_plot.ax.set_ylim(LIMS)
    trajectory_plot.show()
    
    # better_plot = BetterPlot(case)
    # better_plot.create_animation()
    # better_plot.show()
    # import matplotlib.pyplot as plt
    # import numpy as np
    # positions = case.vehicle_list[0].path
    # desired_positions = np.array(case.vehicle_list[0].desired_vectors)

    # # plt.plot(positions[:,0],positions[:,1])
    # print(desired_positions.shape)
    # plt.plot(desired_positions[:,0],desired_positions[:,1])
    # # plt.xlim(0,10)
    # # plt.ylim(-10,0)
    # plt.show()

# EOF
