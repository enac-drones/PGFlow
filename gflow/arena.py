import numpy as np
from numpy import linalg
import math
import matplotlib.pyplot as plt
import pyclipper
from shapely.geometry import Point, Polygon
from datetime import datetime
from itertools import compress

from building import Building
from vehicle import Vehicle
import pdb

from scipy.spatial import ConvexHull

"""##Arena Code"""

class ArenaMap():
    def __init__(self, version = None, building_hulls=None, generate='manual'):
        self.panels = None
        self.wind = [0,0]
        self.windT = 0
        self.buildings = []
        if building_hulls != None:
            generate = 'auto'
            for key in building_hulls.keys():
                posList = building_hulls[key]['pos']
                points = [(pos[0], pos[1]) for pos in posList] # Turn into 3D here if needed !!!!
                hull = ConvexHull(points)
                self.buildings.append(  Building([[points[i][0], points[i][1], 3.0] for i in hull.vertices])  )
                print(f'Adding {key} into list...')
            
            print('--------------- Here are the Buildings -------------', self.buildings)
        if generate == 'manual':
            version = number
            if version == 0:   # Dubai Map
                self.buildings = [Building([[55.1477081, 25.0890699, 50 ],[ 55.1475319, 25.0888817, 50 ],[ 55.1472176, 25.0891230, 50 ],[ 55.1472887, 25.0892549, 50],[55.1473938, 25.0893113, 50]]),
                                                    Building([[55.1481917, 25.0895323, 87 ],[ 55.1479193, 25.0892520, 87 ],[ 55.1476012, 25.0895056, 87 ],[ 55.1478737, 25.0897859, 87]]),
                                                    Building([[55.1486038, 25.0899385, 53 ],[ 55.1483608, 25.0896681, 53 ],[ 55.1480185, 25.0899204, 53 ],[ 55.1482615, 25.0901908, 53]]),
                                                    Building([[55.1490795, 25.0905518, 82 ],[ 55.1488245, 25.0902731, 82 ],[ 55.1485369, 25.0904890, 82 ],[ 55.1487919, 25.0907677, 82]]),
                                                    Building([[55.1494092, 25.0909286, 54 ],[ 55.1493893, 25.0908353, 54 ],[ 55.1493303, 25.0907662, 54 ],[ 55.1492275, 25.0907240, 54],[ 55.1491268, 25.0907304, 54],[ 55.1490341, 25.0907831, 54],[ 55.1489856, 25.0908571, 54],[ 55.1489748, 25.0909186, 54],[ 55.1489901, 25.0909906, 54],[ 55.1490319, 25.0910511, 54],[ 55.1491055, 25.0910987, 54],[ 55.1491786, 25.0911146, 54],[ 55.1492562, 25.0911063, 54],[ 55.1493356, 25.0910661, 54],[ 55.1493858, 25.0910076, 54]]),
                                                    Building([[55.1485317, 25.0885948, 73 ],[ 55.1482686, 25.0883259, 73 ],[ 55.1479657, 25.0885690, 73 ],[ 55.1482288, 25.0888379, 73]]),
                                                    Building([[55.1489093, 25.0890013, 101],[ 55.1486436, 25.0887191, 101],[ 55.1483558, 25.0889413, 101],[ 55.1486214, 25.0892235, 101]]),
                                                    Building([[55.1492667, 25.0894081, 75 ],[ 55.1489991, 25.0891229, 75 ],[ 55.1487253, 25.0893337, 75 ],[ 55.1489928, 25.0896189, 75]]),
                                                    Building([[55.1503024, 25.0903554, 45 ],[ 55.1499597, 25.0899895, 45 ],[ 55.1494921, 25.0903445, 45 ],[ 55.1497901, 25.0906661, 45],[ 55.1498904, 25.0906734, 45]]),
                                                    Building([[55.1494686, 25.0880107, 66 ],[ 55.1491916, 25.0877250, 66 ],[ 55.1490267, 25.0877135, 66 ],[ 55.1486811, 25.0879760, 66],[ 55.1490748, 25.0883619, 66]]),
                                                    Building([[55.1506663, 25.0900867, 47 ],[ 55.1503170, 25.0897181, 47 ],[ 55.1499784, 25.0899772, 47 ],[ 55.1503277, 25.0903494, 47]]),
                                                    Building([[55.1510385, 25.0898037, 90 ],[ 55.1510457, 25.0896464, 90 ],[ 55.1507588, 25.0893517, 90 ],[ 55.1503401, 25.0896908, 90],[ 55.1506901, 25.0900624, 90]])]
            # If we want to add other arenas:
            elif version == 1:
                self.buildings = [Building([[-1.5, -2.5, 1], [-2.5, -3.5 , 1], [-3.5, -2.5, 1], [-2.5, -1.5, 1]]),
                                                    Building([[ 3 ,  2, 1 ], [ 2.,  2, 1 ] ,[ 2.,  3, 1 ],[ 3.,  3, 1 ]]),
                                                    Building([[ 3.,  -1, 1 ], [ 2., -2, 1 ] ,[ 1., -2, 1 ],[ 1.,  -1, 1 ],[ 2, 0, 1 ],[ 3., 0, 1 ]]),
                                                    #Building([[ 4.1 , -3.9, 1 ], [ 4, -3.9, 1 ] ,[  4,  3.9, 1 ],[  4.1,  3.9, 1 ]]),
                                                    #Building([[ 3.9 , -4.1, 1 ], [ -3.9, -4.1, 1 ] ,[ -3.9,  -4, 1 ],[  3.9,  -4, 1 ]]),
                                                    #Building([[ 3.9 , 4, 1 ], [ -3.9, 4, 1 ] ,[ -3.9,  4.1, 1 ],[  3.9,  4.1, 1 ]]),
                                                    #Building([[ -4 , -3.9, 1 ], [ -4.1, -3.9, 1 ] ,[  -4.1,  3.9, 1 ],[  -4,  3.9, 1 ]]),
                                                    Building([[0.0, 1.0, 1], [-0.293, 0.293, 1], [-1.0, 0.0, 1], [-1.707, 0.293, 1], [-2.0, 1.0, 1], [-1.707, 1.707, 1], [-1.0, 2.0, 1], [-0.293, 1.707, 1]]),
                                                    Building([[-2.0, 3.0, 1], [-2.5, 2.134, 1], [-3.5, 2.134, 1], [-4.0, 3.0, 1], [-3.5, 3.866, 1], [-2.5, 3.866, 1]]) ]

            elif version == 2:
                self.buildings = [Building([[0.3, 1.0, 2], [0.05, 0.567, 2], [-0.45, 0.567, 2], [-0.7, 1.0, 2], [-0.45, 1.433, 2], [0.05, 1.433, 2]]),
                                                    Building([[0.3, 3.0, 1.5], [0.05, 2.567, 1.5], [-0.45, 2.567, 1.5], [-0.7, 3.0, 1.5], [-0.45, 3.433, 1.5], [0.05, 3.433, 1.5]]),
                                                    Building([[1.7, 2.0, 1.2], [1.45, 1.567, 1.2], [0.95, 1.567, 1.2], [0.7, 2.0, 1.2], [0.95, 2.433, 1.2], [1.45, 2.433, 1.2]]),
                                                    Building([[-1.07, -0.2, 1.5], [-1.5, -0.63, 1.5], [-1.93, -0.2, 1.5], [-1.5, 0.23, 1.5]]),
                                                    Building([[-1.07, -2.0, 1.5], [-1.5, -2.43, 1.5], [-1.93, -2.0, 1.5], [-1.5, -1.57, 1.5]]),
                                                    Building([[-2.57, -1.0, 1.5], [-3.0, -1.43, 1.5], [-3.43, -1.0, 1.5], [-3.0, -0.57, 1.5]]),
                                                    Building([[-2.57, 1.0, 1.5], [-3.0, 0.57, 1.5], [-3.43, 1.0, 1.5], [-3.0, 1.43, 1.5]]),
                                                    Building([[1, -2.1, 1.2], [0.5, -2.1, 1.2], [0.5, -1, 1.2], [1, -0.6, 1.2]]),
                                                    Building([[2.5, -2.1, 1.2], [2, -2.1, 1.2], [2, -0.6, 1.2], [2.5, -1, 1.2]])]
            elif version == 3:
                self.buildings = [
                                                    Building([[1.7, 2.0, 2], [1.45, 1.567, 2], [0.95, 1.567, 2], [0.7, 2.0, 2], [0.95, 2.433, 2], [1.45, 2.433, 2]])]
            elif version == 4:
                self.buildings = [Building([[0.3, 1.0, 2], [0.05, 0.567, 2], [-0.45, 0.567, 2], [-0.7, 1.0, 2], [-0.45, 1.433, 2], [0.05, 1.433, 2]]),
                                                    Building([[0.3, 3.0, 2], [0.05, 2.567, 2], [-0.45, 2.567, 2], [-0.7, 3.0, 2], [-0.45, 3.433, 2], [0.05, 3.433, 2]]),
                                                    Building([[1.7, 2.0, 2], [1.45, 1.567, 2], [0.95, 1.567, 2], [0.7, 2.0, 2], [0.95, 2.433, 2], [1.45, 2.433, 2]])]
            elif version == 41:
                self.buildings = [Building([[0.3, 1.0, 2], [0.05, 0.567, 2], [-0.45, 0.567, 2], [-0.7, 1.0, 2], [-0.45, 1.433, 2], [0.05, 1.433, 2]]),
                                                    Building([[1.7, 2.0, 2], [1.45, 1.567, 2], [0.95, 1.567, 2], [0.7, 2.0, 2], [0.95, 2.433, 2], [1.45, 2.433, 2]])]
            elif version == 5:
                self.buildings = [Building([[-3.9, 3.9, 2], [-4.1, 3.9, 2], [-4.1, 4.1, 2], [-3.9, 4.1, 2]]),
                                                    Building([[4.1, 3.9, 2], [3.9, 3.9, 2], [3.9, 4.1, 2], [4.1, 4.1, 2]]),
                                                    Building([[4.1, -4.1, 2], [3.9, -4.1, 2], [3.9, -3.9, 2], [4.1, -3.9, 2]]),
                                                    Building([[-3.9, -4.1, 2], [-4.1, -4.1, 2], [-4.1, -3.9, 2], [-3.9, -3.9, 2]])]
            elif version == 6:
                self.buildings = [Building([[3.0, 2.0, 1.2], [2.75, 1.567, 1.2], [2.25, 1.567, 1.2], [2.0, 2.0, 1.2], [2.25, 2.433, 1.2], [2.75, 2.433, 1.2]]), #AddCircularBuilding( 2.5, 2, 6, 0.5, 1.2, angle = 0)
                                                    Building([[1.0, 3.0, 1.5], [0.75, 2.567, 1.5], [0.25, 2.567, 1.5], [0.0, 3.0, 1.5], [0.25, 3.433, 1.5], [0.75, 3.433, 1.5]]), #AddCircularBuilding( 0.5, 3, 6, 0.5, 1.5, angle = 0)
                                                    Building([[1.0, 0.5, 2], [0.75, 0.067, 2], [0.25, 0.067, 2], [0.0, 0.5, 2], [0.25, 0.933, 2], [0.75, 0.933, 2]]), #AddCircularBuilding( 0.5, 0.5, 6, 0.5, 2, angle = 0)
                                                    Building([[-2.65, 1.5, 1.5], [-3.0, 1.15, 1.5], [-3.35, 1.5, 1.5], [-3.0, 1.85, 1.5]]), #AddCircularBuilding( -3, 1.5, 4, 0.35, 1.5, angle = 0)
                                                    Building([[-2.65, -1.5, 1.5], [-3.0, -1.85, 1.5], [-3.35, -1.5, 1.5], [-3.0, -1.15, 1.5]]), #AddCircularBuilding( -3, -1.5, 4, 0.35, 1.5, angle = 0)
                                                    Building([[-1.15, -0.2, 1.5], [-1.5, -0.55, 1.5], [-1.85, -0.2, 1.5], [-1.5, 0.15, 1.5]]), #AddCircularBuilding( -1.5, -0.2, 4, 0.35, 1.5, angle = 0)
                                                    Building([[1.5, -2.5, 1.2], [1, -2.5, 1.2], [1, -1.4, 1.2], [1.5, -1, 1.2]]),
                                                    Building([[3.5, -2.5, 1.2], [3, -2.5, 1.2], [3, -1, 1.2], [3.5, -1.4, 1.2]])]
            elif version == 61:
                self.buildings = [Building([[1.0, 0.5, 2], [0.75, 0.067, 2], [0.25, 0.067, 2], [0.0, 0.5, 2], [0.25, 0.933, 2], [0.75, 0.933, 2]])]
            elif version == 8:
                self.buildings = [Building([[20.0, 15.0, 40], [17.5, 10.67, 40], [12.5, 10.67, 40], [10.0, 15.0, 40], [12.5, 19.33, 40], [17.5, 19.33, 40]]), #Arena.AddCircularBuilding( 15, 15, 6, 5, 40, angle = 0)
                                                    Building([[40.0, 27.0, 40], [46.062, 23.5, 40], [46.062, 16.5, 40], [40.0, 13.0, 40], [33.938, 16.5, 40], [33.938, 23.5, 40]]), #Arena.AddCircularBuilding( 40, 20, 6, 7, 40, angle = np.pi/2)
                                                    Building([[31.0, 45.0, 40], [26.854, 39.294, 40], [20.146, 41.473, 40], [20.146, 48.527, 40], [26.854, 50.706, 40]]), #Arena.AddCircularBuilding( 25, 45, 5, 6, 40, angle = 0)
                                                    Building([[12.828, 37.828, 40], [11.035, 31.136, 40], [6.136, 36.035, 40]]), #Arena.AddCircularBuilding( 10, 35, 3, 4, 40, angle = np.pi/4) 
                                                    Building([[55.657, 45.657, 40], [55.657, 34.343, 40], [44.343, 34.343, 40], [44.343, 45.657, 40]])] #Arena.AddCircularBuilding( 50, 40, 4, 8, 40, angle = np.pi/4)
        elif generate == 'random':
            self.buildings = []
            self.buildings.append(self.AddRandomBuilding())
            while len(self.buildings) < number:
                temp_building = self.AddRandomBuilding()
                for i in range(len(self.buildings) ):
                    x = self.buildings[i].position[0]
                    y = self.buildings[i].position[1]
                    r = self.buildings[i].position[2]
                    d = ( (x-temp_building.position[0])**2 + (y-temp_building.position[1])**2 )**0.5
                    if d < r*2 + temp_building.position[2]:
                        break
                    if i == len(self.buildings)-1:
                        self.buildings.append(temp_building)


    def Inflate(self, visualize = False, radius = 1e-4):
        # Inflates buildings with given radius
        if visualize: self.Visualize2D(buildingno="All", show = False)
        for building in self.buildings:
            building.inflate(rad = radius)
        if visualize: self.Visualize2D(buildingno="All")
            #self.buildings[index].vertices[:,:2] = self.buildings[index].inflated
    def Panelize(self,size):
         # Divides building edges into smaller line segments, called panels.
        for building in self.buildings:
            building.panelize(size)

    def Calculate_Coef_Matrix(self,method = 'Vortex'):
        # !!Assumption: Seperate building interractions are neglected. Each building has its own coef_matrix
        for building in self.buildings:
            building.calculate_coef_matrix(method = method)

    def Visualize2D(self,buildingno = "All",points = "buildings", show = True):
        plt.grid(color = 'k', linestyle = '-.', linewidth = 0.5)
        #minx = -5 # min(min(building.vertices[:,0].tolist()),minx)
        #maxx = 5 # max(max(building.vertices[:,0].tolist()),maxx)
        #miny = -5 # min(min(building.vertices[:,1].tolist()),miny)
        #maxy = 5 # max(max(building.vertices[:,1].tolist()),maxy)
        #plt.xlim([minx, maxx])
        #plt.ylim([miny, maxy])
        if buildingno == "All":
            if points == "buildings":
                for building in self.buildings:
                    # plt.scatter(  np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) )
                    plt.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'b' )
                    plt.fill(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) ,'b' )
            elif points == "panels":
                for building in self.buildings:
                    plt.scatter(building.panels[:,0],building.panels[:,1])
                    plt.plot(building.panels[:,0],building.panels[:,1])
                    controlpoints = building.pcp
                    plt.scatter(controlpoints[:,0],controlpoints[:,1], marker = '*')
            if show: plt.show()
        else:
            if points == "buildings":
                building = self.buildings[buildingno]
                plt.scatter(  np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) )
                plt.plot(     np.hstack((building.vertices[:,0],building.vertices[0,0]))  , np.hstack((building.vertices[:,1],building.vertices[0,1] )) )
            elif points == "panels":
                building = self.buildings[buildingno]
                controlpoints = building.pcp
                plt.scatter(building.panels[:,0],building.panels[:,1])
                plt.scatter(controlpoints[:,0],controlpoints[:,1], marker = '*')
                plt.plot( np.vstack((building.panels[:], building.panels[0] ))[:,0], np.vstack((building.panels[:], building.panels[0]))[:,1],markersize = 0)
            if show: plt.show()

    def Visualize3D(self,buildingno = "All",show = "buildings"):
        pass

    def ScaleIntoMap(self, shape =  np.array(  ((-1,-1),(1,1))  ) ):
        pass

    def AddCircularBuilding(self, x_offset, y_offset, no_of_pts, size, height = 1, angle = 0):
        n = 6 #number of points
        circle_list = []
        #offset_x = -3
        #offset_y = 3
        #size = 1
        #height = 1
        for i in range(no_of_pts):
            delta_rad = -2*math.pi / no_of_pts * i
            circle_list.append( [round(math.cos(delta_rad)*size + x_offset,3) , round( math.sin(delta_rad)*size + y_offset,3), height] )
        print("Building(" + str(circle_list) + ")" )

    def Wind(self,wind_str = 0, wind_aoa = 0, info = 'unknown'):
        self.wind[0] = wind_str * np.cos(wind_aoa)
        self.wind[1] = wind_str * np.sin(wind_aoa)
        if info == 'known':
            self.windT = 1
        elif info == 'unknown':
            self.windT = 0

    def AddRandomBuilding(self):
            center_x = round(random.uniform(-3, 3),3)
            center_y = round(random.uniform(-3, 3),3)
            #radius = round(random.uniform(0.25, 1),3)
            radius = round(random.uniform(0.25, 1.5),3)
            position = np.array([center_x, center_y, radius ])
            n = random.randint(3, 10) # number of vertices
            height = round(random.uniform(1.25, 2),3)
            circle_list = []
            theta = np.sort(np.random.rand(n)*2*np.pi)  ## Generate n random numbers btw 0-2pi and sort: small to large
            for j in range(n):
                circle_list.append( [round(math.cos(theta[j])*radius + center_x,3) , round( math.sin(theta[j])*radius  + center_y,3), height] )   ######
            return Building(circle_list,position)
