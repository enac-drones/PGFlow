import json
import os
import shutil
import sys
from copy import deepcopy

from src.arena import ArenaMap
from src.building import Building, RegularPolygon
from src.vehicle import Vehicle, PersonalVehicle
from random import random
import numpy as np
from scipy.spatial import distance
import warnings
from typing import List
from src.utils.json_utils import dump_to_json, load_from_json


class Case:
    """Class to store a particular case, takes a name string as an input"""

    _name: str

    def __init__(self, name):
        # self._name = None
        # this line ensures the setter is called even when the class instance is created
        self.name = name
        self._vehicle_list: List[Vehicle] = []
        self.buildings: List[Building] = []
        self._arena = None
        self.collision_threshold = 0.5

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if new_name == "q" or new_name == "d":
            # q and d are used to quit or use the default case when the user requests an inexistent case name
            # they are protected (ie the system quits when q is called instead of running a case named 'q')
            raise ValueError(
                "'d' and 'q' are protected names, please choose a different name for your case."
            )
        self._name = new_name

    @property
    def vehicle_list(self) -> List[Vehicle]:
        return self._vehicle_list

    @vehicle_list.setter
    def vehicle_list(self, new_vehicle_list: List[Vehicle]):
        self._vehicle_list = deepcopy(new_vehicle_list)
        for vehicle in self._vehicle_list:
            # vehicle.personal_vehicle_list = deepcopy(new_vehicle_list)
            vehicle.personal_vehicle_list = [
                PersonalVehicle(*v.basic_properties()) for v in new_vehicle_list
            ]

    @property
    def arena(self):
        return self._arena

    @arena.setter
    def arena(self, new_arena):
        """Arena setter, need to add some error handling first probably, just like in the vehicle_list setter"""
        self._arena = deepcopy(new_arena)
        for vehicle in self._vehicle_list:
            vehicle.arena = deepcopy(new_arena)

    def colliding(self, get_culprits=False):
        squared_distance_threshold = self.collision_threshold**2
        active_vehicles = [v for v in self.vehicle_list if v.state == 0]
        for i in range(len(active_vehicles)):
            for j in range(i + 1, len(active_vehicles)):
                if (
                    self.calculate_squared_distance(
                        active_vehicles[i].position, active_vehicles[j].position
                    )
                    < squared_distance_threshold
                ):
                    if not get_culprits:
                        return True
                    else:
                        return (active_vehicles[i].ID, active_vehicles[j].ID)
        return False

    def calculate_squared_distance(self, position1, position2):
        x1, y1, z1 = position1
        x2, y2, z2 = position2
        return (x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2

    def clean_case(self):
        self.vehicle_list = []
        return None


class Cases:
    def __init__(self, filename="examples/cases.json") -> None:
        """initiate the class with the json filename and the case within that file"""
        self._filename: str = filename
        self.cases: dict = self._load_file(self._filename)
        # print(f"cases are {self.cases}")
        self._case_name: str = "default"
        self.case = None

    @property
    def case_name(self):
        return self._case_name

    @case_name.setter
    def case_name(self, new_name):
        """Ensure the user sets a correct case"""
        # print(self.cases.keys())
        if new_name in self.cases.keys():
            self._case_name = new_name
        else:
            self.select_case(new_name=new_name)

    def select_case(self, new_name):
        """Allow the user to select a case manually. This function is called if the case requested does not exist"""
        print(
            f"Error: '{new_name}' is an invalid case name. Valid cases are: {list(self.cases.keys())}"
        )
        while True:
            user_input = input(
                "Please input desired case, or type 'd' to use 'default' case or 'q' to quit: "
            )
            if user_input == "q":
                sys.exit("Quitting simulation, please specify desired case")
            elif user_input == "d":
                break
            elif user_input in self.cases.keys():
                self._case_name = user_input
                break
            else:
                print("Invalid input")

        print(f"Using '{self._case_name}' case instead")

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, new_name):
        """Set new filename and reset the cases object"""
        try:
            self._filename = new_name
            self.cases = self._load_file(new_name)
        except FileNotFoundError as ex:
            # User gives invalid filepath
            print(ex, type(ex).__name__, ex.args)
            print(
                f"File {new_name} contains a directory that does not exist. Please try again or create the directory."
            )

    @classmethod
    def get_case(cls, filename, case_name):
        case_cls = cls(filename=filename)
        case_cls.case_setup(case_name)
        return case_cls.case

    def case_setup(self, case_name):
        self.case_name = case_name
        self.case = Case(self.case_name)
        self.case.vehicle_list = self.obtain_vehicles()
        self.case.buildings = self.obtain_buildings()
        self.case.arena = ArenaMap(buildings=self.case.buildings)

    def _load_file(self, filename) -> dict:
        """Return a dictionary of all the cases inside filename."""
        # self.filename = filename
        self.cases = {}  # Initializing self.cases to be an empty dictionary

        if not os.path.exists(filename):
            # The file does not exist, create it.
            with open(filename, "w") as f:
                pass  # No need to write anything, just create the file.

        if self._is_file_empty():
            self.load_default_case()
        else:
            try:
                self._load_cases_from_file()
            except json.JSONDecodeError as ex:
                self._handle_invalid_json(ex)

        self._ensure_default_case_exists()
        return self.cases

    def _is_file_empty(self) -> bool:
        """Check if file is empty."""
        return os.stat(self.filename).st_size == 0

    def _load_cases_from_file(self):
        """Load cases from file."""
        self.cases = load_from_json(self.filename)
        # with open(self.filename, "r") as f:
        #     self.cases = json.load(f)

    def _handle_invalid_json(self, ex):
        """Handle invalid JSON error."""
        print(type(ex).__name__, ex.args)
        self._backup_and_clear_file()
        self.load_default_case()

    def _backup_and_clear_file(self):
        """Backup the file and clear the contents."""
        self._backup_file()
        self._clear_file_contents()

    def _backup_file(self):
        """Create a backup of the file."""
        dir_path = os.path.dirname(self.filename)
        file_name, file_ext = os.path.splitext(os.path.basename(self.filename))
        backup_filename = os.path.join(dir_path, f"{file_name}BACKUP.json")
        shutil.copyfile(self.filename, backup_filename)

    def _clear_file_contents(self):
        """Clear the contents of the file."""
        open(self.filename, "w").close()

    def _ensure_default_case_exists(self):
        """Ensure that a default case exists."""
        if "default" not in self.cases.keys():
            self.load_default_case()

    def load_default_case(self):
        sides = 5
        position = (0, 0)
        rotation = 0
        radius = 0.5

        obstacle = RegularPolygon(
            sides=sides, centre=position, rotation=rotation, radius=radius
        )
        building = Building(obstacle.points())
        Vehicle1 = Vehicle(ID="V1", source_strength=0.5, imag_source_strength=0.5)
        Vehicle1.Set_Goal(goal=[3, 0, 0.5], goal_strength=5, safety=0.0001)
        Vehicle1.Set_Position(pos=[-3, 0.0001, 0.5])
        buildings, vehicles = [], []
        buildings.append(building)
        vehicles.append(Vehicle1)
        # print(f"the vehicle list should be {vehicles[0],len(vehicles)}")
        case = Case(name="default")
        case.vehicle_list = vehicles
        case.buildings = buildings
        # add the case to the self.cases dict
        self.add_case(case)
        # dump self.cases to the json data file
        self.update_json()
        return None

    def obtain_buildings(self):
        """return a list of building objects"""
        buildings = []
        for building in self.cases[self.case_name]["buildings"]:
            coords = building["vertices"]
            # print(f'{coords = }',type(coords))
            buildings.append(Building(coords))
        return buildings

    def obtain_vehicles(self):
        """return a list of vehicle objects"""
        vehicles = []
        for vehicle in self.cases[self.case_name]["vehicles"]:
            # print(f"vehicle is {vehicle}")
            position = vehicle["position"]
            goal = vehicle["goal"]
            ID = vehicle["ID"]
            source_strength = vehicle["source_strength"]
            imag_source_strength = vehicle["imag_source_strength"]
            sink_strength = vehicle["sink_strength"]
            safety = vehicle["safety"]
            myVehicle = Vehicle(
                ID=ID,
                source_strength=source_strength,
                imag_source_strength=imag_source_strength,
            )
            myVehicle.Set_Position(position)
            myVehicle.Set_Goal(goal=goal, goal_strength=sink_strength, safety=safety)
            myVehicle.Go_to_Goal(
                altitude=0.5, AoAsgn=0, t_start=0, Vinfmag=0
            )  # FIXME add these to the json
            vehicles.append(myVehicle)
        return vehicles

    def add_case(self, case: Case):
        """Add a case into self.cases dictionary"""
        case_name = case.name
        building_list = case.buildings
        vehicle_list = case.vehicle_list

        # create sub dictionary within cases to hold the case
        self.cases[case_name] = {}

        # now set some info about the case. Need to create a list of buildings first though
        self.cases[case_name]["buildings"] = [
            {
                "ID": f"Building {count}",
                "vertices": building.vertices.tolist(),
            }
            for count, building in enumerate(building_list)
        ]

        # now the vehicles
        self.cases[case_name]["vehicles"] = [
            {
                "ID": vehicle.ID,
                "position": vehicle.position.tolist(),
                "goal": vehicle.goal.tolist(),
                "source_strength": vehicle.source_strength,
                "imag_source_strength": vehicle.imag_source_strength,
                "sink_strength": vehicle.sink_strength,
                "safety": vehicle.safety,
            }
            for vehicle in vehicle_list
        ]

        # dump_to_json(self.filename, self.cases)

        # return the case that was just added
        self.case_name = case_name
        # json_case holds the case in the format that it will be written as in the json file
        json_case = self.cases[case_name]
        return json_case

    def update_json(self):
        dump_to_json(self.filename, self.cases)

    def remove_case(self, case_name):
        """Remove a particular case from the cases file, return that case"""
        deleted_case = self.cases.pop(
            case_name
        )  # this returns the value of the removed key
        # with open(self._filename, "w") as f:
        #     json.dump(self.cases, f, sort_keys=False, indent=4)

        dump_to_json(self._filename, self.cases)
        return deleted_case

    def generate_random_case(self, case_name, n_drones):
        """create a case with n_drones with random starting and ending coords"""
        vehicle_list = []
        starting_positions, goal_positions = self.generate_coordinates(
            n_drones=n_drones, side_length=8, min_distance=0.5
        )
        for idx, coord in enumerate(starting_positions):
            vehicle = Vehicle(
                ID=f"V{idx}", source_strength=0.5, imag_source_strength=0.5
            )
            vehicle.Set_Position(pos=coord)
            vehicle.Set_Goal(goal=goal_positions[idx], goal_strength=5, safety=0.0001)
            vehicle_list.append(vehicle)
        case = Case(name=case_name)
        case.vehicle_list = vehicle_list
        return case

    def generate_coordinates(self, n_drones, side_length, min_distance):
        """
        Generate random starting and ending positions for n_drones within a square area.

        Parameters:
        n_drones (int): The number of drones.
        side_length (float): The side length of the square area.
        min_distance (float): The minimum allowed distance between any two drones.

        Returns:
        starting_positions (list): List of starting positions for each drone.
        ending_positions (list): List of ending positions for each drone.

        The function works by generating a random position within the square, then checking if it's
        far enough away from all existing positions. If it's too close to any existing position, it's discarded
        and a new position is generated. This continues until all drones have been placed or the maximum number
        of iterations has been reached.

        Note:
        - The positions are completely random within the square, subject to the minimum distance constraint.
        - If the number of drones, the side length, and the minimum distance are not compatible (i.e., if the drone
        density is too high or the minimum distance is too large relative to the side length), the function may
        not be able to place all the drones and will stop after a certain number of iterations, issuing a warning.
        - Drones are more likely to be evenly spaced if the number of drones is small relative to the square of the
        side length divided by the square of the minimum distance.
        """

        max_iterations = 10000  # Define a limit on the number of iterations
        iteration = 0
        starting_positions = []
        ending_positions = []

        density = n_drones * (np.pi * (min_distance / 2) ** 2) / (side_length**2)
        if density > 0.8:
            warnings.warn(
                f"Drone density ({density}) or minimum distance might be too high for the side length. Adjust the parameters."
            )

        while len(starting_positions) < n_drones and iteration < max_iterations:
            new_start = (
                np.random.uniform(0, side_length, 3) - side_length / 2
            )  # Generate a new start 3D point
            new_end = (
                np.random.uniform(0, side_length, 3) - side_length / 2
            )  # Generate a new end 3D point
            # temporarily set the z coordinate to 0.5 to match the 2d case
            new_start[2] = new_end[2] = 0.5
            if starting_positions:
                dists = distance.cdist([new_start], starting_positions, "euclidean")[0]
                if np.min(dists) < min_distance:
                    iteration += 1
                    continue  # Skip this point, it's too close

            if ending_positions:
                dists = distance.cdist([new_end], ending_positions, "euclidean")[0]
                if np.min(dists) < min_distance:
                    iteration += 1
                    continue  # Skip this point, it's too close

            # If the point passed all checks, add it to both starting and ending positions
            starting_positions.append(new_start)
            ending_positions.append(new_end)

        if iteration == max_iterations:
            warnings.warn(
                f"Maximum iteration reached. Returning available positions."
                f"There are {len(starting_positions)} available drones"
            )

        return starting_positions, ending_positions


