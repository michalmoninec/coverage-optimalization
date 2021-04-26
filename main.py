from os import name
from random import sample
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
from scripts.computational_thread import ClusteringThread, ComputationalThread, GeneticThread, VisibilityGraphThread

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
        content.calculateGA.clicked.connect(self.compute_ga)

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
            if ',' in text:
                out_text = text.replace(',','.')
                # print(f"changed text: {out_text}")
                # return text
            else:
                out_text = text
            self.graph_data.setWidth(float(out_text))

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
        pass
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
            print(f'genetic best solution: {final_val}')
            # print(f'Time needed for GA: {time_genetic}')
            paths, states, paths_m = self.switch_seq(areas_nodes, final_seq, node_graph)

            #KONEC THREADU
            ##############


            # percentage = ((final_val - exact_val)/(max_val - exact_val))*100
            # print(f'percentage difference: {round(percentage,2)}')
            colors = []
            for i in range(100):
                colors.append(list(np.random.choice(range(255), size=3)))
            self.colors = colors

            colors = self.colors
            
            output_points = []
            for index, path in enumerate(paths):
                self.plot_path(path, colors[index], 2)
                self.plot_upper(path[0], [0,150,0])
                self.plot_upper(path[-1], [150,0,0])
                if index < (len(paths)-1):
                    points = [paths[index][-1], paths[index+1][0]]
                    self.plot_crossing(points,[150,0,0])
                    # self.test_plot_lines(points, node_graph)
            
            # print(f'paths_m {paths_m}')
            for path_m in paths_m:
                self.plot_path(path_m, [0,0,150], 5)
            
            self.plot_first(paths[0][0], [0,150,0])
            self.plot_last(paths[-1][-1], [150,0,0])



    def clustering_finished(self, cluster_thread):
        colors = self.colors
        for i in range(len(cluster_thread.areas.areas)):
            parallels = cluster_thread.areas.areas[i]
            color = colors[i]
            for k in range(len(parallels)):
                parallel = parallels[k]
                self.plot((parallel.upper_point[0],parallel.lower_point[0]),(parallel.upper_point[1],parallel.lower_point[1]) , color, "plot")

        self.visibility_thread = VisibilityGraphThread(cluster_thread.graph, cluster_thread.width, cluster_thread.areas)
        self.visibility_thread.start()
        self.visibility_thread.finished.connect(lambda: self.visibility_graph_finished(self.visibility_thread))
        
    def visibility_graph_finished(self, vis_thread):
        print('Dodelal jsem visibility thread')
        trd = vis_thread
        self.ga_graph = trd.graph
        self.ga_width = trd.width
        self.ga_areas = trd.areas
        self.ga_node_graph = trd.node_graph

        self.genetic_thread = GeneticThread(trd.graph, trd.width, trd.areas, trd.node_graph)
        self.genetic_thread.start()
        self.genetic_thread.finished.connect(lambda: self.genetic_finished(self.genetic_thread))
        self.contentFrame.startButton.setText('Start *NEW* plot')

    def genetic_finished(self, genetic_thread):
        print('Dodelal jsem aji genetak, to jsem pasak.')
        ga = genetic_thread
        self.algorithm_finished(ga.seq, ga.areas, ga.node_graph)
        self.contentFrame.calculateGA.show()

    def compute_ga(self):
        
        self.contentFrame.contentStack.setCurrentWidget(self.contentFrame.stopSimulationWidget)
        self.headerFrame.advancedOptions.setDisabled(True)

        self.genetic_thread = GeneticThread(self.ga_graph, self.ga_width, self.ga_areas, self.ga_node_graph)
        self.genetic_thread.finished.connect(lambda: self.genetic_finished(self.genetic_thread))
        self.genetic_thread.start()


        
        # self.delete_computed()



    def set_complete_file(self):
        self.delete_graph()  
        graph = self.graph_data
        width = graph.width

        if(self.get_graph_data()):
            graph.get_outer_inner()

            self.plot(graph.outer_plot[0],graph.outer_plot[1], 'b', 'outer')
            # self.plot_second(graph.outer_plot[0],graph.outer_plot[1], 'b', 'outer')

            for i in range(len(graph.inner_plot)):
                self.plot(graph.inner_plot[i][0], graph.inner_plot[i][1], 'r', 'inner'+str(i))

            # self.compThread = ComputationalThread(graph, width)
            # self.compThread.start()
            # self.compThread.finished.connect(lambda: self.algorithm_finished(self.compThread.seq, self.compThread.areas, self.compThread.node_graph))

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
        pen = pg.mkPen(color=color, width=2)
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
