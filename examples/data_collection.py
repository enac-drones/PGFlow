# from gflow.arena import ArenaMap
# from gflow.building import Building

import os

from src.utils.plot_utils import plot_trajectories2
from src.cases import Cases, Case
from src.vehicle import Vehicle
from typing import List
import time
from src.utils.json_utils import dump_to_json,load_from_json
from src.utils.simulation_utils import run_simulation
from multiprocessing import Process
import numpy as np

def optional_plot(case: Case, plot_title="No title"):
    plot = plot_trajectories2(case.arena, case.arena, case.vehicle_list)
    plot.slider.set_val(1.0)
    plot.ax.set_title(plot_title)
    plot.show()


# def new_random_cases(n_cases, n_drones):
#     """
#     Generate a specified number of new random cases with a certain number of drones.
#     The generated cases are stored in a json file inside data/.

#     Args:
#     n_cases (int): The number of cases to be generated.
#     n_drones (int): The number of drones to be used in each case.

#     """
#     base_case_name = f"random{n_drones}"
#     file_name = f"data/{base_case_name}.json"
#     cases = {}
#     for idx in range(n_cases):
#         generator = Cases(filename=file_name)
#         case_name = f"{base_case_name}_{idx}"
#         # generate a random case and add it to the json file as defined by file_name
#         case = generator.generate_random_case(case_name=case_name, n_drones=n_drones)
#         cases[case_name] = case
#         # add case to json file
#         generator.add_case(case)
#     return cases

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


# def run_specific_case(file_name, case_name, update_frequency):
#     case = Cases.get_case(filename=file_name, case_name=case_name)
#     # optional:
#     # set_new_attribute(case, "source_strength", new_attribute_value=1)

#     simulation_succeeded = run_simulation(
#         case=case, t=500, update_every=update_frequency, stop_at_collision=True
#     )
#     optional_plot(case)
#     return simulation_succeeded


def simulate_cases(file_name, base_name,n_cases, update_frequency, n_cases_start = 0):
    """
    Simulate a number of cases for a given update frequency and count the total number of failures.

    Args:
    base_name (str): The base name of the cases to be simulated.
    n_cases (int): The number of cases to simulate.
    update_frequency (int): The frequency of updates to be used in the simulation.
    n_start (int<n_cases) where does the case count start

    Returns:
    int: The total number of simulation failures.
    """
    total_failures = 0
    t = time.time()
    failure_indices = {}
    for idx in range(n_cases_start, n_cases):
        case_name = f"{base_name}_{idx}"
        if idx % 250 == 0:
            print(
                f"running case {idx} at frequency {update_frequency}, time taken = {time.time()-t}"
            )
            t = time.time()
        case = Cases.get_case(filename=file_name, case_name=f"{base_name}_{idx}")

        set_new_attribute(case, "source_strength", new_attribute_value=1)

        simulation_succeeded = run_simulation(
            case=case, t=2000, update_every=update_frequency,stop_at_collision=True)

        if not simulation_succeeded:
            total_failures += 1
            failure_indices[case_name] = idx
    # print(f"failures:{failure_indices}")
    return total_failures,failure_indices


# def collect_and_store_data(
#     file_name: str, n_drones: int, n_cases: int, update_frequency_list: list
# ):
#     """
#     For a given drone number and update frequency list, simulate a number of cases, collect the failure data,
#     and store it to a json file.

#     Args:
#     n_drones (int): The number of drones.
#     n_cases (int): The number of cases to simulate.
#     update_frequency_list (list): A list of update frequencies to be used in the simulation.

#     """
#     base_case_name = f"random{n_drones}"
#     # file_name = f"data/{base_case_name}.json"

#     # run_specific_case(
#     #     file_name=file_name, case_name=f"{base_case_name}_3", update_frequency=1
#     # )

#     corresponding_failures = {}
#     for num in update_frequency_list:
#         print(f"Now simulating with frequency of every {num} seconds")
#         total_failures = simulate_cases(file_name, base_case_name, n_cases, num)
#         corresponding_failures[num] = total_failures

#     print(corresponding_failures)
#     dump_to_json(f"results/{base_case_name}.json", corresponding_failures)
#     return None

def worker(file_name: str, n_drones: int, n_cases: int, update_frequency_sublist: list,worker_id: int):
    base_case_name = f"random{n_drones}"
    results = {}
    # corresponding_failures = {}

    for num in update_frequency_sublist:
        print(f"Now simulating with frequency of every {num} seconds")
        total_failures,failure_indices = simulate_cases(file_name, base_case_name, n_cases, num)
        results[num] = total_failures

    print(results)
    dump_to_json(f"results/temp_{worker_id}.json", results)
    dump_to_json(f"results/{base_case_name}/failures_{worker_id}.json", failure_indices)
    return None

def worker_multi_cases(file_name: str, n_drones: int, n_cases_start:int, n_cases: int, update_frequency_sublist: list,worker_id: int):
    '''Multi processing on the number of cases'''
    base_case_name = f"random{n_drones}"
    results = {}
    # corresponding_failures = {}

    for num in update_frequency_sublist:
        print(f"Now simulating with frequency of every {num} seconds")
        total_failures,failure_indices = simulate_cases(file_name, base_case_name, n_cases, num, n_cases_start)
        results[num] = total_failures

    print(results)
    dump_to_json(f"results/temp_{worker_id}.json", results)
    dump_to_json(f"results/{base_case_name}/failures_{n_cases_start}_{n_cases}.json", failure_indices)
    return None

