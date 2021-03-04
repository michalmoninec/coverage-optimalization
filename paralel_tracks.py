from shapely.geometry import Polygon, LineString, MultiPoint, Point
from shapely.ops import split
import math

def intersect(arr):
    res = []
    for i in range(len(arr)):
        res.append((arr[0][i],arr[1][i]))
    return res

class UpperList():
    def __init__(self, index, point) -> None:
        super().__init__()
        self.index = index
        self.point = point
        self.cluster = None

class ParalelTracks():
    def __init__(self, outer, inner_i, width, angle) -> None:
        super().__init__()
        self.outer = Polygon(outer)
        self.paralels = []
        self.paralels_raw = []
        inner = []

        for k in range(len(inner_i)):
            inner.append(Polygon(inner_i[k]))
        
        self.main(width, inner, angle)
        
        print(f"this is angle: {angle}")

    def main(self, width, inner, angle):
        outer = self.outer
        minx, miny, maxx, maxy = outer.bounds
        paralels = []

        pi = math.pi
        angle_rad = angle * pi / 180

        if angle != 180:
            shift = (maxy-miny)/(math.tan(angle_rad))

        print(f"shift {shift}")

        print(f"angle in radians: {angle_rad}")
        

        x = minx
        prubeh = 0

        while x < (maxx+shift):
            line = LineString([(x-shift,miny),(x,maxy)])

            if line.intersects(outer):
                # intersected_points = None
                intersected_points = []

                if (line.intersection(outer).geom_type=="LineString"):
                    intersected_points.append(list(line.intersection(outer).coords))
                elif (line.intersection(outer).geom_type == 'MultiLineString'):
                    for item in line.intersection(outer):
                        intersected_points.append(list(item.coords))
                    # print(f"multiple intersections first item: {line.intersection(outer)[0]}")
                    # intersected_points = []
                else:
                    # print(f"Another type of intersection")
                    intersected_points = []

                if len(intersected_points)>0:
                    for intersected_points_iter in intersected_points:
                        # print(f"Iteration of intersected points: {intersected_points_iter}")

                        croped_line = LineString(intersected_points_iter)
                        intersected = False
                        points = None
                        ppoints = []

                        for i in range(len(inner)):
                            if croped_line.intersects(inner[i]) and croped_line.intersection(inner[i]).geom_type=="LineString":
                                intersected = True
                                intersection = list(croped_line.intersection(inner[i]).coords)
                                # print(f"intersection of simple line string: {intersection}")
                                for k in range(len(intersection)):
                                    ppoints.append(intersection[k])
                            # else:
                                
                            if croped_line.intersects(inner[i]) and croped_line.intersection(inner[i]).geom_type=="MultiLineString":
                                # print(f"prubehove cislo: {prubeh}")
                                # print('booha fucking zooha')
                                intersected = True
                                intersection = []
                                # print(f"double intersection with inner: {croped_line.intersection(inner[i])}")
                                for item in croped_line.intersection(inner[i]):
                                    intersection.append(list(item.coords))
                                # print(f"intersection of multilinestring: {intersection}")
                                for k in range(len(intersection)):
                                    for m in range(len(intersection[k])):
                                        ppoints.append(intersection[k][m])
                            
                        points = MultiPoint(ppoints)
                        # print(f"multipoints point looks like this: {points}")
                                
                        if intersected:
                            splitted = split(croped_line, points)
                            # print(len(splitted))
                            # print(f"lenght of splitted lines: {len(splitted)}")

                            for lin in splitted:
                                contains = False
                                

                                for i in range (len(inner)):
                                    # if lin.intersects(inner[i]) and len(lin.intersection(inner[i]).coords)>1:
                                    # print(f"type of intersection: {lin.intersection(inner[i])}")
                                    if lin.intersects(inner[i]) and (lin.intersection(inner[i]).geom_type=='LineString'):
                                        
                                        contains = True
                                    else:
                                        pass
                                if contains == False:
                                    # print(f'dalsi : {lin.coords}')
                                    paralels.append(intersect(lin.coords))
                                    self.paralels_raw.append(list(lin.coords))
                        else:
                            # print(f"another onee: {intersected_points}")
                            paralels.append(intersect(intersected_points_iter))
                            self.paralels_raw.append(intersected_points_iter)
            x+=width
            prubeh+=1
        self.paralels = paralels

    def getUpperPoints(self):
        paralels = self.paralels_raw
        upper = []

        for i in range(len(paralels)):
            paralel = paralels[i]
            y = []
            for k in range(len(paralel)):
                y.append(paralel[k][1])
            # print(f"Maximum je:  {max(y)} index je: {y.index(max(y))}")
            upper.append(UpperList(i,paralel[y.index(max(y))]))
        self.upper = upper
        # print(f"Number of paralel tracks: {len(paralels)}")


        
