from src.building import Building
from src.vehicle import Vehicle
from src.cases import Case, Cases
buildings = [
                    Building(
                        [
                            [3.0, 2.0, 1.2],
                            [2.75, 1.567, 1.2],
                            [2.25, 1.567, 1.2],
                            [2.0, 2.0, 1.2],
                            [2.25, 2.433, 1.2],
                            [2.75, 2.433, 1.2],
                        ]
                    ),  # AddCircularBuilding( 2.5, 2, 6, 0.5, 1.2, angle = 0)
                    Building(
                        [
                            [1.0, 3.0, 1.5],
                            [0.75, 2.567, 1.5],
                            [0.25, 2.567, 1.5],
                            [0.0, 3.0, 1.5],
                            [0.25, 3.433, 1.5],
                            [0.75, 3.433, 1.5],
                        ]
                    ),  # AddCircularBuilding( 0.5, 3, 6, 0.5, 1.5, angle = 0)
                    Building(
                        [
                            [1.0, 0.5, 2],
                            [0.75, 0.067, 2],
                            [0.25, 0.067, 2],
                            [0.0, 0.5, 2],
                            [0.25, 0.933, 2],
                            [0.75, 0.933, 2],
                        ]
                    ),  # AddCircularBuilding( 0.5, 0.5, 6, 0.5, 2, angle = 0)
                    Building(
                        [
                            [-2.65, 1.5, 1.5],
                            [-3.0, 1.15, 1.5],
                            [-3.35, 1.5, 1.5],
                            [-3.0, 1.85, 1.5],
                        ]
                    ),  # AddCircularBuilding( -3, 1.5, 4, 0.35, 1.5, angle = 0)
                    Building(
                        [
                            [-2.65, -1.5, 1.5],
                            [-3.0, -1.85, 1.5],
                            [-3.35, -1.5, 1.5],
                            [-3.0, -1.15, 1.5],
                        ]
                    ),  # AddCircularBuilding( -3, -1.5, 4, 0.35, 1.5, angle = 0)
                    Building(
                        [
                            [-1.15, -0.2, 1.5],
                            [-1.5, -0.55, 1.5],
                            [-1.85, -0.2, 1.5],
                            [-1.5, 0.15, 1.5],
                        ]
                    ),  # AddCircularBuilding( -1.5, -0.2, 4, 0.35, 1.5, angle = 0)
                    Building(
                        [
                            [1.5, -2.5, 1.2],
                            [1, -2.5, 1.2],
                            [1, -1.4, 1.2],
                            [1.5, -1, 1.2],
                        ]
                    ),
                    Building(
                        [
                            [3.5, -2.5, 1.2],
                            [3, -2.5, 1.2],
                            [3, -1, 1.2],
                            [3.5, -1.4, 1.2],
                        ]
                    ),
                ]

Vehicle1 = Vehicle(
    "V1", 0.5, 0.5
)  # Vehicle ID, Source_strength imaginary source = 1.5
Vehicle2 = Vehicle("V2", 0.5, 0.5)
Vehicle3 = Vehicle("V3", 0.5, 0.5)

Vehicle1.Set_Goal(
    [-3, 0, 0.5], 5, 0.0001
)  # goal,goal_strength all 5, safety 0.001 for V1 safety = 0 when there are sources
Vehicle2.Set_Goal([2, 3.5, 0.5], 5, 0.0001)
Vehicle3.Set_Goal([2, 1, 0.5], 5, 0.0001)

Vehicle1.Go_to_Goal(
    0.5, 0, 0, 0
)  # altitude,AoA,t_start,Vinf=0.5,0.5,1.5
Vehicle2.Go_to_Goal(
    0.5, 0, 0, 0
)  # np.arctan2(3.5+1,1.5+0.5) = 1.1525719 rad
Vehicle3.Go_to_Goal(0.5, 0, 0, 0)

Vehicle1.Set_Position([3, 1, 0.5])
Vehicle2.Set_Position([-1, -3, 0.5])
Vehicle3.Set_Position([-3, 3, 0.5])
vehicle_list = [
    Vehicle1,
    Vehicle2,
    Vehicle3,
]  # , Vehicle2, Vehicle3] # , Vehicle2, Vehicle3]


case = Case(name="simple_example")
case.buildings = buildings
case.vehicle_list = vehicle_list
generator = Cases()
generator.add_case(case)
