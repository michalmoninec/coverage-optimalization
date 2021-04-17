from pyvisgraph import vis_graph
from shapely.geometry.polygon import Polygon
import xlwt
from xlwt import Workbook
from random import random, choices, shuffle, randint, randrange

import pyvisgraph as vg
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
# polygons = [[(706704.1057, 5528909.5638), (706713.0852, 5528909.3863), (706713.1019, 5528896.3983), (706700.6629, 5528896.2188), (706700.4269, 5528904.8689), (706704.0878, 5528905.0096), (706704.1057, 5528909.5638)], [(706734.0413, 5528903.8467), (706736.5461, 5528903.943), (706736.3574, 5528901.323), (706733.7448, 5528901.5212), (706734.0413, 5528903.8467)], [(706711.6391619823, 5528913.776144666), (706710.4848, 5528914.2878), (706711.6437, 5528914.2577), (706711.6391619823, 5528913.776144666)], [(706736.872, 5528910.5245), (706739.7707, 5528910.412), (706740.1718, 5528899.9767), (706737.1854, 5528899.8619), (706736.872, 5528910.5245)]]
polygons = [[(706704.1057, 5528909.5638), (706713.0852, 5528909.3863), (706713.1019, 5528896.3983), (706700.6629, 5528896.2188), (706700.4269, 5528904.8689), (706704.0878, 5528905.0096)], [(706734.0413, 5528903.8467), (706736.5461, 5528903.943), (706736.3574, 5528901.323), (706733.7448, 5528901.5212), (706734.0413, 5528903.8467)], [(706711.6391619823, 5528913.776144666), (706710.4848, 5528914.2878), (706711.6437, 5528914.2577), (706711.6391619823, 5528913.776144666)], [(706736.872, 5528910.5245), (706739.7707, 5528910.412), (706740.1718, 5528899.9767), (706737.1854, 5528899.8619), (706736.872, 5528910.5245)]]

polyg = polygons[0]
xx = [round(pol[0],2) for pol in polyg]
x_min = min(xx)
xx = [round(x-x_min,2) for x in xx]

yy = [round(pol[1],2) for pol in polyg]
y_min = min(yy)
yy = [round(y-y_min,2) for y in yy]

polys = []
for i in range(len(xx)):
    polys.append(vg.Point(xx[i],yy[i]))




# poly = [vg.Point(point[0],point[1]) for point in polyg]

graph = vg.VisGraph()
graph.build([polys])
edges = graph.visgraph.get_edges()

for edge in edges:
    plt.plot([edge.p1.x,edge.p2.x],[edge.p1.y,edge.p2.y])


x1, y1 = 706703.56, 5528907.71
x2, y2 = 706713.45, 5528898.50
# x2, y2 = 706715.45, 5528898.50
# x2, y2 = 706700.15, 5528903.74

x1 = round(x1 - x_min, 2)
x2 = round(x2 - x_min, 2)

y1 = round(y1 - y_min, 2)
y2 = round(y2 - y_min, 2)


plt.plot([x1,x2],[y1,y2])
# plt.plot(x2,y2)


p1 = vg.Point(x1,y1)
p2 = vg.Point(x2,y2)
plt.show()
path = graph.shortest_path(p1,p2)
print(path)
