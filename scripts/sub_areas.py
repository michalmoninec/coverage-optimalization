from random import paretovariate
from itertools import chain
import math

from paralel_tracks import UpperList
from shapely.geometry import Point, Polygon, LineString, MultiPoint, LinearRing
from shapely.ops import split, snap, nearest_points


from copy import deepcopy

def partition(alist, indices):
    return [alist[i:j] for i, j in zip([0]+indices, indices+[None])]

class ParallelLine():
    def __init__(self, upper, lower, objects) -> None:
        super().__init__()
        self.upper_point = upper
        self.lower_point = lower
        
        self.upper_group = self.set_group(upper, objects)
        self.lower_group = self.set_group(lower, objects)

        self.line = LineString([Point(self.upper_point), Point(self.lower_point)])

        

    def set_group(self, point, objects):
        point = Point(point)
        for index,obj_item in enumerate(objects):
            poly = Polygon(obj_item)
            if poly.exterior.distance(point)<0.0000001:
                return index
        # print(f"hello there, general number of objects: {len(objects)}")

class SubArea():
    def __init__(self, parallels) -> None:
        super().__init__()
        self.parallels = parallels
        self.end_points = self.get_points()
        self.paths = self.generate_paths()
        self.node_states = self.get_node_states()

        self.comptue_path_length()


    def get_points(self):
        points = []
        parallels = self.parallels

        points.append(parallels[0].upper_point)
        points.append(parallels[0].lower_point)

        if len(parallels)>1:
            points.append(parallels[-1].upper_point)
            points.append(parallels[-1].lower_point)
        
        # for item in points:
        #     print(f"end point item {item}")
        # print(10*'=')
        return points
    
    def generate_paths(self):
        paths = []
        parallels = self.parallels
        end_points = self.end_points

        for i in range(len(end_points)):
            path = []
            parallels_path = parallels.copy()
            start_point = end_points[i]
            # index = None

            for k in range(len(parallels)):
                # print(f'{parallels[k].upper_point} - parallel')
                # print(f'{start_point} - start point')
                if (start_point == parallels[k].upper_point or start_point == parallels[k].lower_point):
                    index = k
                    if index != 0:
                        parallels_path = parallels_path[::-1]
                    break
            
            

            if start_point == parallels_path[0].upper_point:
                seq = ['upper_point', 'lower_point']
            else:
                seq = ['lower_point', 'upper_point']

            for k in range(len(parallels_path)):
                if k % 2 == 0:
                    for point in seq:
                        path.append(getattr(parallels_path[k], point))
                else:
                    for point in seq[::-1]:
                        path.append(getattr(parallels_path[k], point))

            paths.append(path)
        # for item in paths:
        #     print(f'path item {item}')
        # print(20*'*')
        return paths
    
    def get_distance(self, p1, p2):
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]

        x = x2 - x1
        y = y2 - y1

        diff = math.sqrt(x*x + y*y)
        return diff

    def comptue_path_length(self):
        paths = self.paths
        path_distances = []
        
        for i in range(len(paths)):
            path = paths[i]
            distance = 0
            for k in range(len(path)-1):
                p1 = path[k]
                p2 = path[k+1]
                distance = distance + self.get_distance(p1,p2)
            path_distances.append(distance)
        
        self.path_distances = path_distances






    def get_node_states(self):
        paths = self.paths
        node_states = []

        for i in range(len(paths)):
            path = paths[i]
            node_states.append([path[0],path[-1]])
        # for item in node_states:
        #     print(f'node_state item: {item}')
        # print(5*'-')
        return node_states


