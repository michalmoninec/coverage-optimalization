from shapely.geometry import Polygon, LineString, MultiPoint, Point, mapping
from shapely.ops import split, snap
import math
import numpy as np

def intersect(arr):
    # print(f"input arr {arr}")
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
        self.paralels_fake = []
        inner = []

        for k in range(len(inner_i)):
            inner.append(Polygon(inner_i[k]))
        
        self.main(width, inner, angle)
        
        # print(f"this is angle: {angle}")

    def main(self, width, inner, angle):
        outer = self.outer
        minx, miny, maxx, maxy = outer.bounds
        paralels = []

        pi = math.pi
        angle_rad = angle * pi / 180

        

        if angle !=0 and angle !=180:
            shift = (maxy-miny)/(math.tan(angle_rad))

            if angle>90:
                start_shift = shift
                shift_max = -shift     
            else:
                start_shift = 0
                shift_max = shift

            end_border = maxx+shift_max
            iter_coord = minx + start_shift
            dir_addition = width/math.sin(angle_rad)
        else:
            shift = 0
            start_shift = 0
            end_border = maxy
            iter_coord = miny
            dir_addition = width
            # print("mel bych kreslit vodorovne")

        

        # print(f"shift {shift}")
        # print(f"dir_addiion {dir_addition}")
        



        while iter_coord < (end_border):
            if (angle == 0) or (angle == 180):
                line = LineString([(minx,iter_coord),(maxx,iter_coord)])
            else:
                line = LineString([(iter_coord-shift,miny),(iter_coord,maxy)])

            if line.intersects(outer):
                # intersected_points = None
                intersected_points = []

                #oriznuti o vnejsi polygon - funguje
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

                for point in intersected_points:
                    # print(f"isolated point: {point}")
                    self.paralels_fake.append(intersect(point))

                # print(f"intersected points: {np.round(intersected_points,5)}")
                # intersected_points = np.round(intersected_points,5)

                #pokud dojde k orezani, vytvori se orezana primka
                if len(intersected_points)>0:
                    for intersected_points_iter in intersected_points:
                        
                        #vytvoreni orezane primky
                        croped_line = LineString(intersected_points_iter)
                        # print(f"crope_line round: {croped_line.coords}")
                        intersected = False
                        points = None
                        ppoints = []

                        #pro kazdy vnitrni tvar se zjisti jestli jej protina a jakym zpusobem jej protina
                        for i in range(len(inner)):
                            if croped_line.intersects(inner[i]) and croped_line.intersection(inner[i]).geom_type=="LineString":
                                # print('Protina jednou primkou')
                                intersected = True
                                intersection = list(croped_line.intersection(inner[i]).coords)
                                # print(f"intersection of simple line string: {intersection}")
                                for k in range(len(intersection)):
                                    ppoints.append(intersection[k])

                                
                            if croped_line.intersects(inner[i]) and croped_line.intersection(inner[i]).geom_type=="MultiLineString":
                                # print(f"prubehove cislo: {prubeh}")
                                # print('booha fucking zooha')
                                # print('Protina multiline primkou.')
                                intersected = True
                                intersection = []
                                # print(f"double intersection with inner: {croped_line.intersection(inner[i])}")
                                for item in croped_line.intersection(inner[i]):
                                    intersection.append(list(item.coords))
                                # print(f"intersection of multilinestring: {intersection}")

                                for k in range(len(intersection)):
                                    for m in range(len(intersection[k])):
                                        ppoints.append(intersection[k][m])
                            
                        # print(f"poiints before multipoint adjustment: {ppoints}")
                        # # ppoints = np.round(ppoints, 5)
                        points = MultiPoint(ppoints)
                        # print(f"pocet bodu o ktere se to ma orezat: {len(points)}")
                        
                        # print(f"points looks: {points}")
                        # print(f"points looks: {ppoints}")
                        # print(f"point after adjustment: {points}")
                        # print(f"multipoints point looks like this: {points}")


                        tolerance = 0.000000001
                        # tolerance = 0.0122141514
                        # 0122141514
                        croped_line = snap(croped_line, points, tolerance)
                                
                        if intersected:
                            

                            # print(f"points to split the line> {points}")
                            splitted = split(croped_line, points)
                            # print(f"splitted: {splitted}")
                            # print(f"cropped: {croped_line}")
                            # print(f"protina line bod? {croped_line.intersects(points[0])}")
                            # print(f"vzdalenost bodu od primky: {croped_line.distance(points[0])}")
                            # print(f"splitted object: {splitted}")
                            # print(len(splitted))
                            # print(f"pocet rozdelenych car: {len(splitted)}")
                            # print(f"lenght of splitted lines: {len(splitted)}")
                            # print("----------------------------------")
                            # print(f"number of lines: {len(splitted)}")

                            for index, lin in enumerate(splitted):
                                # print(f"index of lin:{index}")
                                
                                contains = False
                                

                                for i in range (len(inner)):
                                    # if lin.intersects(inner[i]) and len(lin.intersection(inner[i]).coords)>1:
                                    # print(f"type of intersection: {lin.intersection(inner[i])}")
                                    # print(f"intersection with {i}? {lin.intersects(inner[i])} and type {(lin.intersection(inner[i])).geom_type} ")
                                    if lin.intersects(inner[i]) and ((lin.intersection(inner[i])).geom_type == 'LineString' or 'MultiLineString'):
                                        # print(f"distance of two colision points: {lin.intersection(inner[i]).length}")
                                        # print('Mel bych vynechat tuto line.')
                                        if lin.intersection(inner[i]).length > 0.00001:
                                            contains = True 
                                        
                                    else:
                                        # print('dostal jsem se tady a nic nevykreslim')
                                        # print(f"intersection? : {lin.intersects(inner[i])}")
                                        # contains = False
                                        pass
                                # print(f"Should I delete this line? : {contains}")

                                if contains == False:
                                    # print(f'dalsi : {lin.coords}')
                                    push_data = []
                                    for point in lin.coords:
                                        if point not in push_data:
                                            push_data.append(point)

                                    # print(f"input data {list(lin.coords)}")
                                    # print(f"upravene data: {push_data}")
                                    paralels.append(intersect(push_data))
                                    self.paralels_raw.append(list(lin.coords))
                        else:
                            # print(f"another onee: {intersected_points}")
                            paralels.append(intersect(intersected_points_iter))
                            self.paralels_raw.append(intersected_points_iter)



            iter_coord += dir_addition
            # prubeh+=1
        self.paralels = paralels
        # print(f"paralels: {self.paralels}")
        # self.paralels_fake = paralels_fake

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


        
