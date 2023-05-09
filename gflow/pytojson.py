import json
from gflow.building import Building, RegularPolygon
from gflow.vehicle import Vehicle

sides = 7
position = (0,0)
orientation = 0
radius = 1

obstacle = RegularPolygon(sides = sides, centre = position, rotation=orientation,radius=radius)
building = Building(obstacle.points())
Vehicle1 = Vehicle("V1",0.5,0.5)
Vehicle1.Set_Goal([3,   0, 0.5], 5, 0.0001)
Vehicle1.Set_Position([ -3,  0.0001 , 0.5])
#create dict to hold cases
cases = {}
#create sub dictionary within cases to hold the first case named "alpha"
cases["alpha"] = {}
#now set some info about the first case. Need to create a list of buildings first though
cases['alpha']["buildings"] = [{}]
cases['alpha']["buildings"][0]["ID"] = "Building 0"
cases['alpha']["buildings"][0]["vertices"] = building.vertices.tolist()

#now set some info about the first case. Need to create a list of buildings first though
cases['alpha']["vehicles"] = [{}]
cases['alpha']["vehicles"][0]["ID"] = Vehicle1.ID
cases['alpha']["vehicles"][0]["position"] = Vehicle1.position.tolist()
cases['alpha']["vehicles"][0]["goal"] = Vehicle1.goal.tolist()


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



class PyToJSON:
    def __init__(self,casename,filename="examples/cases.json") -> None:
        '''initiate the class with the json filename and the case within that file'''
        self.filename = filename
        self.cases = self.load_file(self.filename)
        print(self.cases)
        self._casename = casename
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

    def load_file(self,filename)->dict:
        '''return a dictionary of all the cases inside filename'''
        try:
            with open(filename,"r") as f:
                cases = json.load(f)
                return cases
        except Exception:
            print(Exception)
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
            position = vehicle["position"]
            goal = vehicle["goal"]
            ID = vehicle["ID"]
            myVehicle = Vehicle(ID=ID,source_strength=0.5,imag_source_strength=0.5)
            myVehicle.Set_Position(position)
            myVehicle.Set_Goal(goal=goal,goal_strength=5,safety=0.0001)
            myVehicle.Go_to_Goal(altitude=0.5,AoAsgn=0,t_start=0,Vinfmag=0)
            vehicles.append(myVehicle)
        return vehicles
        


