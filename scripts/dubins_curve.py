
from shapely.geometry.base import JOIN_STYLE
from shapely.geometry.polygon import LinearRing, LineString
import matplotlib.pyplot as plt

points = [[0,0],[0,3],[1,3],[1,0.1]]
points = points[::-1]
line_init = LineString(points)

# line = line.buffer(0.5, join_style=1).buffer(-0.4,join_style=1)
# line = line.parallel_offset(-0.25, "left")
line = line_init.parallel_offset(0.49, "left")
line2 = LineString(line.coords)
line2 = line2.parallel_offset(0.49,'right')
# line2 = line.parallel_offset()
print(f'line looks: {line}')
# line = line.parallel_offset(0.25)

# print(f'line looks: {line}')

x = []
y = []
xx=[]
yy=[]

for point in list(line2.coords):
    x.append(point[0])
    y.append(point[1])

for point in list(line_init.coords):
    xx.append(point[0])
    yy.append(point[1])

plt.plot(x,y)
plt.plot(xx,yy)
plt.show()

