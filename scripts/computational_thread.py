from PyQt5.QtCore import QThread, QTime, Qt, QTimer, pyqtSignal
import time
import numpy as np
from pyqtgraph import graphicsWindows

from scripts.xmeans import xmeans_clustering
from scripts.genetic import run_evolution
from scripts.node_graph import NodeGraph
from scripts.sub_areas import Areas
from paralel_tracks import ParalelTracks

from copy import deepcopy

class ComputationalThread(QThread):
    def __init__(self, graph, width):
        QThread.__init__(self)
        self.data = None
        self.graph = deepcopy(graph)
        self.width = deepcopy(width)
        self.seq = None
        self.areas = None
        self.node_graph = None


    def __del__(self):
        self.wait()

    def run(self):
        graph = self.graph
        width = self.width

        tracks = ParalelTracks(graph.outer, graph.inner, width, graph.angle)
            # print(f"tracks lookalike: {tracks.paralels}")
        tracks.getUpperPoints()

        arr = []
        input_arr = []

        for i in range(len(tracks.upper)):
            arr.append((tracks.upper[i].point))
            input_arr.append([tracks.upper[i].point[0],tracks.upper[i].point[1]])


        clusters, clusters_count, centers = xmeans_clustering(input_arr)

        objects = [graph.outer]
        for item in graph.inner:
            objects.append(item)

        areas = Areas(tracks.paralels, clusters, objects, width, None, graph.outer_index)

        print(f'Number of clusters: {len(areas.areas)}')
        node_states = []
        group_ids = []
        path_distances = []
        for i in range(len(areas.sub_areas)):
            area = areas.sub_areas[i]
            for k in range(len(area.node_states)):
                node_states.append(area.node_states[k])
                group_ids.append(i)
                path_distances.append(area.path_distances[k])

        objects = [graph.outer]
        for item in graph.inner:
            objects.append(item)
        

        node_graph = NodeGraph(node_states, group_ids, path_distances, objects)
        
        # sample_count = 8
        sample_count = len(areas.sub_areas)

        orig_seq = list(range(0,sample_count))

        areas_nodes = []

        for i in orig_seq:
            areas_nodes.append(areas.sub_areas[i])

        node_graph.set_areas(areas_nodes)


        pop_size = 8
        seq, time_genetic = run_evolution(sample_count, graph.genetic_limit, node_graph.get_value_fitness, graph.pop_size, time_limit=graph.time_limit, genetic_type=graph.genetic_type)

        # print(f'final seq : {seq}')
        seq_areas = [areas_nodes[ind] for ind in seq ]

        

        final_seq, final_val = node_graph.get_value(seq_areas)
        print(f'genetic best solution: {final_val}')
        print(f'Time needed for GA: {time_genetic}')


        self.seq = seq
        self.areas = areas_nodes
        self.node_graph = node_graph

class ClusteringThread(QThread):
    def __init__(self, graph, width):
        QThread.__init__(self)
        self.data = None
        self.graph = deepcopy(graph)
        self.width = deepcopy(width)
        self.seq = None
        self.areas = None
        self.node_graph = None


    def __del__(self):
        self.wait()

    def run(self):
        print(f'running clustering')
        graph = self.graph
        width = self.width

        tracks = ParalelTracks(graph.outer, graph.inner, width, graph.angle)
            # print(f"tracks lookalike: {tracks.paralels}")
        tracks.getUpperPoints()

        self.tracks = tracks

        arr = []
        input_arr = []

        for i in range(len(tracks.upper)):
            arr.append((tracks.upper[i].point))
            input_arr.append([tracks.upper[i].point[0],tracks.upper[i].point[1]])


        clusters, clusters_count, centers = xmeans_clustering(input_arr)

        objects = [graph.outer]
        for item in graph.inner:
            objects.append(item)

        areas = Areas(tracks.paralels, clusters, objects, width, None, graph.outer_index)
        print(f'Number of clusters: {clusters_count}')

        self.areas = areas

