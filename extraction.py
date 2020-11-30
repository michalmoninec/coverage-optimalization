from pykml import parser
from os import path
import re
import matplotlib.pyplot as plt
import matplotlib as mpl
import utm
import numpy as np
import math

kml_file = path.join('activity2.kml')

with open(kml_file) as f:
    doc = parser.parse(f).getroot()


# import souradnic ze zaznamu chozeni
coor = doc.Document.Placemark.LineString.coordinates.text

# import dat z mereni
# coor = doc.Document.Folder.Placemark.LineString.coordinates.text

newCoor = re.findall('[0-9.0-9,0-9.0-9,0-9.0-9]+', coor)

coorX = []
coorY = []

for i in range(len(newCoor)):
    c = newCoor[i].split(',')
    coorX.append(float(c[1]))
    coorY.append(float(c[0]))


X, Y, zn, zl = utm.from_latlon(np.array(coorX[:]), np.array(coorY[:]))

min_X = min(X)
max_X = max(X)
min_Y = min(Y)
max_Y = max(Y)

X = [M - min_X for M in X]
Y = [M - min_Y for M in Y]

# uzavreni tvaru
# X.append(X[0])
# Y.append(Y[0])


def distanceBetweenPoints(p1x, p1y, p2x, p2y):
    a = p2x - p1x
    b = p2y - p1y
    c = math.sqrt(a*a+b*b)
    return c


def getDistance(x, y):
    distance = 0

    for i in range(0, len(x)-1):
        distance += distanceBetweenPoints(X[i], Y[i], X[i+1], Y[i+1])
    return distance


print(getDistance(X, Y))

mpl.rcParams['toolbar'] = 'None'
plt.plot(X, Y)
plt.axis('equal')
plt.show()
