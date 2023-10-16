import numpy as np
from numpy.typing import ArrayLike
from src.cases import Case, Cases
from src.building import Building
from src.vehicle import Vehicle
from gui.entities import Drone, Obstacle
from src.utils.simulation_utils import run_simulation
from src.utils.plot_utils import PlotTrajectories


def distance_between_points(p1: ArrayLike, p2: ArrayLike) -> float:
    """
    Returns the distance between two points.
    """
    p1, p2 = np.array(p1), np.array(p2)
    return np.linalg.norm(p1 - p2)


def generate_case(name: str, buildings: list[Obstacle], drones: list[Drone]) -> Case:
    height = 1.2
    # this line adds a third dimension to the x,y coordinates of the building patches and creates a building object from each patch
    buildings = [
        Building(
            np.hstack(
                [
                    building.vertices,
                    np.full((building.vertices.shape[0], 1), height),
                ]
            )
        )
        for building in buildings
    ]

    # buildings = [Building(patch.get_xy()) for patch in self.building_patches]
    c = Case(name=name)
    c.buildings = buildings
    c.vehicle_list = []
    c.vehicle_list = [
        Vehicle(ID=v.ID, source_strength=1, imag_source_strength=0.5) for v in drones
    ]
    for idx, d in enumerate(drones):
        c.vehicle_list[idx].Set_Position(d.position)
        c.vehicle_list[idx].Set_Goal(goal=d.goal, goal_strength=5, safety=None)
        c.vehicle_list[idx].Go_to_Goal(
            altitude=0.5, AoAsgn=0, t_start=0, Vinfmag=0
        )  # FIXME add these to the json
    generator = Cases(filename="examples/gui_testing.json")
    generator.add_case(c)
    generator.update_json()

    complete_case = generator.get_case("examples/gui_testing.json", "Test Case")
    return complete_case


def run_case(case: Case):
    update_every = 500
    result = run_simulation(
        case,
        t=2000,
        update_every=update_every,
        stop_at_collision=False,
        max_avoidance_distance=20,
    )
    asdf = PlotTrajectories(case, update_every=update_every)
    # asdf = plt_utils.plot_trajectories(my_case) # Old plot

    asdf.show()
    return result
