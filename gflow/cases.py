from gflow.building import Building, RegularPolygon
from gflow.arena import ArenaMap
from gflow.vehicle import Vehicle
from copy import copy, deepcopy
import shutil
import json
import os, sys

class Case():
    '''Class to store a particular case, takes a name string as an input'''
    def __init__(self, name):
        self.name = name
        self.vehicle_list = []
        self.buildings = []
        self._arena = None

    @property
    def arena(self):
        return self._arena
    
    @arena.setter
    def arena(self,new_arena):
        try:
            self._arena = new_arena
            for vehicle in self.vehicle_list:
                vehicle.vehicle_list = deepcopy(self.vehicle_list)
                vehicle.arena = deepcopy(self._arena)  # FIXME are these copies a problem ???
        except Exception as ex:
            print(ex,type(ex).__name__, ex.args)
            raise Exception
                
        # FIXME add arena generation here, remove it from cases setup...\


class Cases():
    def __init__(self,filename="examples/cases.json") -> None:
        '''initiate the class with the json filename and the case within that file'''
        self._filename = filename
        self.cases = self.load_file(self._filename)
        #print(f"cases are {self.cases}")
        self._casename = "default"
        self.case = None

    @property
    def casename(self):
        return self._casename
    
    @casename.setter
    def casename(self,new_name):
        """Ensure the user sets a correct case"""
        #print(self.cases.keys())
        if new_name in self.cases.keys():
            self._casename = new_name
        else:
            print(f"Error: '{new_name}' is an invalid case name. Valid cases are: {list(self.cases.keys())}")
            while True:
                user_input = input("Please input desired case, or type 'd' to use 'default' case or 'q' to quit: ")
                if user_input == "q":
                    sys.exit("Quitting simulation, please specify desired case")
                elif user_input == "d":
                    break
                elif user_input in self.cases.keys():
                    self._casename = user_input
                    break
                else:
                    print("Invalid input")

            print(f"Using '{self._casename}' case instead")

    @property
    def filename(self):
        return self._filename
    
    @filename.setter
    def filename(self,new_name):
        """Set new filename and reset the cases object"""
        try:
            self._filename = new_name
            self.cases = self.load_file(new_name)
        except FileNotFoundError as ex:
            #User gives invalid filepath
            print(ex,type(ex).__name__, ex.args)
            print(f"File {new_name} contains a directory that does not exist. Please try again or create the directory.")

    @classmethod
    def get_case(cls, filename, casename):
        case_cls = cls(filename=filename)
        case_cls.case_setup(casename)
        return case_cls.case


    def case_setup(self, casename):
        self.casename = casename
        self.case = Case(self.casename)
        self.case.vehicle_list =  self.obtain_vehicles()
        self.case.buildings = self.obtain_buildings()
        self.case.arena = ArenaMap(buildings=self.case.buildings)

        # for vehicle in self.case.vehicle_list:
        #     vehicle.vehicle_list = deepcopy(self.case.vehicle_list)
        #     vehicle.arena = deepcopy(self.case.arena)  # FIXME are these copies a problem ???

    def load_file(self,filename)->dict:
        '''return a dictionary of all the cases inside filename'''
        try:
            with open(filename,"a+") as f:
                check_file = os.stat(filename).st_size
                # print(f"check_file is {check_file}")
                # print(f"inside load_file, filename is {filename}")
                if check_file==0:
                    #the file is empty so it was just created
                    #load in a default case 
                    self.cases = {}
                    self.load_default_case()
                else:
                    #file already exists (is not empty), do nothing
                    pass
                #move the file pointer back to the start of the file otherwise json.load(f) doesn't work
                f.seek(0)
                cases = json.load(f)
            if "default" not in cases.keys():
                #make sure there is at least a default case to fall back on 
                self.cases = cases 
                self.load_default_case()
                return self.cases
            return cases
            
        except json.JSONDecodeError as ex:
            #improperly formatted json file will be wiped and replaced with a default case
            #a backup will be stored in the same directory as {name}BACKUP.json
            print(type(ex).__name__, ex.args)
            # Backup the file
            dir_path = os.path.dirname(filename)
            file_name, file_ext = os.path.splitext(os.path.basename(filename))
            new_file_path = os.path.join(dir_path, f"{file_name}BACKUP.json")
            shutil.copyfile(filename, new_file_path)
            #wipe and replace with the default case
            self.cases = {}
            self.load_default_case()
            #return an empty dictionary so that it matches the format of an empty file
            return self.cases
        
    def obtain_buildings(self):
        '''return a list of building objects'''
        buildings = []
        for building in self.cases[self.casename]["buildings"]:
            coords = building["vertices"]
            buildings.append(Building(coords))
        return buildings
        
    def obtain_vehicles(self):
        '''return a list of vehicle objects'''
        vehicles = []
        for vehicle in self.cases[self.casename]["vehicles"]:
            #print(f"vehicle is {vehicle}")
            position = vehicle["position"]
            goal = vehicle["goal"]
            ID = vehicle["ID"]
            source_strength = vehicle["source_strength"]
            imag_source_strength = vehicle["imag_source_strength"]
            sink_strength = vehicle["sink_strength"]
            safety = vehicle["safety"]
            myVehicle = Vehicle(ID=ID,source_strength=source_strength,imag_source_strength=imag_source_strength)
            myVehicle.Set_Position(position)
            myVehicle.Set_Goal(goal=goal,goal_strength=sink_strength,safety=safety)
            myVehicle.Go_to_Goal(altitude=0.5,AoAsgn=0,t_start=0,Vinfmag=0) #FIXME add these to the json
            vehicles.append(myVehicle)
        return vehicles
    
    def load_default_case(self):
        sides = 5
        position = (0,0)
        rotation = 0
        radius = 0.5

        obstacle = RegularPolygon(sides = sides, centre = position, rotation=rotation,radius=radius)
        building = Building(obstacle.points())
        Vehicle1 = Vehicle(ID="V1",source_strength=0.5,imag_source_strength=0.5)
        Vehicle1.Set_Goal(goal=[3,   0, 0.5], goal_strength = 5, safety = 0.0001)
        Vehicle1.Set_Position(pos = [ -3,  0.0001 , 0.5])
        buildings, vehicles = [],[]
        buildings.append(building)
        vehicles.append(Vehicle1)
        #print(f"the vehicle list should be {vehicles[0],len(vehicles)}")
        self.add_case(ID="default",building_list=buildings,vehicle_list=vehicles)
        return None
    
    def add_case(self,ID,building_list,vehicle_list):
        '''add a case of name "ID" into the json data file'''
        if ID == "q" or ID == "d":
            #q and d are used to quit or use the default case when the user requests an inexistent case name
            #they are protected (ie the system quits when q is called instead of running a case named 'q')
            raise ValueError(f"'d' and 'q' are protected names, please choose a different name for your case.")
        #create sub dictionary within cases to hold the case
        #print(f"self.cases is {self.cases}")
        self.cases[ID] = {}
        #now set some info about the case. Need to create a list of buildings first though
        self.cases[ID]["buildings"] = []
        #print(f"self.cases is {self.cases}")
        #add the vertices and and number the buildings starting from 0
        for count, building in enumerate(building_list):
            self.cases[ID]["buildings"].append({})
            self.cases[ID]["buildings"][count]["ID"] = f"Building {count}"
            self.cases[ID]["buildings"][count]["vertices"] = building.vertices.tolist()
        #now the vehicles
        #now set some info about the first case. Need to create a list of buildings first though
        self.cases[ID]["vehicles"] = []
        for count, vehicle in enumerate(vehicle_list):
            #print(f"the vehicle list is {vehicle_list}")
            self.cases[ID]["vehicles"].append({})
            self.cases[ID]["vehicles"][count]["ID"] = vehicle.ID
            self.cases[ID]["vehicles"][count]["position"] = vehicle.position.tolist()
            self.cases[ID]["vehicles"][count]["goal"] = vehicle.goal.tolist()
            self.cases[ID]["vehicles"][count]["source_strength"] = vehicle.source_strength
            self.cases[ID]["vehicles"][count]["imag_source_strength"] = vehicle.imag_source_strength
            self.cases[ID]["vehicles"][count]["sink_strength"] = vehicle.sink_strength
            self.cases[ID]["vehicles"][count]["safety"] = vehicle.safety
            #print(f"The bad thing is {self.cases[ID]['vehicles'][count]}")
            #print(f"Id is {ID}")

        with open(self._filename,"w") as f:
            #print(f"self.cases is {self.cases} and filename is {self._filename}")
            #opening in "w" mode wipes the existing file, and we replace the original with self.cases with the new case appended
            json.dump(self.cases,f,sort_keys=False,indent=4)
            # print("After dumping")
        #return the case that was just added
        self.casename = ID
        return self.cases[ID]
    
    def remove_case(self,ID):
        '''Remove a particular case from the cases file, return that case'''
        deleted_case = self.cases.pop(ID) #this returns the value of the removed key
        with open(self._filename,"w") as f:
            json.dump(self.cases,f,sort_keys=False,indent=4)
        return deleted_case
        



