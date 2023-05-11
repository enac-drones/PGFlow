import json
from gflow.building import Building, RegularPolygon
from gflow.vehicle import Vehicle
import os

sides = 7
position = (0,0)
orientation = 0
radius = 1

obstacle = RegularPolygon(sides = sides, centre = position, rotation=orientation,radius=radius)
building = Building(obstacle.points())
Vehicle1 = Vehicle(ID="V1",source_strength=0.5,imag_source_strength=0.5)
Vehicle1.Set_Goal(goal=[3,   0, 0.5], goal_strength = 5, safety = 0.0001)
Vehicle1.Set_Position(pos = [ -3,  0.0001 , 0.5])
#create dict to hold cases
cases = {}
#create sub dictionary within cases to hold the first case named "alpha"
cases["alpha"] = {}
#now set some info about the first case. Need to create a list of buildings first though
cases['alpha']["buildings"] = [{}]
cases['alpha']["buildings"][0]["ID"] = "Building 0"
cases['alpha']["buildings"][0]["vertices"] = building.vertices.tolist()

#now set some info about the first case. Need to create a list of buildings first though
cases['alpha']["vehicles"] = []
cases['alpha']["vehicles"].append({})
cases['alpha']["vehicles"][0]["ID"] = Vehicle1.ID
cases['alpha']["vehicles"][0]["position"] = Vehicle1.position.tolist()
cases['alpha']["vehicles"][0]["goal"] = Vehicle1.goal.tolist()
cases['alpha']["vehicles"][0]["source_strength"] = Vehicle1.source_strength
cases['alpha']["vehicles"][0]["imag_source_strength"] = Vehicle1.imag_source_strength
cases['alpha']["vehicles"][0]["sink_strength"] = Vehicle1.sink_strength
cases['alpha']["vehicles"][0]["safety"] = Vehicle1.safety
#cases['alpha']["vehicles"].append({})


with open("examples/cases.json","w") as f:
    json.dump(cases,f,sort_keys=False,indent=4)
    # can add this to line above if you wish: separators = (",",": ")

#print(cases)

with open("examples/cases.json","r") as f:
    cases = json.load(f)
    

print(cases)
print(type(cases))
coords = cases['alpha']['buildings'][0]['vertices']
print(coords)

building1 = Building(coords)
print(building1.vertices)


print(f"Vehicle properties are: position {Vehicle1.position}, goal {Vehicle1.goal}")



class JSON2Py:
    def __init__(self,filename="examples/cases.json") -> None:
        '''initiate the class with the json filename and the case within that file'''
        self._filename = filename
        self.cases = self.load_file(self.filename)
        #print(f"cases are {self.cases}")
        self._casename = "alpha"
        #self.buildings = self.obtain_buildings(self.cases,self.casename)

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
            print(f"Error: {new_name} is an invalid case name.")

    @property
    def filename(self):
        return self._filename
    
    @filename.setter
    def filename(self,new_name):
        """Set new filename and reset the cases object"""
        try:
            self.cases = self.load_file(new_name)
            self._filename = new_name
        except Exception:
            print(Exception)

    def load_file(self,filename)->dict:
        '''return a dictionary of all the cases inside filename'''
        # print(f"current directory is {os.getcwd()}")
        # print([f for f in os.listdir('./examples')])
        # print(f"path is {os.path}")
        try:
            with open(filename,"r") as f:
                # print("asd;lfajsl;dfja")
                # print(f.read())
                cases = json.load(f)
                return cases
        except Exception as ex:
            print(Exception)
            # print(ex,type(ex).__name__, ex.args)
            print(f"File {filename} not found. Please try again.")
            return None
        
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
            myVehicle = Vehicle(ID=ID,source_strength=0.5,imag_source_strength=0.5)
            myVehicle.Set_Position(position)
            myVehicle.Set_Goal(goal=goal,goal_strength=5,safety=0.0001)
            myVehicle.Go_to_Goal(altitude=0.5,AoAsgn=0,t_start=0,Vinfmag=0)
            vehicles.append(myVehicle)
        return vehicles
        
    def add_case(self,ID,building_list,vehicle_list):
        '''add a case of name "ID" into the json data file'''
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
            self.cases[ID]["vehicles"].append({})
            self.cases[ID]["vehicles"][0]["ID"] = vehicle.ID
            self.cases[ID]["vehicles"][0]["position"] = vehicle.position.tolist()
            self.cases[ID]["vehicles"][0]["goal"] = vehicle.goal.tolist()
            self.cases[ID]["vehicles"][0]["source_strength"] = vehicle.source_strength
            self.cases[ID]["vehicles"][0]["imag_source_strength"] = vehicle.imag_source_strength
            self.cases[ID]["vehicles"][0]["sink_strength"] = vehicle.sink_strength
            self.cases[ID]["vehicles"][0]["safety"] = vehicle.safety
        with open(self._filename,"w") as f:
            json.dump(self.cases,f,sort_keys=False,indent=4)
        return None
    
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

    converter = JSON2Py()
    print(f"al;sdjfas;ldfj{os.getcwd()}")
    #converter.filename = "./examples/myjson.json"
    buildings = []
    vehicles = []
    buildings.append(building)
    vehicles.append(Vehicle1)
    converter.add_case(ID="test1",building_list=buildings,vehicle_list=vehicles)


    print(converter.cases)
    
