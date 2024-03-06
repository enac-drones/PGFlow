from gflow.building import Building
import time
b = Building([[-1,-1,0],[-1,1,0],[1,1,0],[1,-1,0]])     

t = time.perf_counter()
for i in range(11):
    b.contains_point((0,0))

print(time.perf_counter()-t)

