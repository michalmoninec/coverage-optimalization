from paralel_tracks import UpperList
from shapely.geometry import Point, Polygon

def partition(alist, indices):
    return [alist[i:j] for i, j in zip([0]+indices, indices+[None])]

class ParallelLine():
    def __init__(self, upper, lower, objects) -> None:
        super().__init__()
        self.upper_point = upper
        self.lower_point = lower
        
        self.upper_group = self.set_group(upper, objects)
        self.lower_group = self.set_group(lower, objects)

        

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


