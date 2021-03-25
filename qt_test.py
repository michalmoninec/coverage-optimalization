from graph import GraphData
from paralel_tracks import ParalelTracks
# from components.infoTable import InfoTable
from components.pushButton import PushButton
from components.header import HeaderWidget
from components.content import ContentWidget

from scripts.xmeans import xmeans_clustering
from scripts.sub_areas import Areas

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QFileDialog, \
    QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, QFrame, QRadioButton, QStackedWidget, \
    QStackedLayout, QLabel, QSizePolicy, QGraphicsDropShadowEffect, QGroupBox, QFormLayout, QLineEdit, QComboBox, QSpinBox
from PyQt5.QtCore import Qt, QTimer, QRegExp
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator, QRegExpValidator

from pathlib import Path
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import numpy as np

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
        

        self.setStyleSheet(style)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        ########################HEADER##############################
        self.headerFrame = HeaderWidget()
        header = self.headerFrame
        header.settingsButton.clicked.connect(self.showsettings)
        header.deleteGraphButton.clicked.connect(self.delete_graph_items)
        header.backButton.clicked.connect(self.backtograph)
        header.backButton.setEnabled(False)        
        ######################################################
        
        self.contentFrame = ContentWidget()
        content = self.contentFrame
        self.widthInputCheck(content.widthInput.text())
        self.threshInputCheck(content.threshInput.text())
        self.angleInputCheck(content.angleInput.text())

        content.startButton.clicked.connect(self.set_complete_file)
        content.widthInput.textChanged.connect(lambda text: self.widthInputCheck(text))
        content.threshInput.textChanged.connect(lambda text: self.threshInputCheck(text))
        content.angleInput.textChanged.connect(lambda text: self.angleInputCheck(text))
        ######################################################


        layout.addWidget(self.headerFrame)
        layout.addWidget(self.contentFrame,1)

        self.setLayout(layout)
        self.set_location()
        self.show()

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
        # for item in self.contentFrame.graphWidget.listDataItems():
        #     self.contentFrame.graphWidget.removeItem(item)
        self.contentFrame.graphWidget.clear()
        self.contentFrame.graphWidget2.clear()

    #check data types
    def set_complete_file(self): 
        self.delete_graph()  
        graph = self.graph_data
        width = graph.width

        if(self.get_graph_data()):
            graph.get_outer_inner()

            self.plot(graph.outer_plot[0],graph.outer_plot[1], 'b', 'outer')
            self.plot_second(graph.outer_plot[0],graph.outer_plot[1], 'b', 'outer')

            for i in range(len(graph.inner_plot)):
                self.plot(graph.inner_plot[i][0], graph.inner_plot[i][1], 'r', 'inner'+str(i))
                self.plot_second(graph.inner_plot[i][0], graph.inner_plot[i][1], 'r', 'inner'+str(i))


            # print(f'graph outer: {graph.outer}')
            # print(f"graph inner : {graph.inner}")
            tracks = ParalelTracks(graph.outer, graph.inner, width, graph.angle)
            # print(f"tracks lookalike: {tracks.paralels}")
            tracks.getUpperPoints()

            arr = []
            input_arr = []

            for i in range(len(tracks.upper)):
                arr.append((tracks.upper[i].point))
                input_arr.append([tracks.upper[i].point[0],tracks.upper[i].point[1]])


            clusters, clusters_count, centers = xmeans_clustering(input_arr, 5)

            objects = [graph.outer]
            for item in graph.inner:
                objects.append(item)

            areas = Areas(tracks.paralels, clusters, objects)

            areas_after_change = areas.split_by_different_objects()
            areas_after_check2 = areas.check_neighbours()

            colors = []
            # for i in range(len(areas_after_change)):
            #     colors.append(list(np.random.choice(range(255), size=3)))

            for i in range(len(areas_after_check2)):
                colors.append(list(np.random.choice(range(255), size=3)))

            # sub_areas = get_sub_areas(tracks.paralels, clusters, self.plot, self.plot_upper)
            objects = [graph.outer]
            for item in graph.inner:
                objects.append(item)

            # for i in range(len(areas.areas[0])):
            #     parallel = areas.areas[0][i]
            #     # print(f"upper point group of parallel is: {parallel.upper_group}")
            #     # print(f"lower point group of parallel is: {parallel.lower_group}")
            #     self.plot_upper(parallel.upper_point, [255,255,255])
            #     self.plot_second((parallel.upper_point[0],parallel.lower_point[0]),(parallel.upper_point[1],parallel.lower_point[1]) , [0,0,0], "plot")




            # print(f"number of post processed clusters: {len(areas_after_change)}")
            # for i in range(len(areas_after_change)):
            #     area = areas_after_change[i]
            #     for k in range(len(area)):
            #         parallel = area[k]
            #         self.plot_second((parallel.upper_point[0],parallel.lower_point[0]),(parallel.upper_point[1],parallel.lower_point[1]) , colors[i], "plot")
            #         self.plot_upper_second(parallel.upper_point, colors[i])
            
            print(f"number of post processed clusters: {len(areas_after_check2)}")
            for i in range(len(areas_after_check2)):
                area = areas_after_check2[i]
                for k in range(len(area)):
                    parallel = area[k]
                    self.plot_second((parallel.upper_point[0],parallel.lower_point[0]),(parallel.upper_point[1],parallel.lower_point[1]) , colors[i], "plot")
                    self.plot_upper_second(parallel.upper_point, colors[i])


            for i in range(clusters_count):
                color = colors[i]
                for k in range(len(clusters[i])):
                    self.plot(tracks.paralels[clusters[i][k]][0],tracks.paralels[clusters[i][k]][1], color, "plot")
                    # self.plot_second(tracks.paralels[clusters[i][k]][0],tracks.paralels[clusters[i][k]][1], color, "plot")
                    self.plot_upper(tracks.upper[clusters[i][k]].point, color)
                    # self.plot_upper_second(tracks.upper[clusters[i][k]].point, color)
                    self.plot_center(centers[i], color)

            # for i in range(len(areas.areas[0])):
            #     parallel = areas.areas[0][i]
            #     print(f"upper point of parallel is: {parallel.upper_point}")
            #     self.plot_upper(parallel.upper_point, [255,255,255])


            # print(f'paralel tracks: {tracks.paralels}')

            self.backtograph()
            self.headerFrame.deleteGraphButton.setDisabled(False)
            self.headerFrame.backButton.setDisabled(False)
            self.contentFrame.graphWidget.getViewBox().enableAutoRange()

            

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
        self.contentFrame.graphWidget2.plot([point[0]],[point[1]], name="another", pen=None, symbol='o', symbolPen=pg.mkPen(color=color, width=0), symbolBrush=pg.mkBrush(color),symbolSize=7)


    def plot_upper(self ,point, color):
        # print(f"tady to dojde : {point[0]}")
        # pen = pg.mkPen(color="r")
        self.contentFrame.graphWidget.plot([point[0]],[point[1]], name="another", pen=None, symbol='o', symbolPen=pg.mkPen(color=color, width=0), symbolBrush=pg.mkBrush(color),symbolSize=7)

    def plot_center(self, point, color):
        self.contentFrame.graphWidget.plot([point[0]],[point[1]], pen=None, symbol='+', symbolPen=pg.mkPen(color=color, width=0), symbolBrush=pg.mkBrush(color),symbolSize=10)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