if __name__ == "__main__":
    sides = 7
    position = (0,0)
    orientation = 0
    radius = 1

    obstacle = RegularPolygon(sides = sides, centre = position, rotation=orientation,radius=radius)
    building = Building(obstacle.points())
    Vehicle1 = Vehicle(ID="V1",source_strength=0.5,imag_source_strength=0.5)
    Vehicle1.Set_Goal(goal=[3,   0, 0.5], goal_strength = 5, safety = 0.0001)
    Vehicle1.Set_Position(pos = [ -3,  0.0001 , 0.5])
    Vehicle2 = Vehicle(ID="V2",source_strength=0.5,imag_source_strength=0.5)
    Vehicle2.Set_Goal(goal=[-3,   0, 0.5], goal_strength = 5, safety = 0.0001)
    Vehicle2.Set_Position(pos = [ 3,  0.0001 , 0.5])
    Vehicle3 = Vehicle(ID="V3",source_strength=0.5,imag_source_strength=0.5)
    Vehicle3.Set_Goal(goal=[0,   -3, 0.5], goal_strength = 5, safety = 0.0001)
    Vehicle3.Set_Position(pos = [ 0,  3 , 0.5])

    case = Cases()
    #print(f"Now changing the filename")
    case.filename = "examples/cases.json"
    buildings = []
    vehicles = []
    #buildings.append(building)
    vehicles.append(Vehicle1)
    vehicles.append(Vehicle2)
    vehicles.append(Vehicle3)

    case.add_case(ID="threedrones",building_list=buildings,vehicle_list=vehicles)
    #case.add_case(ID="test2",building_list=buildings,vehicle_list=vehicles)
    #print(case.cases)
    
