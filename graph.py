from pykml import parser
from os import path
import re
import matplotlib.pyplot as plt
import matplotlib as mpl
import utm
import numpy as np
import math
from shapely.geometry import Polygon

#dump this after changing data types of outer, inner
class Coordinates():
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
    def clear(self):
        self.x = None
        self.y = None

#change as class function to GraphData
def get_closed_loops(data):
    endpoints = []
    split_coords= []
    split_indexes = [-1]
    separated_loops = []

    for element in data:
        if data.count(element)>1:
            endpoints.append(element)

    if endpoints:
        unique_endpoints=set(endpoints)
        for item in unique_endpoints:
            split_coords.append(item)

    if split_coords:
        for i in range (len(split_coords)):
            index = len(data) - 1 - data[::-1].index(split_coords[i])
            split_indexes.append(index)
    split_indexes = sorted(split_indexes)

    for i in range (len(split_indexes)-1):
        separated_loops.append(data[split_indexes[i]+1:split_indexes[i+1]+1])
    return separated_loops

#fix outer, inner data structures
#coords - make whole array of points [(x,y),(x,y)]
class GraphData():
    def __init__(self, file_name):
        super().__init__()
        self.coords = Coordinates(None, None)
        self.border_inner = Coordinates(None, None)
        self.border_outer = Coordinates(None, None)
        self.inner_x = []
        self.inner_y = []
        self.inner = []
        self.outer = []
        self.border_outer_complete = []
        self.file_name = file_name

    #handle different type of KML files
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

        self.file_name = file_name

        #TODO handle coordinates apropriately
        self.coords.x = x
        self.coords.y = y

    #hardcoded, try some sofisticated way
    def check_closed_loop(self,x, y):
        closed_loop = []
        
        for i in range (len(x)):
            if [x[i],y[i]] in closed_loop:
                closed_loop.append([x[i],y[i]])
                return closed_loop
            else:
                closed_loop.append([x[i],y[i]])
        return None
        
    #bad data types, switch to array of points instead
    def check_inner_validity(self):
        outer_set = []
        inner_set = []

        for i in range (len(self.border_outer.x)):
            outer_set.append((self.border_outer.x[i],self.border_outer.y[i]))

        for i in range (len(self.coords.x)):
            inner_set.append((self.coords.x[i],self.coords.y[i]))
        
        outer_polygon = Polygon(outer_set)
        inner_polygon = Polygon(inner_set)

        x, y = outer_polygon.exterior.coords.xy

        if outer_polygon.contains(inner_polygon):
            return True
        else:
            return False

    #handle outer border properly, HARDCODED af
    def get_outer_inner(self):
        whole_set = []

        for i in range (len(self.coords.x)):
            whole_set.append((self.coords.x[i],self.coords.y[i]))
        closed_loops = get_closed_loops(whole_set)

        outer_x = []
        outer_y = []
        inner_x = []
        inner_y = []
        
        for i in range (len(closed_loops[0])):
            coords = closed_loops[0][i]
            outer_x.append(coords[0])
            outer_y.append(coords[1])
            self.outer.append((coords[0],coords[1]))

        self.border_outer.x = outer_x
        self.border_outer.y = outer_y

        for k in range(1,len(closed_loops)):
            for i in range (len(closed_loops[k])):
                coords = closed_loops[k][i]
                inner_x.append(coords[0])
                inner_y.append(coords[1])
            self.inner.append(Coordinates(inner_x,inner_y))
            inner_y = []
            inner_x = []