class VisibilityGraphThread(QThread):
    def __init__(self, graph, width, areas):
        QThread.__init__(self)
        self.data = None
        self.graph = deepcopy(graph)
        self.width = deepcopy(width)
        self.seq = None
        self.areas = deepcopy(areas)
        self.node_graph = None


    def __del__(self):
        self.wait()

    def run(self):
        graph = self.graph
        width = self.width
        areas = self.areas

        node_states = []
        group_ids = []
        path_distances = []
        for i in range(len(areas.sub_areas)):
            area = areas.sub_areas[i]
            for k in range(len(area.node_states)):
                node_states.append(area.node_states[k])
                group_ids.append(i)
                path_distances.append(area.path_distances[k])

        objects = [graph.outer]
        for item in graph.inner:
            objects.append(item)
        

        node_graph = NodeGraph(node_states, group_ids, path_distances, objects, graph.outer_for_visgraph)
        
        # sample_count = 8
        sample_count = len(areas.sub_areas)

        orig_seq = list(range(0,sample_count))

        areas_nodes = []

        for i in orig_seq:
            areas_nodes.append(areas.sub_areas[i])

        node_graph.set_areas(areas_nodes)

        # self.areas = areas_nodes
        self.node_graph = node_graph


class GeneticThread(QThread):
    def __init__(self, graph, width, areas, node_graph):
        QThread.__init__(self)
        self.data = None
        self.graph = deepcopy(graph)
        self.width = deepcopy(width)
        self.seq = None
        self.areas = deepcopy(areas)
        self.node_graph = deepcopy(node_graph)


    def __del__(self):
        self.wait()

    def run(self):
        graph = self.graph
        width = self.width
        areas = self.areas
        node_graph = self.node_graph

        sample_count = len(areas.sub_areas)

        orig_seq = list(range(0,sample_count))

        areas_nodes = []

        for i in orig_seq:
            areas_nodes.append(areas.sub_areas[i])
        
        print(f'node graph looks check: {node_graph}')

        node_graph.set_areas(areas_nodes)


        seq, time_genetic = run_evolution(sample_count, graph.genetic_limit, node_graph.get_value_fitness, graph.pop_size, time_limit=graph.time_limit, genetic_type=graph.genetic_type)

        # print(f'final seq : {seq}')
        seq_areas = [areas_nodes[ind] for ind in seq ]

        

        final_seq, final_val = node_graph.get_value(seq_areas)
        print(f'genetic best solution: {final_val}')
        print(f'Time needed for GA: {time_genetic}')


        self.seq = seq
        self.areas = areas_nodes
        self.node_graph = node_graph

class GeneticThreadTest(QThread):
    def __init__(self, graph, width, areas, node_graph):
        QThread.__init__(self)
        self.data = None
        self.graph = deepcopy(graph)
        self.width = deepcopy(width)
        self.seq = None
        self.areas = deepcopy(areas)
        self.node_graph = deepcopy(node_graph)


    def __del__(self):
        self.wait()

    def run(self):
        graph = self.graph
        width = self.width
        areas = self.areas
        node_graph = self.node_graph

        sample_count = len(areas.sub_areas)

        orig_seq = list(range(0,sample_count))

        areas_nodes = []

        for i in orig_seq:
            areas_nodes.append(areas.sub_areas[i])

        node_graph.set_areas(areas_nodes)


        seq, time_genetic = run_evolution(sample_count, graph.genetic_limit, node_graph.get_value_fitness, graph.pop_size, time_limit=graph.time_limit, genetic_type=graph.genetic_type)

        # print(f'final seq : {seq}')
        seq_areas = [areas_nodes[ind] for ind in seq ]

        

        final_seq, final_val = node_graph.get_value(seq_areas)
        print(f'genetic best solution: {final_val}')
        print(f'Time needed for GA: {time_genetic}')


        self.seq = seq
        self.areas = areas_nodes
        self.node_graph = node_graph


class PlotThread(QThread):
    def __init__(self, content):
        QThread.__init__(self)
        self.content = content

    def __del__(self):
        self.wait()

    def run(self):
        for item in self.content.graphWidget.listDataItems():
            if item.name() != 'plot':
                self.content.graphWidget.removeItem(item)

