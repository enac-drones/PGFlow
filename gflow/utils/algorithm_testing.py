import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from scenebuilder.gui_sim import InteractivePlot
from gflow.cases import Cases, Case
from gflow.utils.simulation_utils import set_new_attribute
from numpy.typing import ArrayLike
from gflow.arena import ArenaMap


def plot_buildings(ax, buildings):
    """Plots buildings as semi-transparent polygons.

    Args:
        ax: Matplotlib axis object.
        buildings: List of tuples, where each tuple contains the vertices of a building.
    """
    for building in buildings:
        polygon = patches.Polygon(building, closed=True, color='grey', alpha=0.5)
        ax.add_patch(polygon)

def plot_drones(ax, drones):
    """Plots drones as points on the plot.

    Args:
        ax: Matplotlib axis object.
        drones: List of tuples, where each tuple contains the (x, y) position of a drone.
    """
    for idx, drone in enumerate(drones):
        style = 'ro' if idx == 0 else 'bo'
        ax.plot(*drone, style)  # 'bo' for blue circle marker

def calculate_field_vectors(coords:ArrayLike, case:Case)->ArrayLike:
    # print(f"{coords=}")
    vehicle = case.vehicle_list[0]
    uv = np.zeros_like(coords)
    for idx,coord in enumerate(coords):
        vehicle.position = np.hstack((coord,np.array([0])))
        # print(vehicle.position)
        vehicle.update_nearby_buildings(threshold = case.building_detection_threshold)
        vehicle.update_personal_vehicle_dict(case.vehicle_list,case.max_avoidance_distance)
        # print(vehicle.relevant_obstacles)
        flow_vels = vehicle.panel_flow.Flow_Velocity_Calculation(vehicle)
        uv[idx] = flow_vels
    return uv



def create_quiver_plot(case, buildings, drones, xlim, ylim):
    """Creates a 2D quiver plot visualizing the drone path planning.

    Args:
        buildings: List of tuples for building vertices.
        drones: List of tuples for drone positions.
        xlim: Tuple for x-axis limits.
        ylim: Tuple for y-axis limits.
    """
    fig, ax = plt.subplots(figsize = (8,8))
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    plot_buildings(ax, buildings)
    plot_drones(ax, drones)

    # Generate a meshgrid for the quiver plot
    x, y = np.meshgrid(np.linspace(*xlim, 60), np.linspace(*ylim, 60))
    
    # Assume a function to calculate vectors; you'll replace this with your actual function
    # u, v = calculate_field_vectors(x, y, drones)
    # Stack the x and y arrays depth-wise and reshape to a two-column array
    coords = np.dstack((x, y)).reshape(-1, 2)
    uv = calculate_field_vectors(coords,case)
    u = uv[:, 0].reshape(x.shape)
    v = uv[:, 1].reshape(y.shape)   
    # u,v = np.full((2,), 1)

    # Quiver plot
    ax.quiver(x, y, u, v)
    plt.streamplot(x, y, u, v, color='b', density=1)

    LIMS = (-5,5)

    # ax.set_xlim(LIMS)
    # ax.set_ylim(LIMS)
    ax.set_aspect('equal')


if __name__ == '__main__':
    #scenebuilder part
    # p = InteractivePlot()
    # p.draw_scene() 

    #gflow part
    #%%
    ArenaMap.inflation_radius = 0.5
    ArenaMap.size = 0.2
    file_name = "examples/cases.json"
    case_name="voliere4"
    case = Cases.get_case(file_name, case_name)
    # set_new_attribute(case, "ARRIVAL_DISTANCE", new_attribute_value=1e-6)
    set_new_attribute(case, "sink_strength", new_attribute_value=1)
    set_new_attribute(case, "max_speed", new_attribute_value=1)
    set_new_attribute(case, "imag_source_strength", new_attribute_value=5)
    set_new_attribute(case, "source_strength", new_attribute_value=2)
    # set_new_attribute(case, "mode", new_attribute_value="radius")
    set_new_attribute(case,"v_free_stream_mag", new_attribute_value=0.5)
    set_new_attribute(case, "turn_radius", new_attribute_value=0.01)
    case.max_avoidance_distance = 10
    case.building_detection_threshold = 10
    # Example usage
    # case.vehicle_list[0], case.vehicle_list[2] = case.vehicle_list[2], case.vehicle_list[0]
    # buildings = case.buildings
    buildings = [building.vertices[...,:2] for building in case.buildings]  # Define buildings as tuples of vertices
    drones = [vehicle.position[:2] for vehicle in case.vehicle_list]  # Drone positions
    create_quiver_plot(case, buildings, drones, xlim=(-5, 5), ylim=(-5, 5))
    plt.show()