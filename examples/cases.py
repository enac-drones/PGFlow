from gflow.vehicle import Vehicle
from gflow.building import Building
from gflow.arena import ArenaMap
import numpy as np
from copy import copy, deepcopy

class Cases():
	def __init__(self, case_no=0, arenamap=None, generate = 'manual'):

		if generate == 'manual':
			if case_no == 0:

				self.buildings = [Building([[3.0, 2.0, 1.2], [2.75, 1.567, 1.2], [2.25, 1.567, 1.2], [2.0, 2.0, 1.2], [2.25, 2.433, 1.2], [2.75, 2.433, 1.2]]), #AddCircularBuilding( 2.5, 2, 6, 0.5, 1.2, angle = 0)
								Building([[1.0, 3.0, 1.5], [0.75, 2.567, 1.5], [0.25, 2.567, 1.5], [0.0, 3.0, 1.5], [0.25, 3.433, 1.5], [0.75, 3.433, 1.5]]), #AddCircularBuilding( 0.5, 3, 6, 0.5, 1.5, angle = 0)
								Building([[1.0, 0.5, 2], [0.75, 0.067, 2], [0.25, 0.067, 2], [0.0, 0.5, 2], [0.25, 0.933, 2], [0.75, 0.933, 2]]), #AddCircularBuilding( 0.5, 0.5, 6, 0.5, 2, angle = 0)
								Building([[-2.65, 1.5, 1.5], [-3.0, 1.15, 1.5], [-3.35, 1.5, 1.5], [-3.0, 1.85, 1.5]]), #AddCircularBuilding( -3, 1.5, 4, 0.35, 1.5, angle = 0)
								Building([[-2.65, -1.5, 1.5], [-3.0, -1.85, 1.5], [-3.35, -1.5, 1.5], [-3.0, -1.15, 1.5]]), #AddCircularBuilding( -3, -1.5, 4, 0.35, 1.5, angle = 0)
								Building([[-1.15, -0.2, 1.5], [-1.5, -0.55, 1.5], [-1.85, -0.2, 1.5], [-1.5, 0.15, 1.5]]), #AddCircularBuilding( -1.5, -0.2, 4, 0.35, 1.5, angle = 0)
								Building([[1.5, -2.5, 1.2], [1, -2.5, 1.2], [1, -1.4, 1.2], [1.5, -1, 1.2]]),
								Building([[3.5, -2.5, 1.2], [3, -2.5, 1.2], [3, -1, 1.2], [3.5, -1.4, 1.2]])]

				Vehicle1 = Vehicle("V1",0.5,0.5)            # Vehicle ID, Source_strength imaginary source = 1.5
				Vehicle2 = Vehicle("V2",0.5,0.5)
				Vehicle3 = Vehicle("V3",0.5,0.5)
				
				Vehicle1.Set_Goal([-3,   0, 0.5], 5, 0.0001)       # goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
				Vehicle2.Set_Goal([ 2, 3.5, 0.5], 5, 0.0001)
				Vehicle3.Set_Goal([ 2,   1, 0.5], 5, 0.0001)

				Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
				Vehicle2.Go_to_Goal(0.5,0,0,0)        # np.arctan2(3.5+1,1.5+0.5) = 1.1525719 rad
				Vehicle3.Go_to_Goal(0.5,0,0,0)

				Vehicle1.Set_Position([ 3,  1 , 0.5])
				Vehicle2.Set_Position([-1, -3 , 0.5])
				Vehicle3.Set_Position([-3,  3 , 0.5])
				self.Vehicle_list = [Vehicle1,Vehicle2,Vehicle3] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]

			elif case_no == 1:
				#case for drones to swap positions 

				self.buildings = []

				Vehicle1 = Vehicle("V1",0.5,0.5)            # Vehicle ID, Source_strength imaginary source = 1.5
				Vehicle2 = Vehicle("V2",0.5,0.5)
				#Vehicle3 = Vehicle("V3",0.5,0.5)
				
				Vehicle1.Set_Goal([3,   0, 0.5], 5, 0.0001)       # goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
				Vehicle2.Set_Goal([ -3, 0, 0.5], 5, 0.0001)
				#Vehicle3.Set_Goal([ 0,   3, 0.5], 5, 0.0001)

				Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude, AoA,t_start,Vinf=0.5,0.5,1.5
				Vehicle2.Go_to_Goal(0.5,0,0,0)        # np.arctan2(3.5+1,1.5+0.5) = 1.1525719 rad
				#Vehicle3.Go_to_Goal(0.5,0,0,0)

				Vehicle1.Set_Position([ -3,  0.00001 , 0.5])
				Vehicle2.Set_Position([ 3, 0 , 0.5])
				#Vehicle3.Set_Position([0,  -3 , 0.5])
				self.Vehicle_list = [Vehicle1,Vehicle2] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]

			elif case_no == 61:
				Vehicle1 = Vehicle("V1",0,0.5)             # Vehicle ID, Source_strength,safety
				Vehicle_list = [Vehicle1]

				Vehicle1.Set_Position([ -2, 0.5, 0.50])
				Vehicle1.Set_Goal([3, 0.5, 0.5], 5, 0 )       # goal,goal_strength 30, safety 0.001
				Vehicle1.Go_to_Goal(1.5, 0,0)               # altitude,AoAsgn,t_start,Vinfmag
			elif case_no == 31:
				Vehicle1 = Vehicle("V1",0,0.1)            # Vehicle ID, Source_strength
				Vehicle2 = Vehicle("V2",0,0.1)
				Vehicle3 = Vehicle("V3",0,0)
				Vehicle4 = Vehicle("V4",0,0)
				Vehicle5 = Vehicle("V5",0,0)
				Vehicle6 = Vehicle("V6",0,0)
				Vehicle_list = [Vehicle1,Vehicle2,Vehicle3,Vehicle4,Vehicle5,Vehicle6]

				Vehicle1.Set_Position([ -2, 2, 0.50])
				Vehicle2.Set_Position([-1.999, 2, 0.50])
				Vehicle3.Set_Position([-2.002, 2, 0.50])
				Vehicle4.Set_Position([-1.998, 2, 0.50])
				Vehicle5.Set_Position([-1.9985, 2, 0.50])
				Vehicle6.Set_Position([-2.0015, 2, 0.50])

				Vehicle1.Set_Goal([3, 2, 0.5], 5, 0)       # goal,goal_strength 30, safety 0.001 for vortex method
				Vehicle2.Set_Goal([3, 2, 0.5], 5, 0)
				Vehicle3.Set_Goal([3, 2, 0.2], 5, 0)
				Vehicle4.Set_Goal([3, 2, 0.2], 5, 0)
				Vehicle5.Set_Goal([3, 2, 0.2], 5, 0)
				Vehicle6.Set_Goal([3, 2, 0.2], 5, 0)

				Vehicle1.Go_to_Goal(1.5,0,0,0)         # altitude,AoAsgn,t_start,Vinfmag
				Vehicle2.Go_to_Goal(1.5,0,0,0.1)
				Vehicle3.Go_to_Goal(1.5,0,0,0.1)
				Vehicle4.Go_to_Goal(1.5,0,0,0.3)
				Vehicle5.Go_to_Goal(1.5,0,0,0.4)
				Vehicle6.Go_to_Goal(1.5,0,0,0.5)
			elif case_no == 71:
				Vehicle1 = Vehicle("V1",0,0.5)            # Vehicle ID, Source_strength,safety
				Vehicle2 = Vehicle("V2",0,0.5)
				Vehicle3 = Vehicle("V3",0,0.5)
				Vehicle4 = Vehicle("V4",0,0.5)
				Vehicle5 = Vehicle("V5",0,0.5)
				Vehicle6 = Vehicle("V6",0,0.5)
				Vehicle7 = Vehicle("V7",0,0.5)
				Vehicle_list = [Vehicle1,Vehicle2,Vehicle3,Vehicle4,Vehicle5,Vehicle6,Vehicle7]

				Vehicle1.Set_Position([ -2, 3, 0.50])
				Vehicle2.Set_Position([-1.999, 2, 0.50])
				Vehicle3.Set_Position([-2.002, 2, 0.50])
				Vehicle4.Set_Position([-1.99, 2, 0.50])
				Vehicle5.Set_Position([-1.995, 2, 0.50])
				Vehicle6.Set_Position([-2.0015, 2, 0.50])
				Vehicle7.Set_Position([-2.001, 2, 0.50])

				Vehicle1.Set_Goal([3, 2, 0.5], 5, 0, 0    )       # goal,goal_strength 30, safety 0.001, Vinfmag=0.5,0.5,1.5 for vortex method
				Vehicle2.Set_Goal([3, 2, 0.5], 5, 0, 0.01 )
				Vehicle3.Set_Goal([3, 2, 0.2], 5, 0, 0.01 )
				Vehicle4.Set_Goal([3, 2, 0.2], 5, 0, 0.025)
				Vehicle5.Set_Goal([3, 2, 0.2], 5, 0, 0.025)
				Vehicle6.Set_Goal([3, 2, 0.2], 5, 0, 0.05 )
				Vehicle7.Set_Goal([3, 2, 0.2], 5, 0, 0.05 )

				Vehicle1.Go_to_Goal(1.5, 0,0)         # altitude,AoAsgn,t_start,
				Vehicle2.Go_to_Goal(1.5, 1,0)
				Vehicle3.Go_to_Goal(1.5, 1,0)
				Vehicle4.Go_to_Goal(1.5, 1,0)
				Vehicle5.Go_to_Goal(1.5,-1,0)
				Vehicle6.Go_to_Goal(1.5,-1,0)
				Vehicle7.Go_to_Goal(1.5,-1,0)
			elif case_no == 72:
				Vehicle1 = Vehicle("V1",0,0.5)            # Vehicle ID, Source_strength,safety
				Vehicle2 = Vehicle("V2",0,0.5)
				Vehicle3 = Vehicle("V3",0,0.5)
				Vehicle4 = Vehicle("V4",0,0.5)
				Vehicle5 = Vehicle("V5",0,0.5)
				Vehicle6 = Vehicle("V6",0,0.5)
				Vehicle7 = Vehicle("V7",0,0.5)
				Vehicle_list = [Vehicle1,Vehicle2,Vehicle3,Vehicle4,Vehicle5,Vehicle6,Vehicle7]

				Vehicle1.Set_Position([0  ,    3, 0.50])
				Vehicle2.Set_Position([0.002,  3, 0.50])
				Vehicle3.Set_Position([-0.002, 3, 0.50])
				Vehicle4.Set_Position([0.001,  3, 0.50])
				Vehicle5.Set_Position([0.0015, 3, 0.50])
				Vehicle6.Set_Position([-0.0015,3, 0.50])
				Vehicle7.Set_Position([-0.001, 3, 0.50])

				Vehicle1.Set_Goal([2, 0, 0.5], 5, 0, 0    )       # goal,goal_strength 30, safety 0.001, Vinfmag=0.5,0.5,1.5 for vortex method
				Vehicle2.Set_Goal([2, 0, 0.5], 5, 0, 0.01 )
				Vehicle3.Set_Goal([2, 0, 0.5], 5, 0, 0.01 )
				Vehicle4.Set_Goal([2, 0, 0.5], 5, 0, 0.025)
				Vehicle5.Set_Goal([2, 0, 0.5], 5, 0, 0.025)
				Vehicle6.Set_Goal([2, 0, 0.5], 5, 0, 0.05 )
				Vehicle7.Set_Goal([2, 0, 0.5], 5, 0, 0.05 )

				Vehicle1.Go_to_Goal(1.5, 0,0)         # altitude,AoAsgn,t_start,
				Vehicle2.Go_to_Goal(1.5, 1,0)
				Vehicle3.Go_to_Goal(1.5, 1,0)
				Vehicle4.Go_to_Goal(1.5, 1,0)
				Vehicle5.Go_to_Goal(1.5,-1,0)
				Vehicle6.Go_to_Goal(1.5,-1,0)
				Vehicle7.Go_to_Goal(1.5,-1,0)
			elif case_no == 73:
				Vehicle1 = Vehicle("V1",0,0.5)            # Vehicle ID, Source_strength,safety
				Vehicle_list = [Vehicle1]

				Vehicle1.Set_Position([0  ,3, 0.50])
				Vehicle1.Set_Goal([2, 0, 0.5], 5, 0)       # goal,goal_strength 30, safety 0.001
				Vehicle1.Go_to_Goal(1.5, 0,0)              # altitude,AoAsgn,t_start,Vinfmag
			elif case_no == 74:
				Vehicle1 = Vehicle("V1",0,0.5)             # Vehicle ID, Source_strength,safety
				Vehicle_list = [Vehicle1]

				Vehicle1.Set_Position([ -2, 2, 0.50])
				Vehicle1.Set_Goal([3, 2, 0.5], 5, 0 )       # goal,goal_strength 30, safety 0.001
				Vehicle1.Go_to_Goal(1.5, 0,0)               # altitude,AoAsgn,t_start,Vinfmag


			elif case_no == 0:
				Vehicle1 = Vehicle("V1",0,0)            # Vehicle ID, Source_strength
				Vehicle2 = Vehicle("V2",0,0.1)
				Vehicle3 = Vehicle("V3",0,0.5)
				Vehicle4 = Vehicle("V4",0,1)
				Vehicle5 = Vehicle("V5",0,2.5)
				Vehicle6 = Vehicle("V6",0,25)
				Vehicle_list = [Vehicle1,Vehicle2,Vehicle3,Vehicle4,Vehicle5,Vehicle6]

				Vehicle1.Set_Goal([3, 2, 0.5], 5, 0)       # goal,goal_strength 30, safety 0.001 for vortex method
				Vehicle2.Set_Goal([3, 2, 0.5], 5, 0)
				Vehicle3.Set_Goal([3, 2, 0.2], 5, 0)
				Vehicle4.Set_Goal([3, 2, 0.2], 5, 0)
				Vehicle5.Set_Goal([3, 2, 0.2], 5, 0)
				Vehicle6.Set_Goal([3, 2, 0.2], 5, 0)

				Vehicle1.Go_to_Goal(1.5,0,0,0)         # altitude,AoAsgn,t_start,Vinfmag
				Vehicle2.Go_to_Goal(1.5,0,0,1)
				Vehicle3.Go_to_Goal(1.5,0,0,2)
				Vehicle4.Go_to_Goal(1.5,0,0,3)
				Vehicle5.Go_to_Goal(1.5,0,0,4)
				Vehicle6.Go_to_Goal(1.5,0,0,5)

				Vehicle1.Set_Position([ -2, 2, 0.50])
				Vehicle2.Set_Position([-1.999, 2, 0.50])
				Vehicle3.Set_Position([-2.002, 2, 0.50])
				Vehicle4.Set_Position([-1.998, 2, 0.50])
				Vehicle5.Set_Position([-1.9985, 2, 0.50])
				Vehicle6.Set_Position([-2.0015, 2, 0.50])
			elif case_no == 8:
				Vehicle1 = Vehicle("V1",0,0.85)            # Vehicle ID, Source_strength, im 0.85 veh 0.95
				Vehicle2 = Vehicle("V2",2,0.85)

				Vehicle_list = [Vehicle1,Vehicle2] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]

				Vehicle1.Set_Goal([1.5, -3, 0.5], 5, 0)       # for arena 6  [1.5, -3.3, 0.5]
				Vehicle2.Set_Goal([1.50001, -2, 0.5] , 5, 0)   # for arena 6 [2.0001, -2.3, 0.5]

				Vehicle1.Go_to_Goal(0.5,-np.pi/2,0,0.5)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
				Vehicle2.Go_to_Goal(0.5,0,0,0)

				Vehicle1.Set_Position([2, 1.5, 0.50])   #for arena 6 [2.5, 0.5, 0.50]
				Vehicle2.Set_Position([1.5, -2 , 0.5])     #for arena 6 [2, -2.3 , 0.5]
			elif case_no == 117:
				Vehicle1 = Vehicle("V1",0,0.5)            # Vehicle ID, Source_strength imaginary source = 1.5
				Vehicle2 = Vehicle("V2",0,0.5)
				Vehicle3 = Vehicle("V3",0,0.5)
				Vehicle_list = [Vehicle1,Vehicle2,Vehicle3] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]

				Vehicle1.Set_Goal([-3, 0, 0.5], 5, 0.0001)       # goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
				Vehicle2.Set_Goal([2, 3.5, 0.5], 5, 0.0001)
				Vehicle3.Set_Goal([2, 1, 0.5], 5, 0.0001)

				Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
				Vehicle2.Go_to_Goal(0.5,0,0,0)        # np.arctan2(3.5+1,1.5+0.5) = 1.1525719 rad
				Vehicle3.Go_to_Goal(0.5,0,0,0)

				Vehicle1.Set_Position([3, 1 , 0.5])
				Vehicle2.Set_Position([-1, -3 , 0.5])
				Vehicle3.Set_Position([-3, 3 , 0.5])
			elif case_no == 1171:
				#Vehicle1 = Vehicle("V1",0,0.5)            # Vehicle ID, Source_strength imaginary source = 1.5
				Vehicle2 = Vehicle("V2",0,0.5)
				#Vehicle3 = Vehicle("V3",0,0.5)
				Vehicle_list = [Vehicle2] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3] Vehicle1,Vehicle2,

				#Vehicle1.Set_Goal([-3, 0, 0.5], 5, 0.000)       # goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
				Vehicle2.Set_Goal([2, 3.5, 0.5], 5, 0.000)
				#Vehicle3.Set_Goal([2, 1, 0.5], 5, 0.000)

				#Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
				Vehicle2.Go_to_Goal(0.5,0,0,0)        # np.arctan2(3.5+1,1.5+0.5) = 1.1525719 rad
				#Vehicle3.Go_to_Goal(0.5,0,0,0)

				#Vehicle1.Set_Position([3, 1 , 0.5])
				Vehicle2.Set_Position([-1, -3 , 0.5])
				#Vehicle3.Set_Position([-3, 3 , 0.5])
			elif case_no == 11:
				Vehicle1 = Vehicle("V1",0,0.3)            # Vehicle ID, Source_strength imaginary source = 1.5
				Vehicle2 = Vehicle("V2",0,0.3)
				Vehicle3 = Vehicle("V3",0,0.3)
				Vehicle_list = [Vehicle1,Vehicle2,Vehicle3] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]

				Vehicle1.Set_Goal([-3, 0, 0.5], 5, 0.0000)       # goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
				Vehicle2.Set_Goal([2, 3.5, 0.5], 5, 0.00000)
				Vehicle3.Set_Goal([2, 1, 0.5], 5, 0.00000)

				Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
				Vehicle2.Go_to_Goal(0.5,0,0,0)        # np.arctan2(3.5+1,1.5+0.5) = 1.1525719 rad
				Vehicle3.Go_to_Goal(0.5,0,0,0)

				Vehicle1.Set_Position([3, 1 , 0.5])
				Vehicle2.Set_Position([-1, -3 , 0.5])
				Vehicle3.Set_Position([-3, 3 , 0.5])
			elif case_no == 12:
				Vehicle1 = Vehicle("V1",0,0.85)            # Vehicle ID, Source_strength imaginary source = 0.75
				Vehicle2 = Vehicle("V2",0.75,0.85)
				Vehicle3 = Vehicle("V3",0,0.85)
				Vehicle_list = [Vehicle1,Vehicle2,Vehicle3] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]

				Vehicle1.Set_Goal([2.5, -3.5, 0.5], 5, 0.0000)       # goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
				Vehicle2.Set_Goal([-0.5, 3 , 0.5], 5, 0.00000)
				Vehicle3.Set_Goal([3, 3, 0.5], 5, 0.00000)

				Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
				Vehicle2.Go_to_Goal(0.5,0,0,0)
				Vehicle3.Go_to_Goal(0.5,0,0,0)

				Vehicle1.Set_Position([-2, 3 , 0.5])
				Vehicle2.Set_Position([-2, -3, 0.5])
				Vehicle3.Set_Position([-3, 0, 0.5])
			elif case_no == 121:
				Vehicle1 = Vehicle("V1",0,0.85)            # Vehicle ID, Source_strength imaginary source = 0.75
				Vehicle_list = [Vehicle1] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]
				Vehicle1.Set_Position([-2, 3 , 0.5])
				Vehicle1.Set_Goal([2.5, -3.5, 0.5], 5, 0.0000)       # goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
				Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
			elif case_no == 13:
				Vehicle1 = Vehicle("V1",0.25)            # Vehicle ID, Source_strength
				Vehicle2 = Vehicle("V2",0.5)
				Vehicle3 = Vehicle("V3",0.25)
				Vehicle4 = Vehicle("V4",0.5)
				Vehicle5 = Vehicle("V5",0.5)
				Vehicle6 = Vehicle("V6",0.5)
				Vehicle7 = Vehicle("V7",0.25)
				Vehicle8 = Vehicle("V8",0.5)
				Vehicle9 = Vehicle("V9",0.25)
				Vehicle10 = Vehicle("V10",0.5)
				Vehicle_list = [Vehicle1,Vehicle2,Vehicle3,Vehicle4,Vehicle5,Vehicle6,Vehicle7,Vehicle8,Vehicle9,Vehicle10] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]

				Vehicle1.Set_Goal([3   , 0.5, 0.5], 5, 0)       # goal,goal_strength 30, safety 0.001 for vortex method
				Vehicle2.Set_Goal([2.5 ,-3.5, 0.5], 5, 0)
				Vehicle3.Set_Goal([-1  , 3  , 0.5], 5, 0)
				Vehicle4.Set_Goal([-1  ,-3  , 0.5], 5, 0)
				Vehicle5.Set_Goal([-3  , 0  , 0.5], 5, 0)
				Vehicle6.Set_Goal([2   , 1  , 0.5], 5, 0)
				Vehicle7.Set_Goal([3   , 3.7, 0.5], 5, 0)
				Vehicle8.Set_Goal([-1  ,-1  , 0.5], 5, 0)
				Vehicle9.Set_Goal([2.2 ,-2  , 0.5], 5, 0)
				Vehicle10.Set_Goal([-0.5,-1  , 0.5], 5, 0)

				Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
				Vehicle2.Go_to_Goal(0.5,0,0,0)
				Vehicle3.Go_to_Goal(0.5,0,0,0)
				Vehicle4.Go_to_Goal(0.5,0,0,0)
				Vehicle5.Go_to_Goal(0.5,0,0,0)
				Vehicle6.Go_to_Goal(0.5,0,0,0)
				Vehicle7.Go_to_Goal(0.5,0,0,0)
				Vehicle8.Go_to_Goal(0.5,0,0,0)
				Vehicle9.Go_to_Goal(0.5,0,0,0)
				Vehicle10.Go_to_Goal(0.5,0,0,0)

				Vehicle1.Set_Position([-2  , 2, 0.5])
				Vehicle2.Set_Position([-2  , 1, 0.5])
				Vehicle3.Set_Position([0   ,-2, 0.5])
				Vehicle4.Set_Position([-3  , 3, 0.5])
				Vehicle5.Set_Position([3   , 0, 0.5])
				Vehicle6.Set_Position([-0.5,-3, 0.5])
				Vehicle7.Set_Position([-2  , 3, 0.5])
				Vehicle8.Set_Position([-3  ,-3, 0.5])
				Vehicle9.Set_Position([3.8 , 2, 0.5])
				Vehicle10.Set_Position([1  , 2, 0.5])
			elif case_no == 131:
				Vehicle1 = Vehicle("V1",0,0.75)            # Vehicle ID, Source_strength
				Vehicle2 = Vehicle("V2",0,0.75)
				Vehicle3 = Vehicle("V3",0,0.75)
				Vehicle4 = Vehicle("V4",0,0.75)
				Vehicle5 = Vehicle("V5",0,0.75)


				Vehicle_list = [Vehicle1,Vehicle2,Vehicle3,Vehicle4,Vehicle5] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]

				Vehicle1.Set_Goal([-2  ,  3, 0.5], 5, 0)       # goal,goal_strength 30, safety 0.001 for vortex method
				Vehicle2.Set_Goal([ 3  ,  -0.2, 0.5], 5, 0)
				Vehicle3.Set_Goal([-3  ,  0.5, 0.5], 5, 0)
				Vehicle4.Set_Goal([ 3  ,3.5, 0.5], 5, 0)
				Vehicle5.Set_Goal([-0.5 , -3, 0.5], 5, 0)



				Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
				Vehicle2.Go_to_Goal(0.5,0,0,0)
				Vehicle3.Go_to_Goal(0.5,0,0,0)
				Vehicle4.Go_to_Goal(0.5,0,0,0)
				Vehicle5.Go_to_Goal(0.5,0,0,0)



				Vehicle1.Set_Position([-0.5 , -3, 0.5])
				Vehicle2.Set_Position([-2  ,  3, 0.5])
				Vehicle3.Set_Position([ 3  ,  -0.2, 0.5])
				Vehicle4.Set_Position([-3  , 0.5, 0.5])
				Vehicle5.Set_Position([ 3  ,3.5, 0.5])


		if generate == 'random':
			no_of_vehicles = case_no
			Vehicle_list = []
			for no in range(no_of_vehicles):
				Vehicle_list.append(self.SetRandomStartGoal(arenamap,"V" + str(no)))

		# self.Vehicle_list = Vehicle_list
		print('Arena Map for first arena')
		self.arena = ArenaMap(buildings=self.buildings)
		print('Arena Map for second arena')
		# self.arenaR = ArenaMap(buildings=self.buildings) # FIX ME , remove this ! 
		print('Arena Maps are ready !')

		for vehicle in self.Vehicle_list: # FIXME Veh and veh ... select a norm for naming... :(
			vehicle.vehicle_list = deepcopy(self.Vehicle_list)
			vehicle.arena = deepcopy(self.arena)  # FIXME are these copies a prblme ???

	
	def SetRandomStartGoal(self,arenamap,ID):
		loop = True
		while loop == True:
			goal_temp  = [round(random.uniform(-3.5, 3.5),1),round(random.uniform(-3.5, 3.5),1),0.5]
			start_temp = [round(random.uniform(-3.5, 3.5),1),round(random.uniform(-3.5, 3.5),1),0.5]
			d = ( (goal_temp[0]-start_temp[0])**2 + (goal_temp[1]-start_temp[1])**2 )**0.5
			if d > 1:
				for i in range(len(arenamap.buildings) ):
					x = arenamap.buildings[i].position[0]
					y = arenamap.buildings[i].position[1]
					r = arenamap.buildings[i].position[2]
					d_goal  = ( (x-goal_temp[0])**2  + (y-goal_temp[1])**2 )**0.5
					d_start = ( (x-start_temp[0])**2 + (y-start_temp[1])**2 )**0.5
					if d_goal < r*2:
						break
					elif d_start < r*2:
						break
					if i == len(arenamap.buildings)-1:
						goal_position  = goal_temp
						start_position = start_temp
						loop = False
		vs = round(random.uniform(0, 0.5),2)
		Vehicle_ = Vehicle(ID,vs,0.75)
		Vehicle_.Set_Goal(goal_position, 5, 0.0000)
		Vehicle_.Set_Position(start_position)
		Vehicle_.Go_to_Goal(0.5,0,0,0)
		return Vehicle_

            # if version == 0:   # Dubai Map
            #     self.buildings = [Building([[55.1477081, 25.0890699, 50 ],[ 55.1475319, 25.0888817, 50 ],[ 55.1472176, 25.0891230, 50 ],[ 55.1472887, 25.0892549, 50],[55.1473938, 25.0893113, 50]]),
            #                                         Building([[55.1481917, 25.0895323, 87 ],[ 55.1479193, 25.0892520, 87 ],[ 55.1476012, 25.0895056, 87 ],[ 55.1478737, 25.0897859, 87]]),
            #                                         Building([[55.1486038, 25.0899385, 53 ],[ 55.1483608, 25.0896681, 53 ],[ 55.1480185, 25.0899204, 53 ],[ 55.1482615, 25.0901908, 53]]),
            #                                         Building([[55.1490795, 25.0905518, 82 ],[ 55.1488245, 25.0902731, 82 ],[ 55.1485369, 25.0904890, 82 ],[ 55.1487919, 25.0907677, 82]]),
            #                                         Building([[55.1494092, 25.0909286, 54 ],[ 55.1493893, 25.0908353, 54 ],[ 55.1493303, 25.0907662, 54 ],[ 55.1492275, 25.0907240, 54],[ 55.1491268, 25.0907304, 54],[ 55.1490341, 25.0907831, 54],[ 55.1489856, 25.0908571, 54],[ 55.1489748, 25.0909186, 54],[ 55.1489901, 25.0909906, 54],[ 55.1490319, 25.0910511, 54],[ 55.1491055, 25.0910987, 54],[ 55.1491786, 25.0911146, 54],[ 55.1492562, 25.0911063, 54],[ 55.1493356, 25.0910661, 54],[ 55.1493858, 25.0910076, 54]]),
            #                                         Building([[55.1485317, 25.0885948, 73 ],[ 55.1482686, 25.0883259, 73 ],[ 55.1479657, 25.0885690, 73 ],[ 55.1482288, 25.0888379, 73]]),
            #                                         Building([[55.1489093, 25.0890013, 101],[ 55.1486436, 25.0887191, 101],[ 55.1483558, 25.0889413, 101],[ 55.1486214, 25.0892235, 101]]),
            #                                         Building([[55.1492667, 25.0894081, 75 ],[ 55.1489991, 25.0891229, 75 ],[ 55.1487253, 25.0893337, 75 ],[ 55.1489928, 25.0896189, 75]]),
            #                                         Building([[55.1503024, 25.0903554, 45 ],[ 55.1499597, 25.0899895, 45 ],[ 55.1494921, 25.0903445, 45 ],[ 55.1497901, 25.0906661, 45],[ 55.1498904, 25.0906734, 45]]),
            #                                         Building([[55.1494686, 25.0880107, 66 ],[ 55.1491916, 25.0877250, 66 ],[ 55.1490267, 25.0877135, 66 ],[ 55.1486811, 25.0879760, 66],[ 55.1490748, 25.0883619, 66]]),
            #                                         Building([[55.1506663, 25.0900867, 47 ],[ 55.1503170, 25.0897181, 47 ],[ 55.1499784, 25.0899772, 47 ],[ 55.1503277, 25.0903494, 47]]),
            #                                         Building([[55.1510385, 25.0898037, 90 ],[ 55.1510457, 25.0896464, 90 ],[ 55.1507588, 25.0893517, 90 ],[ 55.1503401, 25.0896908, 90],[ 55.1506901, 25.0900624, 90]])]
            # # If we want to add other arenas:
            # elif version == 1:
            #     self.buildings = [Building([[-1.5, -2.5, 1], [-2.5, -3.5 , 1], [-3.5, -2.5, 1], [-2.5, -1.5, 1]]),
            #                                         Building([[ 3 ,  2, 1 ], [ 2.,  2, 1 ] ,[ 2.,  3, 1 ],[ 3.,  3, 1 ]]),
            #                                         Building([[ 3.,  -1, 1 ], [ 2., -2, 1 ] ,[ 1., -2, 1 ],[ 1.,  -1, 1 ],[ 2, 0, 1 ],[ 3., 0, 1 ]]),
            #                                         #Building([[ 4.1 , -3.9, 1 ], [ 4, -3.9, 1 ] ,[  4,  3.9, 1 ],[  4.1,  3.9, 1 ]]),
            #                                         #Building([[ 3.9 , -4.1, 1 ], [ -3.9, -4.1, 1 ] ,[ -3.9,  -4, 1 ],[  3.9,  -4, 1 ]]),
            #                                         #Building([[ 3.9 , 4, 1 ], [ -3.9, 4, 1 ] ,[ -3.9,  4.1, 1 ],[  3.9,  4.1, 1 ]]),
            #                                         #Building([[ -4 , -3.9, 1 ], [ -4.1, -3.9, 1 ] ,[  -4.1,  3.9, 1 ],[  -4,  3.9, 1 ]]),
            #                                         Building([[0.0, 1.0, 1], [-0.293, 0.293, 1], [-1.0, 0.0, 1], [-1.707, 0.293, 1], [-2.0, 1.0, 1], [-1.707, 1.707, 1], [-1.0, 2.0, 1], [-0.293, 1.707, 1]]),
            #                                         Building([[-2.0, 3.0, 1], [-2.5, 2.134, 1], [-3.5, 2.134, 1], [-4.0, 3.0, 1], [-3.5, 3.866, 1], [-2.5, 3.866, 1]]) ]

            # elif version == 2:
            #     self.buildings = [Building([[0.3, 1.0, 2], [0.05, 0.567, 2], [-0.45, 0.567, 2], [-0.7, 1.0, 2], [-0.45, 1.433, 2], [0.05, 1.433, 2]]),
            #                                         Building([[0.3, 3.0, 1.5], [0.05, 2.567, 1.5], [-0.45, 2.567, 1.5], [-0.7, 3.0, 1.5], [-0.45, 3.433, 1.5], [0.05, 3.433, 1.5]]),
            #                                         Building([[1.7, 2.0, 1.2], [1.45, 1.567, 1.2], [0.95, 1.567, 1.2], [0.7, 2.0, 1.2], [0.95, 2.433, 1.2], [1.45, 2.433, 1.2]]),
            #                                         Building([[-1.07, -0.2, 1.5], [-1.5, -0.63, 1.5], [-1.93, -0.2, 1.5], [-1.5, 0.23, 1.5]]),
            #                                         Building([[-1.07, -2.0, 1.5], [-1.5, -2.43, 1.5], [-1.93, -2.0, 1.5], [-1.5, -1.57, 1.5]]),
            #                                         Building([[-2.57, -1.0, 1.5], [-3.0, -1.43, 1.5], [-3.43, -1.0, 1.5], [-3.0, -0.57, 1.5]]),
            #                                         Building([[-2.57, 1.0, 1.5], [-3.0, 0.57, 1.5], [-3.43, 1.0, 1.5], [-3.0, 1.43, 1.5]]),
            #                                         Building([[1, -2.1, 1.2], [0.5, -2.1, 1.2], [0.5, -1, 1.2], [1, -0.6, 1.2]]),
            #                                         Building([[2.5, -2.1, 1.2], [2, -2.1, 1.2], [2, -0.6, 1.2], [2.5, -1, 1.2]])]
            # elif version == 3:
            #     self.buildings = [Building([[1.7, 2.0, 2], [1.45, 1.567, 2], [0.95, 1.567, 2], [0.7, 2.0, 2], [0.95, 2.433, 2], [1.45, 2.433, 2]])]
            # elif version == 4:
            #     self.buildings = [Building([[0.3, 1.0, 2], [0.05, 0.567, 2], [-0.45, 0.567, 2], [-0.7, 1.0, 2], [-0.45, 1.433, 2], [0.05, 1.433, 2]]),
            #                                         Building([[0.3, 3.0, 2], [0.05, 2.567, 2], [-0.45, 2.567, 2], [-0.7, 3.0, 2], [-0.45, 3.433, 2], [0.05, 3.433, 2]]),
            #                                         Building([[1.7, 2.0, 2], [1.45, 1.567, 2], [0.95, 1.567, 2], [0.7, 2.0, 2], [0.95, 2.433, 2], [1.45, 2.433, 2]])]
            # elif version == 41:
            #     self.buildings = [Building([[0.3, 1.0, 2], [0.05, 0.567, 2], [-0.45, 0.567, 2], [-0.7, 1.0, 2], [-0.45, 1.433, 2], [0.05, 1.433, 2]]),
            #                                         Building([[1.7, 2.0, 2], [1.45, 1.567, 2], [0.95, 1.567, 2], [0.7, 2.0, 2], [0.95, 2.433, 2], [1.45, 2.433, 2]])]
            # elif version == 5:
            #     self.buildings = [Building([[-3.9, 3.9, 2], [-4.1, 3.9, 2], [-4.1, 4.1, 2], [-3.9, 4.1, 2]]),
            #                                         Building([[4.1, 3.9, 2], [3.9, 3.9, 2], [3.9, 4.1, 2], [4.1, 4.1, 2]]),
            #                                         Building([[4.1, -4.1, 2], [3.9, -4.1, 2], [3.9, -3.9, 2], [4.1, -3.9, 2]]),
            #                                         Building([[-3.9, -4.1, 2], [-4.1, -4.1, 2], [-4.1, -3.9, 2], [-3.9, -3.9, 2]])]
            # elif version == 6:
            #     self.buildings = [Building([[3.0, 2.0, 1.2], [2.75, 1.567, 1.2], [2.25, 1.567, 1.2], [2.0, 2.0, 1.2], [2.25, 2.433, 1.2], [2.75, 2.433, 1.2]]), #AddCircularBuilding( 2.5, 2, 6, 0.5, 1.2, angle = 0)
            #                                         Building([[1.0, 3.0, 1.5], [0.75, 2.567, 1.5], [0.25, 2.567, 1.5], [0.0, 3.0, 1.5], [0.25, 3.433, 1.5], [0.75, 3.433, 1.5]]), #AddCircularBuilding( 0.5, 3, 6, 0.5, 1.5, angle = 0)
            #                                         Building([[1.0, 0.5, 2], [0.75, 0.067, 2], [0.25, 0.067, 2], [0.0, 0.5, 2], [0.25, 0.933, 2], [0.75, 0.933, 2]]), #AddCircularBuilding( 0.5, 0.5, 6, 0.5, 2, angle = 0)
            #                                         Building([[-2.65, 1.5, 1.5], [-3.0, 1.15, 1.5], [-3.35, 1.5, 1.5], [-3.0, 1.85, 1.5]]), #AddCircularBuilding( -3, 1.5, 4, 0.35, 1.5, angle = 0)
            #                                         Building([[-2.65, -1.5, 1.5], [-3.0, -1.85, 1.5], [-3.35, -1.5, 1.5], [-3.0, -1.15, 1.5]]), #AddCircularBuilding( -3, -1.5, 4, 0.35, 1.5, angle = 0)
            #                                         Building([[-1.15, -0.2, 1.5], [-1.5, -0.55, 1.5], [-1.85, -0.2, 1.5], [-1.5, 0.15, 1.5]]), #AddCircularBuilding( -1.5, -0.2, 4, 0.35, 1.5, angle = 0)
            #                                         Building([[1.5, -2.5, 1.2], [1, -2.5, 1.2], [1, -1.4, 1.2], [1.5, -1, 1.2]]),
            #                                         Building([[3.5, -2.5, 1.2], [3, -2.5, 1.2], [3, -1, 1.2], [3.5, -1.4, 1.2]])]
            # elif version == 61:
            #     self.buildings = [Building([[1.0, 0.5, 2], [0.75, 0.067, 2], [0.25, 0.067, 2], [0.0, 0.5, 2], [0.25, 0.933, 2], [0.75, 0.933, 2]])]
            # elif version == 8:
            #     self.buildings = [Building([[20.0, 15.0, 40], [17.5, 10.67, 40], [12.5, 10.67, 40], [10.0, 15.0, 40], [12.5, 19.33, 40], [17.5, 19.33, 40]]), #Arena.AddCircularBuilding( 15, 15, 6, 5, 40, angle = 0)
            #                                         Building([[40.0, 27.0, 40], [46.062, 23.5, 40], [46.062, 16.5, 40], [40.0, 13.0, 40], [33.938, 16.5, 40], [33.938, 23.5, 40]]), #Arena.AddCircularBuilding( 40, 20, 6, 7, 40, angle = np.pi/2)
            #                                         Building([[31.0, 45.0, 40], [26.854, 39.294, 40], [20.146, 41.473, 40], [20.146, 48.527, 40], [26.854, 50.706, 40]]), #Arena.AddCircularBuilding( 25, 45, 5, 6, 40, angle = 0)
            #                                         Building([[12.828, 37.828, 40], [11.035, 31.136, 40], [6.136, 36.035, 40]]), #Arena.AddCircularBuilding( 10, 35, 3, 4, 40, angle = np.pi/4) 
            #                                         Building([[55.657, 45.657, 40], [55.657, 34.343, 40], [44.343, 34.343, 40], [44.343, 45.657, 40]])] #Arena.AddCircularBuilding( 50, 40, 4, 8, 40, angle = np.pi/4)
        