from paralel_tracks import UpperList
from shapely.geometry import Point, Polygon, LineString, linestring

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


class Areas():
    def __init__(self, tracks, clusters, objects) -> None:
        super().__init__()
        self.get_sub_areas(tracks, clusters, objects)
        self.split_by_different_objects()
        self.check_neighbours()

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


    def check_neighbours(self):
        areas_output = []
        for area in self.areas:
            right_lines = self.equidistant_and_not_identical(area)
            if right_lines:
                areas_output.append(area)
            else:
                print(f'I should update this cluster!')
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
                        if (line.distance(line_next) - 0.5)>diff or self.is_identical(area_copy[i], area_copy[i+1]):
                            print('nok, will pop')
                            area_copy.pop(i+1)
                            i = i - 1
                            if i < 0:
                                i = 0
                        else:
                            # print('ok, will apend')
                            # area_item.append(area_copy[i+1])
                            i = i + 1
                        print(f"count of counter: {counter}")
                        # if i == len(area_copy):
                        #     break


                    for k in range(len(area_copy)):
                        print(f'iteration of popping {k}')
                        area.pop(area.index(area_copy[k]))

                    
                    areas_to_append.append(area_copy)

                    if self.equidistant_and_not_identical(area):
                        areas_to_append.append(area)



                for item in areas_to_append:
                    areas_output.append(item)

        self.areas = areas_output
        return self.areas
        



                