def main_multi_frequencies():
    """
    The main function that defines input values and triggers the data collection and storage process.
    """
    # n_drones = 2
    n_drones_list = [2,3,4,5,6,7,8,9]
    # n_drones_list = [2]

    # n_drones_sublists = np.array_split(n_drones_list, 8)

    n_cases = 1000
    # random_cases = new_random_cases(n_cases, n_drones)
    # dump_to_json(file_name,random_cases)
    # update_frequency_list = [1, 2, 3, 4, 5, 10, 50, 100, 200, 300]
    # update_frequency_list = [400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000]
    update_frequency_list = [20,40,60,70,80,90]

    # Split update_frequency_list into 4 sublists
    update_frequency_sublists = np.array_split(update_frequency_list, 6)


    for n_drones in n_drones_list:
        base_case_name = f"random{n_drones}"
        file_name = f"data/{base_case_name}.json"
        # Create and start a process for each sublist
        processes = []
        for i, sublist in enumerate(update_frequency_sublists):
            p = Process(target=worker, args=(file_name, n_drones, n_cases, sublist.tolist(), i))
            p.start()
            processes.append(p)

        # Wait for all processes to finish
        for p in processes:
            p.join()
        
        # Combine the results from all workers into one dictionary
        combined_results = {}
        for i in range(len(processes)):
            results = load_from_json(f"results/temp_{i}.json")
            combined_results.update(results)
            os.remove(f"results/temp_{i}.json")  # delete the temporary file

        # dump_to_json(f"results/{base_case_name}.json", combined_results)
        print(n_drones, {int(key):value for key,value in combined_results.items()})

def main_multi_cases():
    """
    MultiProcess over the cases
    """
    # n_drones = 2
    # n_drones_list = [2,3,4,5,6,7,8,9]
    n_drones_list = [7,8,9]

    # n_drones_sublists = np.array_split(n_drones_list, 8)

    n_cases = 1000
    cases_per_worker = 100
    n_cases_sublist = list(range(0,n_cases,cases_per_worker))
    print(n_cases_sublist)
    # random_cases = new_random_cases(n_cases, n_drones)
    # dump_to_json(file_name,random_cases)
    # update_frequency_list = [1, 2, 3, 4, 5, 10, 50, 100, 200, 300, 500, 1000]
    # update_frequency_list = [1,3,5,50,300,500]
    update_frequency_list = [1]

    # Split update_frequency_list into 4 sublists
    # update_frequency_sublists = np.array_split(update_frequency_list, 1)


    for n_drones in n_drones_list:
        base_case_name = f"random{n_drones}"
        file_name = f"data/{base_case_name}.json"
        # Create and start a process for each sublist
        processes = []
        for i, n_start in enumerate(n_cases_sublist):
            p = Process(target=worker_multi_cases, args=(file_name, n_drones,n_start, n_start+cases_per_worker, update_frequency_list, i))
            p.start()
            processes.append(p)

        # Wait for all processes to finish
        for p in processes:
            p.join()
        
        # Combine the results from all workers into one dictionary
        combined_results = {}
        for n_cases_start in n_cases_sublist:
            results = load_from_json(f"results/{base_case_name}/failures_{n_cases_start}_{n_cases_start+cases_per_worker}.json")
            combined_results.update(results)
            os.remove(f"results/{base_case_name}/failures_{n_cases_start}_{n_cases_start+cases_per_worker}.json")  # delete the temporary file

        dump_to_json(f"results/{base_case_name}/failures_0_1000.json", combined_results)
        print(combined_results)
        # print(n_drones, {int(key):value for key,value in combined_results.items()})

def main_multi_drones():
    """
    Same as main but multiprocessing is done on the n_drones_list instead of frequency_list
    """
    # n_drones = 2
    n_drones_list = [2,3,4,5,6,7,8,9]
    # n_drones_sublists = np.array_split(n_drones_list, 8)

    n_cases = 100
    # random_cases = new_random_cases(n_cases, n_drones)
    # dump_to_json(file_name,random_cases)
    # update_frequency_list = [1, 2, 3, 4, 5, 10, 50, 100, 200, 300, 500, 1000]
    # update_frequency_list = [1,3,5,50,300,500]
    update_frequencies = [1]
    # Split update_frequency_ist into 4 sublists
    # update_frequency_sublists = np.array_split(update_frequency_list, 6)

        
    # Create and start a process for each sublist
    processes = []
    for idx, n_drones in enumerate(n_drones_list):
        base_case_name = f"random{n_drones}"
        file_name = f"data/{base_case_name}.json"
        p = Process(target=worker, args=(file_name, n_drones, n_cases, update_frequencies, n_drones))
        p.start()
        processes.append(p)

    # Wait for all processes to finish
    for p in processes:
        p.join()
    
    # Combine the results from all workers into one dictionary
    combined_results = {}
    for i in range(len(processes)):
        results = load_from_json(f"results/temp_{i}.json")
        combined_results.update(results)
        os.remove(f"results/temp_{i}.json")  # delete the temporary file

    # dump_to_json(f"results/{base_case_name}.json", combined_results)
    print({int(key):value for key,value in combined_results.items()})

    


if __name__ == "__main__":
    main_multi_frequencies()


# if __name__ == "__main__":
#     collect_data()
# EOF
# 3 drones:
# 1:38, 2: 41, 3:57/50, 4:49, 5:50,10:63,50:113, 100:145, 200: 202, 300:207, 400:231, 500:248

# %%
