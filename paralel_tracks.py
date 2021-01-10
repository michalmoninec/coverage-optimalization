from shapely.geometry import Polygon, LineString, MultiPoint, Point
from shapely.ops import split

def intersect(arr):
    res = []
    for i in range(len(arr)):
        res.append((arr[0][i],arr[1][i]))
    return res

class ParalelTracks():
    def __init__(self, outer, inner_i, width) -> None:
        super().__init__()
        self.outer = Polygon(outer)
        self.paralels = []
        inner = []

        for k in range(len(inner_i)):
            inner_2 = []
            for i in range(len(inner_i[k].x)):
                inner_2.append((inner_i[k].x[i],inner_i[k].y[i]))
            inner.append(Polygon(inner_2))
        
        self.main(width, inner)

    def main(self, width, inner):
        outer = self.outer
        minx, miny, maxx, maxy = outer.bounds
        paralels = []
        
        #TODO change to use minx in while loop
        x = minx

        while x < maxx:
            line = LineString([(x,miny),(x,maxy)])

            if line.intersects(outer):
                intersected_points = None

                if (line.intersection(outer).geom_type=="LineString"):
                    intersected_points = list(line.intersection(outer).coords)
                else:
                    intersected_points = []

                if len(intersected_points)>1:
                    croped_line = LineString(intersected_points)
                    intersected = False
                    points = None
                    ppoints = []

                    for i in range(len(inner)):
                        if croped_line.intersects(inner[i]):
                            intersected = True
                            intersection = list(croped_line.intersection(inner[i]).coords)
                            for k in range(len(intersection)):
                                ppoints.append(intersection[k])
                    points = MultiPoint(ppoints)
                            
                    if intersected:
                        splitted = split(croped_line, points)

                        for lin in splitted:
                            contains = False

                            for i in range (len(inner)):
                                if lin.intersects(inner[i]) and len(lin.intersection(inner[i]).coords)>1:
                                    contains = True
                                else:
                                    pass
                            if contains == False:
                                paralels.append(intersect(lin.coords))
                    else:
                        paralels.append(intersect(intersected_points))
            x+=width
        self.paralels = paralels


        
