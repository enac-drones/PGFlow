import numpy as np
from numpy import linalg
import math
import matplotlib.pyplot as plt
import pyclipper
from shapely.geometry import Point, Polygon
from datetime import datetime
from itertools import compress

from panel_flow import Flow_Velocity_Calculation

import pdb

"""##Vehicles"""

def dynamics(X, t, U):
    '''  Dynamic model :
    Xdot   = X(k+1) - X(k)
    X(k+1) = AX(k)  + BU(k)
    where X : [PE,PN,PU,Vx,Vy,Vz] Elem R6
    U : [VdesE, VdesN, VdesU]
    X = X0 + V*t
    V = V0 + a*t
    '''
    k = 1.140
    A = np.array([[1.,  0.,  0.,  t,      0.,     0.    ],
                                [0.,  1.,  0.,  0.,     t,      0.    ],
                                [0.,  0.,  1.,  0.,     0.,     t     ],
                                [0.,  0.,  0.,  1.-k*t, 0.,     0.    ],
                                [0.,  0.,  0.,  0.,     1.-k*t, 0.    ],
                                [0.,  0.,  0.,  0.,     0.,     1.-k*t]])
    B = np.array([[0.,  0.,  0. ],
                                [0.,  0.,  0. ],
                                [0.,  0.,  0. ],
                                [k*t, 0.,  0. ],
                                [0.,  k*t, 0. ],
                                [0.,  0.,  k*t]])

    Xdot = A@X + B@U - X
    return Xdot
def curvature(x,y):
    dx  = np.gradient(x)
    ddx = np.gradient(dx)
    dy  = np.gradient(y)
    ddy = np.gradient(dy)
    k   = np.abs((dx*ddy - dy*ddx))/(dx*dx + dy*dy)**(3/2)
    return k
    
def line(p1, p2):
        A = (p1[1] - p2[1])
        B = (p2[0] - p1[0])
        C = (p1[0]*p2[1] - p2[0]*p1[1])
        return A, B, -C

def intersection(L1, L2):
        D  = L1[0] * L2[1] - L1[1] * L2[0]
        Dx = L1[2] * L2[1] - L1[1] * L2[2]
        Dy = L1[0] * L2[2] - L1[2] * L2[0]
        if D != 0:
                x = Dx / D
                y = Dy / D
                return True
        else:
                return False