# if __name__ == "__main__":
#     sides = 7
#     position = (0, 0)
#     orientation = 0
#     radius = 1

#     obstacle = RegularPolygon(
#         sides=sides, centre=position, rotation=orientation, radius=radius
#     )
#     building = Building(obstacle.points())
#     Vehicle1 = Vehicle(ID="V1", source_strength=0.5, imag_source_strength=0.5)
#     Vehicle1.Set_Goal(goal=[3, 0, 0.5], goal_strength=5, safety=0.0001)
#     Vehicle1.Set_Position(pos=[-3, 0.0001, 0.5])
#     Vehicle2 = Vehicle(ID="V2", source_strength=0.5, imag_source_strength=0.5)
#     Vehicle2.Set_Goal(goal=[-3, 0, 0.5], goal_strength=5, safety=0.0001)
#     Vehicle2.Set_Position(pos=[3, 0.0001, 0.5])
#     Vehicle3 = Vehicle(ID="V3", source_strength=0.5, imag_source_strength=0.5)
#     Vehicle3.Set_Goal(goal=[0, -3, 0.5], goal_strength=5, safety=0.0001)
#     Vehicle3.Set_Position(pos=[0, 3, 0.5])

#     generator = Cases()
#     # print(f"Now changing the filename")
#     generator.filename = "examples/cases.json"
#     buildings = []
#     vehicles = []
#     # buildings.append(building)
#     vehicles.append(Vehicle1)
#     vehicles.append(Vehicle2)
#     vehicles.append(Vehicle3)

#     case = Case(name="default")
#     case.vehicle_list = vehicles
#     case.buildings = buildings

#     generator.add_case(case)
# case.add_case(ID="test2",building_list=buildings,vehicle_list=vehicles)
# print(case.cases)
