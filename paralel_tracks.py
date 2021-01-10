from shapely.geometry import Polygon, LineString, MultiPoint, Point, point
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
        # print(inner[0].x)
        inner = []
        

        for k in range(len(inner_i)):
            inner_2 = []
            for i in range(len(inner_i[k].x)):
                inner_2.append((inner_i[k].x[i],inner_i[k].y[i]))
            inner.append(Polygon(inner_2))
        
        # print(f"inner polygon whole chunk {inner}")
        # print(f"inner polygon {inner[0]}")

        # self.inner1 = Polygon(inner[0])
        
        # print(f"another class {outer}")
        # print(f"polygon bounds: {self.outer.bounds}")
        self.main(width, inner)

    def main(self, width, inner):
        outer = self.outer
        # print(f"another instance of inner: {inner}")

        # for i in range(len(inner)):
        #     inner.append(Polygon())
        # print(f'inner_input jak vypada: {inner}')
        # print(Polygon(inner[0]))

        minx, miny, maxx, maxy = outer.bounds

        paralels = []
        par_tracks = []
        x = minx
        # points = []

        while x < maxx:
            line = LineString([(x,miny),(x,maxy)])
            if line.intersects(outer):
                intersected_points = None
                if (line.intersection(outer).geom_type=="LineString"):
                    intersected_points = list(line.intersection(outer).coords)
                else:
                    intersected_points = []
                
                # print(f"len of intersected points {len(intersected_points)}")
                # print(f"jak vypada intersection: {intersected_points}")

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
                    # print(f"ppoints looks: {ppoints}")
                            
                    if intersected:
                        # print(f"shouldnt be None {points}")
                        # splitted = split(croped_line, points)
                        splitted = split(croped_line, points)
                        # print(f"splitted primky{splitted}")
                        for lin in splitted:
                            # print(f"jednotlive rozdelene primky: {lin}")
                            # print(f"len of lin {len(lin.coords)}")
                            # print(f"first coords of lin, X axis {lin.coords[0][0]}")
                            # print(f"intersects with inner polygons?: {lin.intersects(inner[0])}")
                            contains = False
                            # print(f"number of splitted: {len()}")
                            for i in range (len(inner)):
                                if lin.intersects(inner[i]) and len(lin.intersection(inner[i]).coords)>1:
                                    contains = True
                                    
                                    # paralels.append(intersect(lin.coords))
                                else:
                                    pass
                            if contains == False:
                                paralels.append(intersect(lin.coords))
                    else:
                        paralels.append(intersect(intersected_points))
                        # pass

              

            
               
            x+=width

        self.paralels = paralels
        # self.paralels = par_tracks


        
