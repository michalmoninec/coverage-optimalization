from pykml import parser
from os import path
import re
import matplotlib.pyplot as plt
import matplotlib as mpl
import utm
import numpy as np
import math
from shapely.geometry import Polygon, LineString
from copy import deepcopy

#dump this after changing data types of outer, inner
class Coordinates():
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
    def clear(self):
        self.x = None
        self.y = None

#line intersection with set of lines
def line_intersection(sset, item, last):
    line = LineString([(item),(last)])

    for i in range(len(sset)-1):
        if line.intersects(sset[i]):
            point_list = list(line.intersection(sset[i]).coords)
            return point_list[0]
    return False
   
#loops through array and looks for second closure
def trim_backwards(a_rr, norm):
    arr = norm[::-1]
    trimmed = [arr[0],arr[1]]
    trimmed_lines = [LineString([(arr[0]),(arr[1])])]

    for i in range(2 ,len(arr)):
        if line_intersection(trimmed_lines, arr[i], trimmed[-1]):
            # print('focking intersection!')
            trimmed.append(line_intersection(trimmed_lines, arr[i], trimmed[-1]))
            break
        else:
            trimmed.append(arr[i])
            trimmed_lines.append(LineString([(trimmed[-1]),(trimmed[-2])]))
    trimmed = trimmed[::-1]
    trimmed[-1] = a_rr[-1]
    return trimmed
            
#change as class function to GraphData
def get_closed_loops(data):
    # print(f"delka dat na vstupu : {len(data)}")
    separated_loops = []
    i = 0
    while i<(len(data)-1):
        open = True
        adepts = []
        adepts_lines = []
        normalized = []
        while open:
            if len(adepts)<1:
                adepts.append(data[i])
            elif len(adepts)<2:
                adepts.append(data[i])
                adepts_lines.append(LineString([(adepts[0]),(adepts[1])]))
            elif line_intersection(adepts_lines, data[i], adepts[-1]) or (data[i] in adepts):
                if data[i] in adepts:
                    normalized = deepcopy(adepts)
                    normalized.append(data[i])
                    adepts.append(data[i])
                    trimmed = trim_backwards(adepts, normalized)
                    separated_loops.append(trimmed)
                    open = False
                else:
                    normalized = deepcopy(adepts)
                    normalized.append(data[i])
                    adepts.append(line_intersection(adepts_lines, data[i], adepts[-1]))
                    trimmed = trim_backwards(adepts, normalized)
                    separated_loops.append(trimmed)
                    open = False
            else:
                adepts.append(data[i])
                adepts_lines.append(LineString([(adepts[-1]),(adepts[-2])]))

            if open:
                i+=1

            if i == len(data):
                open = False

    return separated_loops
                
    # endpoints = []
    # split_coords= []
    # split_indexes = [-1]
    # separated_loops = []

    # for element in data:
    #     if data.count(element)>1:
    #         endpoints.append(element)

    # if endpoints:
    #     unique_endpoints=set(endpoints)
    #     for item in unique_endpoints:
    #         split_coords.append(item)

    # if split_coords:
    #     for i in range (len(split_coords)):
    #         index = len(data) - 1 - data[::-1].index(split_coords[i])
    #         split_indexes.append(index)
    # split_indexes = sorted(split_indexes)

    # for i in range (len(split_indexes)-1):
    #     separated_loops.append(data[split_indexes[i]+1:split_indexes[i+1]+1])
    # return separated_loops

#fix outer, inner data structures
#coords - make whole array of points [(x,y),(x,y)]

def data_to_print(arr):
    arr_x = []
    arr_y = []
    for i in range(len(arr)):
        arr_x.append(arr[i][0])
        arr_y.append(arr[i][1])
    return (arr_x,arr_y)

class GraphData():
    def __init__(self, file_name):
        super().__init__()
        self.coords = []
        self.inner = []
        self.outer = []
        self.inner_plot = []
        self.file_name = file_name
        self.width = None
        self.coef = None
        self.angle = None
        self.genetic_limit = 100
        self.time_limit = 1800
        self.pop_size = 8
        self.genetic_type = 0
        



    def set_default(self):
        self.coords = []
        self.inner = []
        self.outer = []
        self.inner_plot = []
        self.outer_plot = []

    def set_time_limit(self, limit):
        self.time_limit = limit

    def set_genetic_type(self, type):
        self.genetic_type = type

    def setAngle(self, angle):
        self.angle = angle

    def setWidth(self,width):
        self.width = width

    def setCoef(self,coef):
        self.coef = coef

    def set_genetic_limit(self, limit):
        self.genetic_limit = limit

    def set_pop_size(self, size):
        self.pop_size = size

    def reset_advanced_settings(self):
        self.genetic_limit = 100
        self.time_limit = 1800
        self.pop_size = 8
    #handle different type of KML files

    def set_coords(self, file_name):
        self.file_name = file_name
        with open(file_name, encoding='utf-8') as f:
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
            # np.round(np.array(coor_x[:]),4), np.round(np.array(coor_y[:]),4))

        x = np.round(np.array(x),4)
        y = np.round(np.array(y),4)

        xmin = min(x)
        ymin = min(y)
        # print('min x =  {}'.format(xmin))
        # print('min y =  {}'.format(ymin))

        x = [x-xmin for x in x]
        y = [y-ymin for y in y]

        # print(f"vstup x> {x}")

        for i in range(len(x)):
            self.coords.append((x[i],y[i]))

        self.file_name = file_name


    def get_outer_inner(self):
        closed_loops = get_closed_loops(self.coords)
        # print(f"closed loops: {closed_loops}")

        polygons = []

        for i in range(len(closed_loops)):
            polygons.append(Polygon(closed_loops[i]).area)

        # print(f"polygons of closed loops: {polygons.index(max(polygons))}")
        # print(f"polygons areas: {polygons[0].area}")
        outer_index = polygons.index(max(polygons))
        self.outer_index = outer_index

        # print(f'outer_index: {outer_index}')

        for i in range(len(closed_loops)):
            if i == outer_index:
                self.outer = closed_loops[i]
            else:
                self.inner.append(closed_loops[i])

        # print(f"self.inner : {self.inner}")
        # print(f"self.outer : {self.outer}")

        self.outer_plot = data_to_print(self.outer)
        # print(f"outer_plot: {self.outer_plot}")

        for i in range(len(self.inner)):
            self.inner_plot.append(data_to_print(self.inner[i]))

    def scale_inner(self):
        inner = self.inner
        
