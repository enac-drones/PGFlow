from gflow.vehicle import Vehicle
import numpy as np


class Cases():
	def __init__(self,number,arenamap, generate = 'manual'):
		if generate == 'manual':
			version = number
			if version == 61:
				Vehicle1 = Vehicle("V1",0,0.5)             # Vehicle ID, Source_strength,safety
				Vehicle_list = [Vehicle1]

				Vehicle1.Set_Position([ -2, 0.5, 0.50])
				Vehicle1.Set_Goal([3, 0.5, 0.5], 5, 0 )       # goal,goal_strength 30, safety 0.001
				Vehicle1.Go_to_Goal(1.5, 0,0)               # altitude,AoAsgn,t_start,Vinfmag
			elif version == 31:
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
			elif version == 71:
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
			elif version == 72:
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
			elif version == 73:
				Vehicle1 = Vehicle("V1",0,0.5)            # Vehicle ID, Source_strength,safety
				Vehicle_list = [Vehicle1]

				Vehicle1.Set_Position([0  ,3, 0.50])
				Vehicle1.Set_Goal([2, 0, 0.5], 5, 0)       # goal,goal_strength 30, safety 0.001
				Vehicle1.Go_to_Goal(1.5, 0,0)              # altitude,AoAsgn,t_start,Vinfmag
			elif version == 74:
				Vehicle1 = Vehicle("V1",0,0.5)             # Vehicle ID, Source_strength,safety
				Vehicle_list = [Vehicle1]

				Vehicle1.Set_Position([ -2, 2, 0.50])
				Vehicle1.Set_Goal([3, 2, 0.5], 5, 0 )       # goal,goal_strength 30, safety 0.001
				Vehicle1.Go_to_Goal(1.5, 0,0)               # altitude,AoAsgn,t_start,Vinfmag


			elif version == 0:
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
			elif version == 8:
				Vehicle1 = Vehicle("V1",0,0.85)            # Vehicle ID, Source_strength, im 0.85 veh 0.95
				Vehicle2 = Vehicle("V2",2,0.85)

				Vehicle_list = [Vehicle1,Vehicle2] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]

				Vehicle1.Set_Goal([1.5, -3, 0.5], 5, 0)       # for arena 6  [1.5, -3.3, 0.5]
				Vehicle2.Set_Goal([1.50001, -2, 0.5] , 5, 0)   # for arena 6 [2.0001, -2.3, 0.5]

				Vehicle1.Go_to_Goal(0.5,-np.pi/2,0,0.5)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
				Vehicle2.Go_to_Goal(0.5,0,0,0)

				Vehicle1.Set_Position([2, 1.5, 0.50])   #for arena 6 [2.5, 0.5, 0.50]
				Vehicle2.Set_Position([1.5, -2 , 0.5])     #for arena 6 [2, -2.3 , 0.5]
			elif version == 117:
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
			elif version == 1171:
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
			elif version == 11:
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
			elif version == 12:
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
			elif version == 121:
				Vehicle1 = Vehicle("V1",0,0.85)            # Vehicle ID, Source_strength imaginary source = 0.75
				Vehicle_list = [Vehicle1] #, Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]
				Vehicle1.Set_Position([-2, 3 , 0.5])
				Vehicle1.Set_Goal([2.5, -3.5, 0.5], 5, 0.0000)       # goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
				Vehicle1.Go_to_Goal(0.5,0,0,0)         # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
			elif version == 13:
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
			elif version == 131:
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
			no_of_vehicles = number
			Vehicle_list = []
			for no in range(no_of_vehicles):
				Vehicle_list.append(self.SetRandomStartGoal(arenamap,"V" + str(no)))
		self.Vehicle_list = Vehicle_list

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
