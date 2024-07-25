from pgflow import Cases
from pgflow import run_simulation, set_new_attribute
from pgflow import PlotTrajectories 
from pgflow import SimulationVisualizer
import numpy as np

file_name = 'examples/voliere.json'
case_name ="scenebuilder"

# from pgflow import ArenaMap
# ArenaMap.inflation_radius=0.0
# ArenaMap.size = 0.1

case = Cases.get_case(file_name, case_name)

set_new_attribute(case, "imag_source_strength", new_attribute_value=10)
set_new_attribute(case, "sink_strength", new_attribute_value=5)
set_new_attribute(case, "max_speed", new_attribute_value=0.5)
set_new_attribute(case, "source_strength", new_attribute_value=1)
set_new_attribute(case,"v_free_stream_mag", new_attribute_value=0.5)
set_new_attribute(case,"ARRIVAL_DISTANCE", new_attribute_value=0.2)
set_new_attribute(case, "turn_radius", new_attribute_value=0.05)
# set_new_attribute(case, "goal", new_attribute_value=np.array([34.06, -8.23 ,2]))

case.max_avoidance_distance = 4
case.building_detection_threshold = 1.

case.mode = ''
result = run_simulation(
    case,
    t=3500,
    update_every=1,
    stop_at_collision=False
    )


# save simulation to output json file
file_name = 'example_output.json'
case.to_dict(file_path=file_name)

# Use the original visualiser
trajectory_plot = PlotTrajectories(file_name, collision_threshold=0.5, max_connection_distance=case.max_avoidance_distance, update_every=1)

# specify new axes plot limits if desired
LIMS = (-5,5)
trajectory_plot.ax.set_xlim(LIMS)
trajectory_plot.ax.set_ylim(LIMS)
# Show the trajectories
trajectory_plot.show()


# Use the alternative visualiser
visualizer = SimulationVisualizer(file_name)
visualizer.show_plot()