class Vehicle():
    def __init__(self,ID,source_strength = 0, imag_source_strength = 0.75, correction_type = 'none'):
        self.t               = 0
        self.position        = np.zeros(3)
        self.desiredpos      = np.zeros(3)
        self.correction      = np.zeros(3)
        self.velocity        = np.zeros(3)
        self.goal            = np.zeros(3)
        self.source_strength = source_strength
        self.imag_source_strength = imag_source_strength
        self.gamma           = 0
        self.altitude_mask   = None
        self.ID              = ID
        self.path            = []
        self.state           = 0
        self.distance_to_destination = None
        self.velocitygain    = 1/50 # 1/300 or less for vortex method, 1/50 for hybrid
        self.velocity_desired = np.zeros(3)
        self.velocity_corrected = np.zeros(3)
        self.vel_err = np.zeros(3)
        self.correction_type = correction_type

    @property
    def arena(self):
        return self._arena
    @arena.setter
    def arena(self,arena):
        self._arena = arena

    @property
    def vehicle_list(self):
        return self._vehicle_list

    @vehicle_list.setter
    def vehicle_list(self,vehicle_list):
        self._vehicle_list = vehicle_list

    def Set_Position(self,pos):
        self.position = np.array(pos)
        self.path     = np.array(pos)
        # print('GOOOAAALLL : ', self.goal)
        if np.all(self.goal) != None:
            self.distance_to_destination = np.linalg.norm(np.array(self.goal)-np.array(self.position))
            if np.all(self.distance_to_destination) < 0.2:
                self.state = 1

    def Set_Velocity(self,vel):
        self.velocity = vel

    def Set_Desired_Velocity(self,vel, method='direct'):
        self.velocity_desired = vel
        self.correct_vel(method=method)


    def correct_vel(self, method='None'):

        if method == 'projection':
            #Projection Method
            wind = self.velocity - self.velocity_desired
            self.vel_err = self.vel_err - (wind - np.dot(wind, self.velocity_desired/np.linalg.norm(self.velocity_desired) ) * np.linalg.norm(self.velocity_desired) ) *(1./240.)
        elif method == 'direct':
            # err = self.velocity_desired - self.velocity
            self.vel_err = (self.velocity_desired - self.velocity)*(1./40.)
            # self.vel_err = (self.velocity_desired - self.velocity)
            # print(f' Vel err : {self.vel_err[0]:.3f}  {self.vel_err[1]:.3f}  {self.vel_err[2]:.3f}')
        else:
            self.vel_err = np.zeros(3)

        self.velocity_corrected = self.velocity_desired + self.vel_err
        self.velocity_corrected[2] = 0.
        # print(f' Wind              : {wind[0]:.3f}  {wind[1]:.3f}  {wind[2]:.3f}')
        # print(f' Projected Vel err : {self.vel_err[0]:.3f}  {self.vel_err[1]:.3f}  {self.vel_err[2]:.3f}')
        # print(f' Desired   Vel     : {self.velocity_desired[0]:.3f}  {self.velocity_desired[1]:.3f}  {self.velocity_desired[2]:.3f}')
        # print(f' Corrected Vel     : {self.velocity_corrected[0]:.3f}  {self.velocity_corrected[1]:.3f}  {self.velocity_corrected[2]:.3f}')
        # print('   ')
        # print('   ')
        # print('   ')

    def Set_Goal(self,goal,goal_strength,safety):
        self.goal          = np.array(goal) # or just goal...FIXME
        self.sink_strength = goal_strength
        self.safety = safety
        #self.aoa = np.arctan2(self.goal[1]-self.position[1],self.goal[0]-self.position[0]) # Do we still need this ? FIXME
        

    def Set_Next_Goal(self,goal, goal_strength=5):
        self.state         = 0
        self.goal          = goal
        # self.sink_strength = goal_strength NOT USED FOR NOW


    def Go_to_Goal(self, altitude = 1.5, AoAsgn = 0, t_start = 0, Vinfmag = 0):
        self.AoA = (np.arctan2(self.goal[1]-self.position[1],self.goal[0]-self.position[0])) + AoAsgn*np.pi/2
        

        '''
        print( " AoA "    +  str( self.AoA*180/np.pi ) )
        print( " goal "   +  str( self.goal ) )
        print( " pos "    +  str( self.position ) )
        print( " AoAsgn " +  str( AoAsgn ) )
        print( " arctan " +  str( (np.arctan2(self.goal[1]-self.position[1],self.goal[0]-self.position[0]))*180/np.pi ) )
        '''
        self.altitude = altitude
        self.Vinfmag = Vinfmag                                      # Cruise altitude
        self.V_inf    = np.array([self.Vinfmag*np.cos(self.AoA), self.Vinfmag*np.sin(self.AoA)]) # Freestream velocity. AoA is measured from horizontal axis, cw (+)tive
        self.t = t_start

    def Source_Points(self):
        v = self.position[:2]
        g = self.goal[:2]
        beta = np.pi/2 #2*np.pi/3
        d = 0.1
        R2 = np.array([[np.cos(beta), -np.sin(beta)],[np.sin(beta),np.cos(beta)]])
        R3 = np.array([[np.cos(-beta), -np.sin(-beta)],[np.sin(-beta),np.cos(-beta)]])
        p1 = ((g-v) / linalg.norm(g-v))*d
        p2 = np.matmul(R2,p1)
        p3 = np.matmul(R3,p1)
        p1 = v - p1
        p2 = v + p2
        p3 = v + p3      
        return p1, p2, p3

    def Update_Velocity(self,flow_vels,arenamap):
    # K is vehicle speed coefficient, a design parameter
        #flow_vels = flow_vels * self.velocitygain
        V_des = flow_vels
        mag = np.linalg.norm(V_des)
        V_des_unit = V_des/mag
        V_des_unit[2] = 0
        mag = np.clip(mag, 0., 1) #0.3 tello 0.5 pprz
        mag_converted = mag # This is Tellos max speed 30Km/h
        flow_vels2 = V_des_unit * mag_converted
        flow_vels2 = flow_vels2 * self.velocitygain
        prevpos = self.position
        self.desiredpos = self.position + np.array(flow_vels2)
        self.position   = self.position + np.array(flow_vels2)  + np.array([arenamap.wind[0], arenamap.wind[1], 0]) +  self.correction
        dif1 = self.position  -prevpos
        dif2 = self.desiredpos-prevpos
        dif3 = self.position  -self.desiredpos
        if self.correction_type == 'none':
            self.correction      = np.array([0,0,0])
        elif self.correction_type == 'all':
            self.correction = self.desiredpos-self.position + self.correction
        elif self.correction_type == 'project':
            self.correction = -(dif3 - np.dot(dif3,dif2/np.linalg.norm(dif2))*np.linalg.norm(dif2) ) + self.correction
        self.path = np.vstack(( self.path,self.position ))
        if np.linalg.norm(self.goal-self.position) < 0.2: #0.1 for 2d
            self.state = 1
        return self.position

    def Update_Position(self):
        self.position = self.Velocity_Calculate(flow_vels)
    

    def propagate_future_path(self,  maglist ,dyn=dynamics, t0=0., dt=0.02, hor = 2.4,reset_position=True, set_best_state=True):
        Xe           = np.hstack([self.position,self.velocity])
        time_horizon = np.arange(t0 + dt, t0 + hor, dt)
        vinfmag_list = maglist
        #vinfmag_list = [0.05, 0.025,  0. ,  -0.025, -0.05]
        #vinfmag_list = [0.05, 0.025, 0.01, 0. , -0.01, -0.025, -0.05]
        path         = np.zeros((len(vinfmag_list),len(time_horizon),6))

