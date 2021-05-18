from os import name
from os.path import join
from random import sample
from xlwt import Workbook

from shapely.geometry.polygon import LinearRing, LineString
from graph import GraphData
from paralel_tracks import ParalelTracks
# from components.infoTable import InfoTable
from components.pushButton import PushButton
from components.header import HeaderWidget
from components.content import ContentWidget

from scripts.xmeans import xmeans_clustering
from scripts.sub_areas import Areas
from scripts.node_graph import NodeGraph
from scripts.genetic import run_evolution
from scripts.computational_thread import ClusteringThread, ComputationalThread, GeneticThread, PlotThread, VisibilityGraphThread

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QFileDialog, \
    QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, QFrame, QRadioButton, QStackedWidget, \
    QStackedLayout, QLabel, QSizePolicy, QGraphicsDropShadowEffect, QGroupBox, QFormLayout, QLineEdit, QComboBox, QSpinBox
from PyQt5.QtCore import QThread, Qt, QTimer, QRegExp, pyqtSignal
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator, QRegExpValidator

from pathlib import Path
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import numpy as np
import itertools
import time

import matplotlib.pyplot as plt

from copy import deepcopy

from hirearchial_clustering import hierarichial_cluster as cluster

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.graph_data = GraphData('')
        
        title = 'Optimal coverage plan'

        self.setWindowTitle(title)
        self.setGeometry(0, 0, 1200, 800)
        self.setWindowIcon(QIcon('icon.png'))

        style = """
        background-color: lightgray;
        margin: 0;
        padding: 0;
        """

        colors = []
        for i in range(100):
            colors.append(list(np.random.choice(range(255), size=3)))
        self.colors = colors
        

        self.setStyleSheet(style)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        # self.connect(self.compThread, pyqtSignal('computed()'), lambda i: print(i))

        ########################HEADER##############################
        self.headerFrame = HeaderWidget()
        header = self.headerFrame
        header.settingsButton.clicked.connect(self.showsettings)
        header.deleteGraphButton.clicked.connect(self.delete_graph_items)
        header.backButton.clicked.connect(self.backtograph)
        header.backButton.setEnabled(False)
        header.advancedOptions.clicked.connect(self.advanced_clicked)
        header.backToLoaderButton.clicked.connect(self.backToLoader)    
        ######################################################
        
        self.contentFrame = ContentWidget()
        content = self.contentFrame
        self.widthInputCheck(content.widthInput.text())
        self.threshInputCheck(content.threshInput.text())
        self.angleInputCheck(content.angleInput.text())

        content.startButton.clicked.connect(self.set_complete_file)
        # content.startButton.clicked.connect(self.test_thread)
        content.widthInput.textChanged.connect(lambda text: self.widthInputCheck(text))
        content.threshInput.textChanged.connect(lambda text: self.threshInputCheck(text))
        content.angleInput.textChanged.connect(lambda text: self.angleInputCheck(text))
        content.geneticIterLimit.textChanged.connect(lambda text: self.geneticInputChange(text))
        content.timeLimit.textChanged.connect(lambda text: self.timeLimitChange(text))
        content.popSize.textChanged.connect(lambda text: self.popSizeChange(text))
        content.geneticType.cb.currentIndexChanged.connect(lambda index: self.geneticTypeChange(index))
        content.stopButton.clicked.connect(lambda: self.stopSimulation())
        content.previewButton.clicked.connect(lambda: self.getToPreview())
        content.calculateGA.clicked.connect(lambda: self.compute_ga())

        content.advancedOptions.hide()
        content.graphWrapper.hide()
        self.graph_data.set_genetic_type(content.geneticType.cb.currentIndex())
        # print(f'current index: {content.geneticType.cb.currentIndex()}')
        ######################################################


        layout.addWidget(self.headerFrame)
        layout.addWidget(self.contentFrame,1)

        self.setLayout(layout)
        self.set_location()
        self.show()

    def timeLimitChange(self, text):
        self.graph_data.set_time_limit(int(text))

    def popSizeChange(self, text):
        self.graph_data.set_pop_size(int(text)) 

    def geneticTypeChange(self, index):
        self.graph_data.set_genetic_type(index)

    def advanced_clicked(self):
        text = self.headerFrame.advancedOptions.text()
        if text == 'Advanced options':
            self.headerFrame.advancedOptions.setText('Basic options')
            self.contentFrame.advancedOptions.show()
            self.graph_data.set_genetic_limit(int(self.contentFrame.geneticIterLimit.text()))
        else:
            self.headerFrame.advancedOptions.setText('Advanced options')
            self.contentFrame.advancedOptions.hide()
            self.graph_data.reset_advanced_settings()
            #nastaveni pevnych hodnot
        
        
        pass

    def angleInputCheck(self,text):
        if text:
            self.headerFrame.infoTable.angle.setText(text)
            self.graph_data.setAngle(int(text))

    def threshInputCheck(self, text):
        if text:
            # self.headerFrame.infoTable.thresh.setText(text)
            out_text = text.replace(',','.')
            out_text = float(out_text)
            self.graph_data.setCoef(out_text)
            self.headerFrame.infoTable.thresh.setText(str(out_text).replace('.',','))
        else:
            self.graph_data.setCoef(float('0.1'))
            self.headerFrame.infoTable.thresh.setText('0,1')

    def widthInputCheck(self, text):
        if text:
            self.headerFrame.infoTable.width.setText(text)
            # if ',' in text:
            #     out_text = text.replace(',','.')
            #     # print(f"changed text: {out_text}")
            #     # return text
            # else:
            #     out_text = text
            # self.graph_data.setWidth(float(out_text))
            self.graph_data.setWidth(float(text.replace(",",".")))

    def geneticInputChange(self, text):
        if text:
            self.graph_data.set_genetic_limit(int(text))

    def stopSimulation(self):
        if self.clustering_thread.isRunning():
            self.clustering_thread.terminate()
        elif self.visibility_thread.isRunning():
            self.visibility_thread.terminate()
        elif self.genetic_thread.isRunning():
            self.genetic_thread.terminate()
        elif self.visibility_thread_a.isRunning():
            self.visibility_thread_a.terminate()
        elif self.genetic_thread_a.isRunning():
            self.genetic_thread_a.terminate()


        self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.settingsMenu)
        
        

        # self.compThread.terminate()
        # self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.settingsMenu)
        # self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.graphWrapper)
        # self.headerFrame.settingsToggle.setCurrentWidget(self.headerFrame.backButtonWidget)
        # self.headerFrame.backButton.setDisabled(True)
        # self.headerFrame.advancedOptions.setDisabled(False)

    def getToPreview(self):
        self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.graphWrapper)
        self.headerFrame.settingsToggle.setCurrentWidget(self.headerFrame.backToLoaderWidget)

    def backToLoader(self):
        self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.stopSimulationWidget)
        self.headerFrame.settingsToggle.setCurrentWidget(self.headerFrame.backButtonWidget)


    def test_inner_thread(self):
        print(f'Print something: {self.graph_data.file_name}')
            

    def delete_graph_items(self):
        self.delete_graph()
        self.showsettings()
        self.headerFrame.deleteGraphButton.setEnabled(False)
        self.headerFrame.backButton.setEnabled(False)
        self.contentFrame.startButton.setText('Start plot')
        self.contentFrame.calculateGA.hide()

    def backtograph(self):
        # print('Helo there')
        self.headerFrame.settingsToggle.setCurrentWidget(self.headerFrame.settingsButtons)
        self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.graphWrapper)

    def showsettings(self):
        # print('General Kenobi')
        self.headerFrame.settingsToggle.setCurrentWidget(self.headerFrame.backButtonWidget)
        self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.settingsMenu)


    #remove outer bounds 
    def delete_graph (self):
        self.graph_data.set_default()
        self.contentFrame.graphWidget.clear()


    def test_thread(self):
        # time.sleep(10)
        # print('Heloo there')
        self.compThread.start()
        self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.stopSimulationWidget)
        self.headerFrame.advancedOptions.setDisabled(True)
        # self.compThread.finished.connect(lambda: self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.settingsMenu))

    def algorithm_finished(self, seq, areas_nodes, node_graph):
        self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.graphWrapper)
        self.headerFrame.settingsToggle.setCurrentWidget(self.headerFrame.settingsButtons)
        self.headerFrame.deleteGraphButton.setDisabled(False)
        self.headerFrame.backButton.setDisabled(False)
        self.headerFrame.advancedOptions.setDisabled(False)
        self.contentFrame.graphWidget.getViewBox().enableAutoRange()
        if seq:
            seq_areas = [areas_nodes[ind] for ind in seq ]
            final_seq, final_val = node_graph.get_value(seq_areas)
            # print(f'genetic best solution: {final_val}')
            # print(f'Time needed for GA: {time_genetic}')
            paths, states, paths_m = self.switch_seq(areas_nodes, final_seq, node_graph)

                       
            paths_exo = []
            for index, path in enumerate(paths):
                paths_iter = []
                i = 0
                if len(path)>3:
                # while i < len(path)-2:
                    while i < len(path)-2:
                    # if len(path)>3:
                        if i == 0:
                            line = LineString([path[i],path[i+1],path[i+2],path[i+3]])
                            linering = LinearRing([path[i],path[i+1],path[i+2],path[i+3]])

                            if linering.is_ccw:
                                line = line.parallel_offset(self.graph_data.width/2.1,'left')
                                line2 = LineString(line.coords)
                                line2 = line2.parallel_offset(self.graph_data.width/2.1, 'right')
                                coords = list(line2.coords[::-1])
                                paths_iter = paths_iter + coords[0:-1]
                                
                            else:
                                line = line.parallel_offset(self.graph_data.width/2.1,'right')
                                line2 = LineString(line.coords)
                                line2 = line2.parallel_offset(self.graph_data.width/2.1, 'right')
                                coords = list(line2.coords)
                                paths_iter = paths_iter + coords[0:-1]
                            
                            i = i+3
                            if i+3>len(path):
                                k = deepcopy(i)
                                while k<len(path):
                                    paths_iter.append(path[k])
                                    # print(f'paths iter looks: {paths_iter}')
                                    k = k+1
                        else:
                            # print(f'focking i is: {i}')
                            line = LineString([paths_iter[-1], path[i], path[i+1], path[i+2]])
                            linering = LinearRing([paths_iter[-1],path[i], path[i+1], path[i+2]])

                            if linering.is_ccw:
                                line = line.parallel_offset(self.graph_data.width/2.1,'left')
                                line2 = LineString(line.coords)
                                line2 = line2.parallel_offset(self.graph_data.width/2.1, 'right')
                                coords = list(line2.coords[::-1])
                                paths_iter = paths_iter + coords[0:-1]
                                
                            else:
                                line = line.parallel_offset(self.graph_data.width/2.1,'right')
                                line2 = LineString(line.coords)
                                line2 = line2.parallel_offset(self.graph_data.width/2.1, 'right')
                                coords = list(line2.coords)
                                paths_iter = paths_iter + coords[0:-1]                            
                            
                            i = i+2

                            if i+2>len(path):
                                k = deepcopy(i)
                                while k<len(path):
                                    paths_iter.append(path[k])
                                    # print(f'paths iter looks: {paths_iter}')
                                    k = k+1
                else:
                    paths_iter = paths_iter + path
                paths_exo.append(paths_iter)
                # print(f'paths to print looks: {paths_exo}')


            #VYHLAZENI CELE CESTY`
            for i in range(len(paths_exo)-1):
                path = paths_exo[i]
                path_next = paths_exo[i+1]
                path_b = paths_m[i]

                path_pre = []
                path_past = []

                line = LineString([path[-2], path_b[0], path_b[1]])
                linering = LinearRing([path[-2], path_b[0], path_b[1]])

                if linering.is_ccw:
                    line1 = line.parallel_offset(self.graph_data.width/2.2,'left')
                    if len(line1.coords)>1:
                        line2 = LineString(line1.simplify(0).coords)
                        line2 = line2.parallel_offset(self.graph_data.width/2.2, 'right')
                        coords = list(line2.coords[::-1])
                    else:
                        coords = list(line.coords)
                    path_past = path_past + coords
                else:
                    line1 = line.parallel_offset(self.graph_data.width/2.2,'right')
                    if len(line1.coords)>1:
                        line2 = LineString(line1.simplify(0).coords)
                        line2 = line2.parallel_offset(self.graph_data.width/2.2, 'right')
                        coords = list(line2.coords)
                    else:
                        coords = list(line.coords)
                    path_past = path_past + coords


                path_b = path_past + path_b[2:]

                line = LineString([path_b[-2], path_b[-1], path_next[1]])
                linering = LinearRing([path_b[-2], path_b[-1], path_next[1]])

                if linering.is_ccw:
                    line1 = line.parallel_offset(self.graph_data.width/2.2,'left')
                    if len(line1.coords)>1:
                        line2 = LineString(line1.simplify(0).coords)
                        line2 = line2.parallel_offset(self.graph_data.width/2.2, 'right')
                        coords = list(line2.coords[::-1])
                    else:
                        coords = list(line.coords)
                    path_pre = path_pre + coords
                else:
                    line1 = line.parallel_offset(self.graph_data.width/2.2,'right')
                    if len(line1.coords)>1:
                        line2 = LineString(line1.simplify(0).coords)
                        line2 = line2.parallel_offset(self.graph_data.width/2.2, 'right')
                        coords = list(line2.coords)
                    else:
                        coords = list(line.coords)
                    path_pre = path_pre + coords


                path_b = path_b[:-2] + path_pre

                paths_exo[i].pop(-1)
                paths_exo[i].append(path_b[1])
                

                paths_exo[i+1].pop(0)
                paths_exo[i+1].insert(0, path_b[-2])

                path_b.pop(0)
                path_b.pop(-1)

                paths_m[i] = path_b








            #KONEC THREADU
            ##############

            
            # percentage = ((final_val - exact_val)/(max_val - exact_val))*100
            # print(f'percentage difference: {round(percentage,2)}')
            colors = []
            for i in range(100):
                colors.append(list(np.random.choice(range(255), size=3)))
            self.colors = colors

            colors = self.colors

            for index, p in enumerate(paths_exo):
                self.plot_path(p, self.colors[index], 4)
            
            # output_points = []
            # for index, path in enumerate(paths):
            #     # self.plot_path(path, colors[index], 2)
            #     # self.plot_upper(path[0], [0,150,0])
            #     # self.plot_upper(path[-1], [150,0,0])
            #     if index < (len(paths)-1):
            #         points = [paths[index][-1], paths[index+1][0]]
            #         # self.plot_crossing(points,[150,0,0])
            #         # self.test_plot_lines(points, node_graph)
            
            # # print(f'paths_m {paths_m}')

            for index, path_m in enumerate(paths_m):
            #     # self.plot_path(path_m, self.colors[index], 5)
                self.plot_path(path_m, [0,0,150], 4)
            
            self.plot_first(paths[0][0], [0,150,0])
            self.plot_last(paths[-1][-1], [150,0,0])

    def plot_parallels(self, areas):
        colors = self.colors
        for i in range(len(areas)):
            parallels = areas[i]
            color = colors[i]
            for k in range(len(parallels)):
                parallel = parallels[k]
                self.plot((parallel.upper_point[0],parallel.lower_point[0]),(parallel.upper_point[1],parallel.lower_point[1]) , color, "plot_parallels")

    def clustering_finished(self, cluster_thread):
        self.plot_parallels(cluster_thread.areas.areas)
        # self.plot_parallel_clean(cluster_thread.tracks.paralels, [0,150,0], 3)
        # self.plot_parallel_upper(cluster_thread.tracks.paralels, [0,150,0])
        self.parallels_plot = cluster_thread.areas.areas
        self.tracks = cluster_thread.tracks.paralels

        # print(f'tracks looks: {self.tracks}')

        self.cl_graph = cluster_thread.graph
        self.cl_width = cluster_thread.width
        self.cl_areas = cluster_thread.areas

        self.visibility_thread = VisibilityGraphThread(cluster_thread.graph, cluster_thread.width, cluster_thread.areas)
        self.visibility_thread.start()
        self.visibility_thread.finished.connect(lambda: self.visibility_graph_finished(self.visibility_thread))
        
    def visibility_graph_finished(self, vis_thread):
        # print('Dodelal jsem visibility thread')
        trd = vis_thread
        self.ga_graph = trd.graph
        self.ga_width = trd.width
        self.ga_areas = trd.areas
        self.ga_node_graph = trd.node_graph
        # self.tracks = trd.tracks

        self.genetic_thread = GeneticThread(trd.graph, trd.width, trd.areas, trd.node_graph)
        self.genetic_thread.finished.connect(lambda: self.genetic_finished(self.genetic_thread))
        self.genetic_thread.start()
        
        self.contentFrame.startButton.setText('Start *NEW* plot')

    def genetic_finished(self, genetic_thread):
        ga = genetic_thread
        clean_plot = PlotThread(self.contentFrame)
        self.contentFrame.calculateGA.show()
        clean_plot.finished.connect(lambda: self.algorithm_finished(ga.seq, ga.areas, ga.node_graph))
        clean_plot.start()
        self.contentFrame.calculateGA.show()
        # self.stopSimulation()


    def plot_deleted(self):
        # self.genetic_thread_a.start()
        # print(f'tracks looks: {self.tracks}')
        # print(f'tracks looks: {self.tracks.paralels}')
        for paralel in self.tracks.paralels:
            self.plot(paralel[0],paralel[1], [0,150,0], 'plot')
        self.contentFrame.previewButton.setDisabled(False)

        # for upper in self.tracks.upper:
        #     # print(f'upper point: {upper.point}')
        #     self.plot_upper(upper.point, [0,150,0])

    def deleted_compute(self):
        # self.plot_deleted()
        self.plot_parallels(self.cl_areas.areas)
        self.contentFrame.previewButton.setDisabled(False)
        # self.compute_ga_vis()
        self.compute_ga_gen()


    def compute_ga_vis(self):
        self.visibility_thread_a = VisibilityGraphThread(self.cl_graph, self.cl_width, self.cl_areas)
        self.visibility_thread_a.finished.connect(lambda: self.compute_ga_gen(self.visibility_thread_a))
        self.visibility_thread_a.start()

    # def compute_ga_gen(self, vis):
    #     if vis.node_graph:
    #         self.genetic_thread_a = GeneticThread(vis.graph, vis.width, vis.areas, vis.node_graph)
    #         self.genetic_thread_a.finished.connect(lambda: self.genetic_finished(self.genetic_thread_a))
    #         self.genetic_thread_a.start()
    #     else:
    #         self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.settingsMenu)
    def compute_ga_gen(self):
        self.genetic_thread_a = GeneticThread(self.ga_graph, self.ga_width, self.ga_areas, self.ga_node_graph)
        self.genetic_thread_a.finished.connect(lambda: self.genetic_finished(self.genetic_thread_a))
        self.genetic_thread_a.start()

    def compute_ga(self):
        
        self.contentFrame.previewButton.setDisabled(True)
        self.delete_plot = PlotThread(self.contentFrame)
        # self.genetic_thread_a = GeneticThread(self.ga_graph, self.ga_width, self.ga_areas, self.ga_node_graph)
        
        
        self.delete_plot.finished.connect(lambda: self.deleted_compute())
        # self.genetic_thread_a.finished.connect(lambda: self.genetic_finished(self.genetic_thread_a))
        self.delete_plot.start()
        # self.contentFrame.graphWidget.clear()
        

        self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.stopSimulationWidget)
        self.headerFrame.advancedOptions.setDisabled(True)
        self.headerFrame.backButton.setDisabled(True)


        # self.genetic_thread_a.start()

        
    def plot_inner_outer(self):
        graph = self.graph_data

        self.plot(graph.outer_plot[0],graph.outer_plot[1], 'b', 'plot')
        # self.plot_second(graph.outer_plot[0],graph.outer_plot[1], 'b', 'outer')

        for i in range(len(graph.inner_plot)):
            self.plot(graph.inner_plot[i][0], graph.inner_plot[i][1], 'r', 'plot')

        
        pass


    def set_complete_file(self):
        self.delete_graph()  
        graph = self.graph_data
        width = graph.width
        # self.stopSimulation()

        if(self.get_graph_data()):
            graph.get_outer_inner()

            self.plot_inner_outer()

            # self.plot(graph.outer_plot[0],graph.outer_plot[1], 'b', 'outer')
            # # self.plot_second(graph.outer_plot[0],graph.outer_plot[1], 'b', 'outer')

            # for i in range(len(graph.inner_plot)):
            #     self.plot(graph.inner_plot[i][0], graph.inner_plot[i][1], 'r', 'inner'+str(i))

            # self.compThread = ComputationalThread(graph, width)
            # self.compThread.start()
            # self.compThread.finished.connect(lambda: self.algorithm_finished(self.compThread.seq, self.compThread.areas, self.compThread.node_graph))
            print(f'width is: {width}')
            self.clustering_thread = ClusteringThread(graph, width)
            self.clustering_thread.start()
            self.clustering_thread.finished.connect(lambda: self.clustering_finished(self.clustering_thread))

            self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.stopSimulationWidget)
            self.headerFrame.advancedOptions.setDisabled(True)

    def from_points_to_coords(self, n1_state, n2_state, node_graph):
        ind1 = node_graph.node_states.index(n1_state)
        ind2 = node_graph.node_states.index(n2_state)
        # print(f'Path between is : {node_graph.move_between_paths[ind1][ind2]}')
        points = node_graph.move_between_paths[ind1][ind2]
        return points

    def test_plot_lines(self, points, node_graph):
        point1 = points[0]
        point2 = points[1]

        for i in range(len(node_graph.test_lines)):
            line = node_graph.test_lines[i]
            if line[0] == point1:
                coords = line[1]
                if coords:
                    print(f'dostal jsem se tady')
                    self.plot_crossing([[coords[0][0],coords[1][0]],[coords[0][1],coords[1][1]]])

        
        pass

    def switch_seq(self, areas, nodes, node_graph):
        paths = []
        states = []
        paths_interstate = []
        for i in range(len(nodes)):
            node = nodes[i]
            for j in range(len(areas)):
                for k in range(len(areas[j].node_states)):
                    if node.state == areas[j].node_states[k]:
                        paths.append(areas[j].paths[k])
                        # print(f'original paths: {paths}')
                        if i < len(nodes)-1:
                            points = self.from_points_to_coords(nodes[i].state,nodes[i+1].state, node_graph)
                            paths_interstate.append([(point.x,point.y) for point in points])
                        states.append(areas[j].node_states[k])
        return paths, states, paths_interstate






    #looks good
    def get_graph_data(self):
        #add last opened location - if it is possible
        home_dir = str(Path.cwd()) + "/maps"
        fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir)
        if fname[0]:
            self.graph_data.set_coords(fname[0])

            name = []
            for i in range(len(fname[0])):
                name.append(fname[0][i])

            name = name[::-1]
            # print(f"backwards name of file: {name}")
            file_name = []
            for i in name:
                if i != '/':
                    file_name.append(i)
                else:
                    break
            str1 = ''
            file_name = file_name[::-1]
            for i in file_name:
                # print(f"iteration of file_name : {i}")
                str1 += i
                # print(f"str1 lookalike: {str1}")

            # print(f"filename end: {str1}")

            self.headerFrame.infoTable.fileName.setText(str1)
            return fname[0]
        else:
            return None

    #not used
    def update(self):
        pass

    #looks good
    def get_desktop_geometry(self):
        width = QDesktopWidget().screenGeometry().width()
        height = QDesktopWidget().screenGeometry().height()
        return width, height

    #looks good
    def get_window_geometry(self):
        width = self.geometry().width()
        height = self.geometry().height()
        return width, height

    #looks good
    def set_location(self):
        screen_width, screen_height = self.get_desktop_geometry()
        window_width, window_height = self.get_window_geometry()
        x = int((screen_width - window_width)/2)
        y = int((screen_height - window_height)/2)
        self.move(x, y)

    #looks good
    def plot(self, x, y, color, name):
        pen = pg.mkPen(color=color, width=3)
        self.contentFrame.graphWidget.plot(x, y, name=name, pen=pen)

    def plot_second(self, x, y, color, name):
        pen = pg.mkPen(color=color, width=2)
        self.contentFrame.graphWidget2.plot(x, y, name=name, pen=pen)

    def plot_upper_second(self ,point, color):
        # print(f"tady to dojde : {point[0]}")
        # pen = pg.mkPen(color="r")
        self.contentFrame.graphWidget2.plot([point[0]],[point[1]], name="plot_upper_second", pen=None, symbol='o', symbolPen=pg.mkPen(color=color, width=0), symbolBrush=pg.mkBrush(color),symbolSize=7)


    def plot_upper(self ,point, color):
        # print(f"tady to dojde : {point[0]}")
        # pen = pg.mkPen(color="r")
        self.contentFrame.graphWidget.plot([point[0]],[point[1]], name="plot_upper", pen=None, symbol='o', symbolPen=pg.mkPen(color=color, width=0), symbolBrush=pg.mkBrush(color),symbolSize=10)

    def plot_first(self, point, color):
        self.contentFrame.graphWidget.plot([point[0]],[point[1]], pen=None, symbol='o', symbolPen=pg.mkPen(color=color, width=0), symbolBrush=pg.mkBrush(color),symbolSize=15, name='plot_first')

    def plot_last(self, point, color):
        self.contentFrame.graphWidget.plot([point[0]],[point[1]], pen=None, symbol='o', symbolPen=pg.mkPen(color=color, width=0), symbolBrush=pg.mkBrush(color),symbolSize=15, name='plot_last')
    
    def plot_state(self, point, color):
        pass

    def plot_parallel_clean(self, parallels, color, width):
        for line in parallels:
            x = line[0]
            y = line[1]
            pen = pen = pg.mkPen(color=color, width=width)
            self.contentFrame.graphWidget.disableAutoRange()
            self.contentFrame.graphWidget.plot(x,y,name='plot_path', pen=pen)
    
    def plot_parallel_upper(self,parallels,color):
        for line in parallels:
            point = [line[0][1],line[1][1]]
            self.contentFrame.graphWidget.plot([point[0]],[point[1]], pen=None, symbol='o', symbolPen=pg.mkPen(color=color, width=0), symbolBrush=pg.mkBrush(color),symbolSize=15, name='plot_first')
        pass

    def plot_path(self, points, color, width):
        x = []
        y = []
        for i in range(len(points)):
            x.append(points[i][0])
            y.append(points[i][1])
        pen = pen = pg.mkPen(color=color, width=width)
        self.contentFrame.graphWidget.disableAutoRange()
        self.contentFrame.graphWidget.plot(x,y,name='plot_path', pen=pen)

    def plot_crossing(self, points, color):
        x = []
        y = []
        for i in range(len(points)):
            x.append(points[i][0])
            y.append(points[i][1])
        pen = pen = pg.mkPen(color=color, width=4)
        self.contentFrame.graphWidget.plot(x,y,name='plot_crossing', pen=pen)

    def delete_computed(self):
        for item in self.contentFrame.graphWidget.listDataItems():
            if item.name() == 'plot_path' or 'plot_first' or 'plot_last' or 'plot_upper' or 'plot_crossing':
                self.contentFrame.graphWidget.removeItem(item)
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
