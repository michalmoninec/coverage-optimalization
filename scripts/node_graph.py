from logging import exception
import math
import itertools
import time

import pyvisgraph as vg
from shapely.geometry.linestring import LineString
from shapely.geometry.polygon import LinearRing, Point, Polygon
from shapely.ops import nearest_points

import matplotlib.pyplot as plt

class Node():
    def __init__(self, state, length) -> None:
        super().__init__()
        self.state = state
        self.len = length
        self.val = math.inf
        self.parent = None


class NodeGraph():
    def __init__(self, node_states, group_ids, path_distances, objects) -> None:
        super().__init__()

        self.move_between_paths = []
        self.test_lines = []
        self.objects = objects
        self.polygons = [Polygon(obj) for obj in objects]
        self.vis_graph = vg.VisGraph()
        self.get_dist_visibility(objects)
        
        self.distance_table = self.set_distance_table(node_states, group_ids)
        self.path_distances = path_distances
        self.node_states = node_states
        
    def get_exact_solution(self,areas_nodes, sample_count):
        multiple_seq = list(itertools.permutations(areas_nodes,sample_count))
        val_g = math.inf
        val_max = 0
        seq_g = None
        start = time.time()
        for item in multiple_seq:
            seq, val = self.get_value(item)
            if val < val_g:
                seq_g = seq
                val_g = val
            if val > val_max:
                val_max = val
        end = time.time()
        # print(f'Time needed to find exact solution: {end-start}')
        time_needed = end - start
        return seq_g, val_g, val_max, time_needed

    def set_distance_table(self, node_states, group_ids):
        distance_table = []
        move_paths = []
        start = time.time()
        for i in range(len(node_states)):
            column = []
            m_column = []
            for j in range(len(node_states)):
                if group_ids[i] == group_ids[j]:
                    column.append(None)
                    m_column.append(None)
                else:
                    val, path = (self.get_distance(node_states[i], node_states[j]))
                    column.append(val)
                    m_column.append(path)
                    # column.append(self.get_distance(node_states[i], node_states[j]))
            distance_table.append(column)
            move_paths.append(m_column)
        self.move_between_paths = move_paths
        end = time.time()
        print(f'Time for vis graph : {end - start}')
        return distance_table

    def compute_path_len(self, points):
        dist = 0
        for i in range(len(points)-1):
            current = points[i]
            next = points[i+1]
            x1,y1 = current.x,current.y
            x2,y2 = next.x,next.y
            x_diff = x2 - x1
            y_diff = y2 - y1

            diff = math.sqrt(x_diff*x_diff + y_diff*y_diff)
            dist += diff
        return dist




    def create_nodes(self, areas_nodes):
        graph_nodes = []
        for item in areas_nodes:
            nodes = []
            for node in item.node_states:
                len = self.path_distances[self.node_states.index(node)]
                nodes.append(Node(node, len))
                # print(f"len of this area: {self.path_distances[self.node_states.index(node)]}")
            graph_nodes.append(nodes)
        self.nodes = graph_nodes
        # print(graph_nodes[0])

    def get_distance_from_table(self, state1, state2):
        ind1 = self.node_states.index(state1)
        ind2 = self.node_states.index(state2)
        return self.distance_table[ind1][ind2]

    def assign_values(self):
        node_groups = self.nodes
        start = time.time()
        for i in range(len(node_groups[0])):
            node = node_groups[0][i]
            node.val = node.len

        for i in range(len(node_groups)-1):
            nodes_current = node_groups[i]
            nodes_next = node_groups[i+1]

            for j in range(len(nodes_next)):
                node_next_iter = nodes_next[j]
                for k in range(len(nodes_current)):
                    node_current_iter = nodes_current[k]
                    val_iter = node_current_iter.val + node_next_iter.len + self.get_distance_from_table(node_current_iter.state, node_next_iter.state)
                    # print(f'current value of distance and previous state: {val_iter}')
                    if val_iter < node_next_iter.val:
                        node_next_iter.val = val_iter
                        node_next_iter.parent = node_current_iter
            #             print(f'will set this as parent')
            #     print(10*'-')
            # print(10*'**')
        end = time.time()
        # print(f'time for asigning values; {end-start}')

    def get_shortest_path(self):
        value = math.inf
        min_val_node = None
        # print(f"last item of self.nodes {self.nodes[-1]}")
        for i in range(len(self.nodes[-1])):
            node_item = self.nodes[-1][i]
            # print(f'node_item: {node_item.val}')
            if node_item.val < value:
                min_val_node = node_item
                value = node_item.val
                # print(f'chosen index: {i}')

        node_sequence = [min_val_node]
        node_next = min_val_node

        while node_next.parent:
            node_sequence.append(node_next.parent)
            node_next = node_next.parent
            
        return node_sequence[::-1], min_val_node.val

    def get_value(self, seq):
        # seq = [self.areas[i] for i in seq]
        self.create_nodes(seq)
        self.assign_values()
        sequence, val = self.get_shortest_path()
        # print(f'sequence {sequence}, val: {val}')
        return sequence, val

    def set_areas(self, area):
        self.areas = area

    def get_value_fitness(self, seq):
        seq = [self.areas[i] for i in seq]
        self.create_nodes(seq)
        self.assign_values()
        sequence, val = self.get_shortest_path()
        # print(f'sequence {sequence}, val: {val}')
        return val


    def get_dist_visibility(self, objects):
        start = time.time()
        # print(f'objects before: {objects}')
        objects2 = [self.wrap_outer_polygon(objects[0])]
        # objects2 = objects[1:]
        objects2 += objects[1:]
        
        # print(f'objects after: {objects2}')

        polys = []
        for poly in objects2:
            col = []
            for i in range(len(poly)):
                point = poly[i]
                col.append(vg.Point(round(point[0],1),round(point[1],1)))
                # col.append(vg.Point(point[0],point[1]))
            polys.append(col)
        # print(f'polys for visgraph: {polys}')

        self.vis_graph.build(polys, status=False, workers=4)



        end = time.time()
        print(f'Time needed to crate vis graph: {end-start}')

    def get_distance(self, state1, state2):
        p1_end = state1[1]
        p2_start = state2[0]

        x1, y1 = p1_end[0], p1_end[1]
        x2, y2 = p2_start[0], p2_start[1]

        x_diff = x2 - x1
        y_diff = y2 - y1

        dist = math.sqrt(x_diff*x_diff + y_diff*y_diff)
        dist2 = None
        
        point1 = Point(x1,y1)
        point2 = Point(x2,y2)

        id1 = self.get_closest_polygon(point1)
        id2 = self.get_closest_polygon(point2)

        if id1 != None:
            new_point_1, coords1 = self.move_point_from_polygon([x1,y1], id1)
            point1 = vg.Point(new_point_1[0], new_point_1[1])
            # print('Updated point1')
        else:
            point1 = vg.Point(x1,y1)

        if id2 != None:
            new_point_2, coords2 = self.move_point_from_polygon([x2,y2], id2)
            point2 = vg.Point(new_point_2[0],new_point_2[1])
            # print('Updated point2')
        else:
            point2 = vg.Point(x2,y2)

        try:
            dist2 = self.vis_graph.shortest_path(point1, point2)
        except Exception as e:
            print(e)
            pass

        if dist2:
            self.move_between_paths.append(dist2)
            return self.compute_path_len(dist2), dist2
        else:
            self.move_between_paths.append([point1, point2])
            return dist, [point1, point2]

    def move_point_from_polygon(self, point_in, polygon_id):
        # print(f'objects in move function : {len(self.objects)}')


        polygon = self.objects[polygon_id]
        # print(f'point In : {point_in}')
        point = Point(point_in[0],point_in[1])
        # print(f'polygon: {polygon}')
        line_strings = []
        linear_ring = LinearRing(polygon)
        
        for i in range(len(polygon)-1):
            curr = polygon[i]
            next = polygon[i+1]
            line_strings.append(LineString([(curr[0], curr[1]),(next[0], next[1])]))

        ccw = linear_ring.is_ccw
        
        distance = math.inf
        closest_line = None
        for line in line_strings:
            if line.distance(point)<distance:
                closest_line = line
                distance = line.distance(point)

        coords = list(closest_line.coords)
        # print(f'coords looks: {coords}')
        self.test_lines.append([point, coords])
        x1, y1 = coords[0][0], coords[0][1]
        x2, y2 = coords[1][0], coords[1][1]

        x1 = round(x1,2)
        x2 = round(x2,2)

        y1 = round(y1,2)
        y2 = round(y2,2)

        # self.plot_path([[x[0],y[0]],[x[1],y[1]]], [0,150,0],5)

        sx = x2 - x1
        sy = y2 - y1

        if sx and sy:
            sxx = sx/abs(sx)
            syy = sy/abs(sy)
        elif sx and sy==0:
            syy = 0
            sxx = sx/abs(sx)
        elif sx == 0 and sy:
            sxx = 0
            syy = sy/abs(sy)
        else:
            print(f'shouldnt be here')

        # print(f'sxx {sxx}')
        # print(f'syy {syy}')

        d_len = 0.1

        # if not ccw:
        if sxx>0 and syy>0:
            norm = [-1, 1]
            if polygon_id == 0:
                norm = [i * -1 for i in norm]
            angle = math.atan(abs(sy)/abs(sx))
            # print(f'angle: {math.degrees(angle)}')
            x_d = math.sin(angle)*d_len*norm[0]
            y_d = math.cos(angle)*d_len*norm[1]
        elif sxx>0 and syy<0:
            norm = [1, 1]
            if polygon_id == 0:
                norm = [i * -1 for i in norm]
            angle = math.atan(abs(sy)/abs(sx))
            # print(f'angle: {math.degrees(angle)}')
            x_d = math.sin(angle)*d_len*norm[0]
            y_d = math.cos(angle)*d_len*norm[1]
        elif sxx<0 and syy<0:
            norm = [1, -1]
            if polygon_id == 0:
                norm = [i * -1 for i in norm]
            angle = math.atan(abs(sy)/abs(sx))
            # print(f'angle: {math.degrees(angle)}')
            x_d = math.sin(angle)*d_len*norm[0]
            y_d = math.cos(angle)*d_len*norm[1]
        elif sxx<0 and syy>0:
            norm = [-1, -1]
            if polygon_id == 0:
                norm = [i * -1 for i in norm]
            angle = math.atan(abs(sx)/abs(sy))
            # print(f'angle: {math.degrees(angle)}')
            x_d = math.cos(angle)*d_len*norm[0]
            y_d = math.sin(angle)*d_len*norm[1]
        elif sxx==0 and syy:
            x_d = 0
            y_d = d_len*syy
            if polygon_id == 0:
                y_d = -y_d
        elif syy==0 and sxx:
            y_d = 0
            x_d = d_len*sxx
            if polygon_id == 0:
                x_d = -x_d
        else:
            print(f'tady jsem se nemel dostat ombre //////////////////')
        
        if ccw:
            x_d = -x_d
            y_d = -y_d

        new_point = [round(point_in[0]+x_d,2), round(point_in[1]+y_d,2)]


        return new_point, coords

    def get_closest_polygon(self, point):
        distance = math.inf
        # print(f' polygons looks: {self.polygons}')
        #neberu prvni protoze vzdalenost kdyz je bod uvnitr polygonu je nulova
        polygons = self.polygons[1:]
        # polygons = self.polygons
        # print(f'polygons are: {self.objects[1:]}')
        # print(f'len of polygons : {len(polygons)}')
        id = None
        crit = 0.2


        for index, polygon in enumerate(polygons):
            if polygon.distance(point)<distance:
                pol_out = polygon
                distance = polygon.distance(point)
                # print(f'distance: {distance} and index: {index}')
        
        if distance<crit:
            id = polygons.index(pol_out) + 1
        else:
            id = 0
        # print(f'returning id: {id}')
        return id
    
    def wrap_outer_polygon(self, polygon):
        # print('This fucker will be wrapped by no one else than McGyver: {}'.format(polygon))
        
        p1 = polygon[-1]
        p2 = polygon[-2]

        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        dxx = dx/abs(dx)
        dxy = dy/abs(dy)

        polygon.pop()

        po_x = p1[0] + dxx * 0.05
        po_y = p1[1] + dxy * 0.05

        polygon.append((po_x, po_y))

        
        line = LineString(polygon)
        poly = LinearRing(polygon)

        if poly.is_ccw:
            offset = line.parallel_offset(1, 'right')
        else:
            offset = line.parallel_offset(1, 'left')
        # print(f'offset looks : {list(offset.coords)}')
        coords = list(offset.coords)
        polygon += coords[:-1]

        return polygon


       

        




