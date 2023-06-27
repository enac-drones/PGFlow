# from gflow.arena import ArenaMap
# from gflow.building import Building

import os

from src.utils.plot_utils import plot_trajectories2
from src.cases import Cases, Case
from src.vehicle import Vehicle
from typing import List
import time
from src.utils.json_utils import dump_to_json
from src.utils.simulation_utils import run_simulation


def optional_plot(case: Case, plot_title="No title"):
    plot = plot_trajectories2(case.arena, case.arena, case.vehicle_list)
    plot.slider.set_val(1.0)
    plot.ax.set_title(plot_title)
    plot.show()



def new_random_cases(n_cases, n_drones):
    """
    Generate a specified number of new random cases with a certain number of drones.
    The generated cases are stored in a json file inside data/.

    Args:
    n_cases (int): The number of cases to be generated.
    n_drones (int): The number of drones to be used in each case.

    """
    base_case_name = f"random{n_drones}"
    file_name = f"data/{base_case_name}.json"
    cases = {}
    generator = Cases(filename=file_name)
    for idx in range(n_cases):
        case_name = f"{base_case_name}_{idx}"
        # generate a random case and add it to the json file as defined by file_name
        case = generator.generate_random_case(case_name=case_name, n_drones=n_drones)
        cases[case_name] = case
        # add case to json file
        generator.add_case(case)
    generator.update_json()
    return cases


def set_new_attribute(case: Case, attribute_name: str, new_attribute_value):
    """change attributes such as sink strength for every vehicle in a case"""
    if not hasattr(Vehicle(ID="hi"), attribute_name):
        print(f"Attribute {attribute_name} does not exist in the Vehicle class.")
        return None
    v_list = case.vehicle_list
    for vehicle in v_list:
        # vehicle.sink_strength = 5*4/3
        vehicle.source_strength = new_attribute_value
    case.vehicle_list = v_list

    return True


def run_specific_case(file_name, case_name, update_frequency):
    case = Cases.get_case(filename=file_name, case_name=case_name)
    # optional:
    # set_new_attribute(case, "source_strength", new_attribute_value=1)

    simulation_succeeded = run_simulation(
        case=case, t=500, update_every=update_frequency, stop_at_collision=True
    )
    optional_plot(case)
    return simulation_succeeded


def simulate_cases(file_name, case_name, n_cases, update_frequency):
    """
    Simulate a number of cases for a given update frequency and count the total number of failures.

    Args:
    case_name (str): The base name of the cases to be simulated.
    n_cases (int): The number of cases to simulate.
    update_frequency (int): The frequency of updates to be used in the simulation.

    Returns:
    int: The total number of simulation failures.
    """
    total_failures = 0
    t = time.time()
    for idx in range(n_cases):
        if idx % 20 == 0:
            print(
                f"running case {idx} at frequency {update_frequency}, time taken = {time.time()-t}"
            )
            t = time.time()
        case = Cases.get_case(filename=file_name, case_name=f"{case_name}_{idx}")

        set_new_attribute(case, "source_strength", new_attribute_value=0.5)

        simulation_succeeded = run_simulation(
            case=case, t=500, update_every=update_frequency
        )

        if not simulation_succeeded:
            total_failures += 1
    return total_failures


def collect_and_store_data(
    file_name: str, n_drones: int, n_cases: int, update_frequency_list: list
):
    """
    For a given drone number and update frequency list, simulate a number of cases, collect the failure data,
    and store it to a json file.

    Args:
    n_drones (int): The number of drones.
    n_cases (int): The number of cases to simulate.
    update_frequency_list (list): A list of update frequencies to be used in the simulation.

    """
    base_case_name = f"random{n_drones}"
    # file_name = f"data/{base_case_name}.json"

    # run_specific_case(
    #     file_name=file_name, case_name=f"{base_case_name}_3", update_frequency=1
    # )

    corresponding_failures = {}
    for num in update_frequency_list:
        print(f"Now simulating with frequency of every {num} seconds")
        total_failures = simulate_cases(file_name, base_case_name, n_cases, num)
        corresponding_failures[num] = total_failures
        print(total_failures, f"case {num}")

    print(corresponding_failures)
    dump_to_json(f"results/{base_case_name}.json", corresponding_failures)
    return None


def main():
    """
    The main function that defines input values and triggers the data collection and storage process.
    """
    n_drones = 3
    n_cases = 100
    update_frequency_list = [1, 2, 3, 4, 5, 10, 50, 100, 200, 300, 400, 500]

    base_case_name = f"random{n_drones}"
    file_name = f"data/{base_case_name}.json"

    # random_cases = new_random_cases(n_cases, n_drones)
    # dump_to_json(file_name,random_cases)
    collect_and_store_data(file_name, n_drones, n_cases, update_frequency_list)


if __name__ == "__main__":
    main()


# if __name__ == "__main__":
#     collect_data()
# EOF
# 3 drones:
# 1:38, 2: 41, 3:57/50, 4:49, 5:50,10:63,50:113, 100:145, 200: 202, 300:207, 400:231, 500:248

# %%
