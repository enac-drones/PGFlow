from gflow.building import Building
import time
from shapely.geometry import Polygon as Ps
from shapely.geometry import Point
from matplotlib.patches import Polygon as Pm
import numpy as np
import gflow.building
from numpy.typing import ArrayLike
print(gflow.building.__file__)

verts = np.array([[ 4.05    , -1.135656,  1.2     ],
       [ 3.073492, -0.35445 ,  1.2     ],
       [ 2.45    , -0.654116,  1.2     ],
       [ 2.45    , -3.05    ,  1.2     ],
       [ 4.05    , -3.05    ,  1.2     ]])


# b = Building([[-1,-1,0],[-1,1,0],[1,1,0],[1,-1,0]]) 
b = Building(verts)    

verts = b.vertices[...,:2]
# bs = Ps(verts)
# bm = Pm(verts)

p = np.array([ 3., -3.])

print(b.contains_point(p))
print(b.mplPoly.contains_point(p, radius=0))

def contains_point(point:ArrayLike)->bool:
        '''Checks if a point lies within the building.
        Faster with matplotlib than shapely'''
        print(f"{point=},\n {verts=}")
        print(Pm(verts[:,:2]).contains_point(point, radius=0))

        return Pm(verts[:,:2]).contains_point(point, radius=0)

print(contains_point(p))