#   vinfmag_list = [0.2, 0.1, 0.05, 0. , -0.05, -0.1, -0.2]
        for k,vinfmag_ in enumerate(vinfmag_list):
            X0 = Xe.copy()
            ti = t0
            self.Vinfmag = np.abs(vinfmag_)
            for i, t_ in enumerate(time_horizon):
                self.AoA   = (np.arctan2(self.goal[1]-X0[1],self.goal[0]-X0[0])) + np.sign(vinfmag_)*np.pi/2
                self.V_inf = np.array([self.Vinfmag*np.cos(self.AoA), self.Vinfmag*np.sin(self.AoA)])
                # FIX ME : This will only work because we have only one vehicle...
                flow_vels = Flow_Velocity_Calculation(self._vehicle_list, self._arena, method = 'Vortex')
                V_des = flow_vels[0]
                mag = np.linalg.norm(V_des)
                V_des_unit = V_des/mag
                V_des_unit[2] = 0
                mag = np.clip(mag, 0., 1) #0.3 tello 0.5 pprz
                flow_vels2 = V_des_unit * mag
                U = flow_vels2 #* self.velocitygain
                X = scipy.integrate.odeint(dyn, X0, [ti, t_], args=(U,))
                X0 = X[1].copy()
                ti = t_
                path[k,i]     = X[1][:6] # Recording position and velocity to the path
                self.position = X[1][:3]
                self.velocity = X[1][3:6]
        if reset_position:
            self.position[:] = Xe[:3]
            self.velocity[:] = Xe[3:]
        if set_best_state:
            best = np.argmin([np.sum(curvature(path[i, 30:, 0],path[i, 30:, 1])) for i in range(len(vinfmag_list))])
            self.position[:] = Xe[:3]
            self.velocity[:] = Xe[3:]
            '''
            self.position = path[best,-1, :3]
            self.velocity = path[best,-1, 3:6]
            '''
        return path

    def propagate_simple_path(self, vinfmag ,dyn=dynamics, t0=0., dt=0.5, hor = 3.2,reset_position=True):
        Xe           = np.hstack([self.position,self.velocity])
        time_horizon = np.arange(t0 + dt, t0 + hor, dt)
        path         = np.zeros((len(time_horizon),6))
        X0 = Xe.copy()
        ti = t0
        flow_vels = Flow_Velocity_Calculation(self._vehicle_list, self._arena, method = 'Source')
        V_des = flow_vels[0]
        mag = np.linalg.norm(V_des)
        V_des_unit = V_des/mag
        V_des_unit[2] = 0
        mag = np.clip(mag, 0., 1) #0.3 tello 0.5 pprz
        flow_vels2 = V_des_unit * mag
        U = flow_vels2 #* self.velocitygain
        for i, t_ in enumerate(time_horizon):
            # FIX ME : This will only work because we have only one vehicle...
            X = X0[:3] + U*dt #scipy.integrate.odeint(dyn, X0, [ti, t_], args=(U,))
            X0 = X.copy()
            ti = t_
            path[i,:]     = np.hstack([X,U]) # Recording position and velocity to the path
        if reset_position:
            self.position[:] = Xe[:3]
            self.velocity[:] = Xe[3:]
        future_line = line((path[0,:2]),(path[-1,:2]))  
        for building in self._arena.buildings:
            vertice_list = np.vstack((building.vertices, building.vertices[0]))
            for vert in range(building.vertices.shape[0]-1):
                polygon_line = line((vertice_list[vert]),(vertice_list[vert+1]))      
                if intersection(future_line , polygon_line) == True:
                    vinfmag = vinfmag
                elif intersection(future_line , polygon_line) == False:
                    vinfmag = 0
        # print('For vehicle ', str('Best'), 'Best V_inf is: ', str(vinfmag))
        self.Go_to_Goal(AoAsgn = np.sign(vinfmag), Vinfmag = np.abs(vinfmag))
        return path#, vinfmag