class Areas():
    def __init__(self, tracks, clusters, objects, width, plot_print, outer_index) -> None:
        super().__init__()
        self.graph_width = width

        self.get_sub_areas(tracks, clusters, objects)
        self.split_by_different_objects()
        self.check_neighbours(width)
        self.split_by_convex(objects, plot_print, outer_index)
        self.set_areas()

        
        # self.plot_print = plot_print
    def set_areas(self):
        sub_areas = []
        for i in range(len(self.areas)):
            sub_areas.append(SubArea(self.areas[i]))
        self.sub_areas = sub_areas

    def get_sub_areas(self, tracks, clusters, objects):
        sub_areas = []
        areas = []

        for i in range(len(clusters)):
            subset = []
            for k in range(len(clusters[i])):
                subset.append([tracks[clusters[i][k]][0],tracks[clusters[i][k]][1]])
            # print(f'subset looks like: {subset}')
            sub_areas.append(subset)

        for i in range(len(sub_areas)):
            sub_area = sub_areas[i]
            area_item = []
            for k in range(len(sub_area)):
                paralel = sub_area[k]
                upper = (paralel[0][1],paralel[1][1])
                # upper = (paralel[0][0],paralel[1][0])
                lower = (paralel[0][0],paralel[1][0])
                area_item.append(ParallelLine(upper, lower, objects))
                # print(f"single paralel track {paralel}")
                # print(f"lower : {(paralel[0][0],paralel[1][0])}")
                # print(f"upper : {(paralel[0][1],paralel[1][1])}")
            areas.append(area_item)

        self.areas = areas

    def split_by_upper_objects(self):
        areas_upper_splitted = []
        for area in self.areas:
            area_upper_item = []
            upper_groups = []
            for index, paralel in enumerate(area):
                if paralel.upper_group not in upper_groups:
                    upper_groups.append(paralel.upper_group)
                    area_upper_item.append([paralel])
                else:
                    area_upper_item[upper_groups.index(paralel.upper_group)].append(paralel)
            for item in area_upper_item:
                areas_upper_splitted.append(item)
        self.areas = areas_upper_splitted

    def split_by_lower_objects(self):
        areas_lower_splitted = []
        for area in self.areas:
            area_lower_item = []
            lower_groups = []
            for index, paralel in enumerate(area):
                if paralel.lower_group not in lower_groups:
                    lower_groups.append(paralel.lower_group)
                    area_lower_item.append([paralel])
                else:
                    area_lower_item[lower_groups.index(paralel.lower_group)].append(paralel)
            for item in area_lower_item:
                areas_lower_splitted.append(item)
        self.areas = areas_lower_splitted

    def split_by_different_objects(self):
        self.split_by_upper_objects()
        self.split_by_lower_objects()
        return self.areas

    def is_identical(self, line1, line2):
        if (Point(line1.upper_point).distance(Point(line2.lower_point))) > (Point(line1.lower_point).distance(Point(line2.upper_point))):
            point1 = line1.upper_point
            point2 = line2.lower_point
            line = LineString([Point(point1), Point(point2)])
            if line.distance(Point(line1.lower_point))>0.00001 and line.distance(Point(line2.upper_point))>0.00001:
                return False
            else:
                return True
        else:
            point1 = line1.lower_point
            point2 = line2.upper_point
            line = LineString([Point(point1), Point(point2)])
            if line.distance(Point(line1.upper_point))>0.00001 and line.distance(Point(line2.lower_point))>0.00001:
                return False
            else:
                return True
        
            
    def equidistant_and_not_identical(self, area):
        valid = True
        for i in range(len(area)-1):
            line = area[i].line
            line_next = area[i+1].line
            diff = 0.00001
            if (line.distance(line_next) - 0.5)>diff or self.is_identical(area[i], area[i+1]):
                valid = False
        return valid


    def check_neighbours(self, width):
        areas_output = []
        for area in self.areas:
            right_lines = self.equidistant_and_not_identical(area)
            if right_lines:
                areas_output.append(area)
            else:
                # print(f'I should update this cluster!')
                areas_to_append = []
                while not self.equidistant_and_not_identical(area):
                    area_copy = area.copy()
                    counter = 0
                    i = 0
                    while i < (len(area_copy)-1):
                        # if i == (len(area_copy)-1):
                        #     areas_to_append.append([area_copy])
                        line = area_copy[i].line
                        line_next = area_copy[i+1].line
                        diff = 0.00001
                        if (line.distance(line_next) - width)>diff or self.is_identical(area_copy[i], area_copy[i+1]):
                            # print('nok, will pop')
                            area_copy.pop(i+1)
                            i = i - 1
                            if i < 0:
                                i = 0
                        else:
                            # print('ok, will apend')
                            # area_item.append(area_copy[i+1])
                            i = i + 1
                        # print(f"count of counter: {counter}")
                        # if i == len(area_copy):
                        #     break


                    for k in range(len(area_copy)):
                        # print(f'iteration of popping {k}')
                        area.pop(area.index(area_copy[k]))

                    
                    areas_to_append.append(area_copy)

                    if self.equidistant_and_not_identical(area):
                        areas_to_append.append(area)



                for item in areas_to_append:
                    areas_output.append(item)

        self.areas = areas_output
        return self.areas

    def center_outside(self, points, object, outer_index, obj_index):
        p1 = points[0]
        p2 = points[1]
        line = LineString([Point(p1), Point(p2)])
        midpoint = line.interpolate(0.5, normalized=True)
        if object.contains(midpoint):
            if obj_index == outer_index:
                return False
            else:
                # print('center inside = true, object is outer')
                return True
        else:
            if obj_index == outer_index:
                # print('center outside = true, object is outer')
                return True
            else:
                return False


    def distance_not_in_bounds(self, points):
        p1 = points[0]
        p2 = points[1]
        width = self.graph_width
        coef = 2
        dist = coef * width

        if p1.distance(p2) > dist:
            # print('Distance is out of bounds')
            return True

        else:
            return False

    def next_point_collision(self, area, objects, plot_print, outer_index):
        counter = 0
        good = True
        # print(50*'-')
        # print(f"area looks: {area}")
        # print(f'out of index fuckup: {area[0].upper_group}')
        # print(f'len of objects {len(objects)}')
        obj_upper = Polygon(objects[area[0].upper_group])
        obj_lower = Polygon(objects[area[0].lower_group])
        obj_upper_index = area[0].upper_group
        obj_lower_index = area[0].lower_group

        split_indexes = []

        for i in range(len(area)-1):
            parallel = area[i]
            parallel_next = area[i+1]

            upper_points = MultiPoint([parallel.upper_point, parallel_next.upper_point])
            lower_points = MultiPoint([parallel.lower_point, parallel_next.lower_point])

            obj_upper = snap(obj_upper, upper_points, 0.0000001)
            obj_lower = snap(obj_lower, lower_points, 0.0000001)

            ring_upper = LinearRing(list(obj_upper.exterior.coords))
            ring_lower = LinearRing(list(obj_lower.exterior.coords))

            line_upper = LineString(upper_points)
            line_lower = LineString(lower_points)

            if ring_upper.intersects(line_upper):
                intersection = ring_upper.intersection(line_upper)
                # print(f"type of intersection : {intersection.geom_type}")
                if intersection.geom_type != "LineString" and (self.center_outside(upper_points, obj_upper, outer_index, obj_upper_index or len(intersection)>2)) and self.distance_not_in_bounds(upper_points):
                    # plot_print((parallel.upper_point[0],parallel_next.upper_point[0]),(parallel.upper_point[1],parallel_next.upper_point[1]), [150,0,0], 'heisenberg')
                    good = False
                    if i not in split_indexes:
                        split_indexes.append(i)

            if ring_lower.intersects(line_lower):
                intersection = ring_lower.intersection(line_lower)
                # print(f"type of intersection : {intersection.geom_type}")
                # if intersection.geom_type != "LineString" and self.center_outside(lower_points, obj_lower, outer_index, obj_lower_index) and self.distance_not_in_bounds(lower_points):
                if intersection.geom_type != "LineString" and (self.center_outside(lower_points, obj_lower, outer_index, obj_lower_index) or len(intersection)>2) and self.distance_not_in_bounds(lower_points) :
                    # print(f"len of intersection: {len(intersection)}")
                    # print(5*"dostanu se tadz kokote")
                    good = False
                    if i not in split_indexes:
                        split_indexes.append(i)
        return split_indexes

        # if good:
        #     return area
        # else:
        #     return None
    def partition(self, alist, indices):
        pairs = zip(chain([0], indices), chain(indices, [None]))
        return (alist[i:j] for i, j in pairs)

    def split_by_convex(self, objects, plot_print, outer_index):
        areas = self.areas
        output_areas = []
        
        for area in areas:
            #neco nefungovalo pri rozteci 1m a uhlu 135
            if area:
                indexes = self.next_point_collision(area, objects, plot_print, outer_index)
                indexes = [x+1 for x in indexes]
                if len(indexes)<1:
                    output_areas.append(area)
                else:
                    # print(f'splitting indexes: {indexes}')
                    new_ones = self.partition(area, indexes)
                    # print(f"new areas to append: {new_ones}")
                    for item in new_ones:
                        # print(f"item looks: {item}")
                        output_areas.append(item)
        
        self.areas = output_areas

            
            


        

        



                


