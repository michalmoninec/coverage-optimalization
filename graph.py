from pykml import parser
from os import path
import re
import matplotlib.pyplot as plt
import matplotlib as mpl
import utm
import numpy as np
import math
from shapely.geometry import Polygon


class Coordinates():
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

    def clear(self):
        self.x = None
        self.y = None


def get_closed_loops(data):
    endpoints = []
    split_coords = []
    split_indexes = [-1]
    separated_loops = []
    for element in data:
        if data.count(element) > 1:
            endpoints.append(element)
    # print(f'endpoint are: {endpoints}')
    if endpoints:
        unique_endpoints = set(endpoints)
        for item in unique_endpoints:
            split_coords.append(item)
    # print(split_coords)
    if split_coords:
        for i in range(len(split_coords)):
            index = len(data) - 1 - data[::-1].index(split_coords[i])
            split_indexes.append(index)
    print(split_indexes)
    print(f'Cele data: {data}')
    for i in range(len(split_indexes)-1):
        separated_loops.append(
            data[split_indexes[i]+1:split_indexes[i+1]+1])
    print(f'Separovane smycky: {separated_loops}')
    return separated_loops


class GraphData():
    def __init__(self, file_name):
        super().__init__()
        self.coords = Coordinates(None, None)
        self.border_inner = Coordinates(None, None)
        self.border_outer = Coordinates(None, None)
        self.border_outer_complete = []
        # self.coors = []
        self.file_name = file_name

        # self.set_coords(file_name)

    def set_coords(self, file_name):
        with open(file_name) as f:
            doc = parser.parse(f).getroot()

        # coor = doc.Document.Placemark.LineString.coordinates.text
        coor = doc.Document.Folder.Placemark.LineString.coordinates.text

        new_coor = re.findall('[0-9.0-9,0-9.0-9,0-9.0-9]+', coor)

        coor_x = []
        coor_y = []

        for i in range(len(new_coor)):
            c = new_coor[i].split(',')
            coor_x.append(float(c[1]))
            coor_y.append(float(c[0]))

        x, y, zn, zl = utm.from_latlon(
            np.array(coor_x[:]), np.array(coor_y[:]))

        # min_x = min(x)
        # min_y = min(y)

        # x = [m - min_x for m in x]
        # y = [m - min_y for m in y]

        self.file_name = file_name
        self.coords.x = x
        self.coords.y = y

        # for i in range (len(x)):
        #     self.coors.append(Coordinates(x[i],y[i]))

    def check_closed_loop(self, x, y):
        closed_loop = []

        for i in range(len(x)):
            if [x[i], y[i]] in closed_loop:
                closed_loop.append([x[i], y[i]])
                print(closed_loop)
                return closed_loop
            else:
                closed_loop.append([x[i], y[i]])
        return None

    def check_inner_validity(self):
        outer_set = []
        inner_set = []
        for i in range(len(self.border_outer.x)):
            outer_set.append((self.border_outer.x[i], self.border_outer.y[i]))

        for i in range(len(self.coords.x)):
            inner_set.append((self.coords.x[i], self.coords.y[i]))

        outer_polygon = Polygon(outer_set)
        inner_polygon = Polygon(inner_set)

        if outer_polygon.contains(inner_polygon):
            return True
        else:
            return False

    def get_outer_inner(self):
        whole_set = []
        for i in range(len(self.coords.x)):
            whole_set.append((self.coords.x[i], self.coords.y[i]))
        closed_loops = get_closed_loops(whole_set)
        print(closed_loops[0][0])

        outer_x = []
        outer_y = []

        inner_x = []
        inner_y = []

        for i in range(len(closed_loops[0])):
            coords = closed_loops[0][i]
            outer_x.append(coords[0])
            outer_y.append(coords[1])
        self.border_outer.x = outer_x
        self.border_outer.y = outer_y

        for i in range(len(closed_loops[1])):
            coords = closed_loops[1][i]
            inner_x.append(coords[0])
            inner_y.append(coords[1])

        self.border_inner.x = inner_x
        self.border_inner.y = inner_y
        # self.border_outer = closed_loops[0]
        # self.border_inner = closed_loops[1]
        # return(get_closed_loops(whole_set))
