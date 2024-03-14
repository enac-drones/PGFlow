from gflow.cases import Cases
from gflow.utils.simulation_utils import run_simulation, set_new_attribute
from gflow.utils.plot_utils import PlotTrajectories 
from gflow.plotting.main_plot import SimulationVisualizer
from scenebuilder.gui_sim import InteractivePlot
from gflow.arena import ArenaMap

#scenebuilder part
# p = InteractivePlot()
# p.draw_scene() 
ArenaMap.inflation_radius = 0.2

#gflow part
file_name = "voliere.json"
case_name="voliere6_1"
# file_name = "examples/cases.json"
# case_name="k"
case = Cases.get_case(file_name, case_name)
# set_new_attribute(case, "ARRIVAL_DISTANCE", new_attribute_value=1e-6)
set_new_attribute(case, "sink_strength", new_attribute_value=5)
set_new_attribute(case, "max_speed", new_attribute_value=0.5)
set_new_attribute(case, "imag_source_strength", new_attribute_value=1)
set_new_attribute(case, "source_strength", new_attribute_value=1)
set_new_attribute(case,"v_free_stream_mag", new_attribute_value=0.0)
set_new_attribute(case,"ARRIVAL_DISTANCE", new_attribute_value=0.25)


set_new_attribute(case, "turn_radius", new_attribute_value=0.05)
case.max_avoidance_distance = 5
case.building_detection_threshold = 10
# case.arrival_distance = 0.0000001


case.mode = 'fancy'
result = run_simulation(
    case,
    t=1500,
    update_every=1,
    stop_at_collision=False
    )

# create ouput json
case.to_dict(file_path="example_output.json")

trajectory_plot = PlotTrajectories(case, update_every=1)
# trajectory_plot.BUILDING_EDGE_COLOUR
LIMS = (-5,5)
# XLIMS = (575600,576000)
# YLIMS = (6275100,6275700)
trajectory_plot.ax.set_xlim(LIMS)
trajectory_plot.ax.set_ylim(LIMS)
trajectory_plot.show()

# visualisation part
# visualizer = SimulationVisualizer('example_output.json')
# visualizer.show_plot()