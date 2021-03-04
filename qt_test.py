from graph import GraphData
from paralel_tracks import ParalelTracks
# from components.infoTable import InfoTable
from components.pushButton import PushButton
from components.header import HeaderWidget
from components.content import ContentWidget

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
        for item in self.contentFrame.graphWidget.listDataItems():
            self.contentFrame.graphWidget.removeItem(item)

    #check data types
    def set_complete_file(self): 
        self.delete_graph()  
        graph = self.graph_data
        width = graph.width
        coef = graph.coef

        if(self.get_graph_data()):
            graph.get_outer_inner()

            self.plot(graph.outer_plot[0],graph.outer_plot[1], 'b', 'outer')

            for i in range(len(graph.inner_plot)):
                self.plot(graph.inner_plot[i][0], graph.inner_plot[i][1], 'r', 'inner'+str(i))

            # tracks = ParalelTracks(graph.outer, graph.inner, 1)
            tracks = ParalelTracks(graph.outer, graph.inner, width, graph.angle)
            tracks.getUpperPoints()

            arr = []
            for i in range(len(tracks.upper)):
                arr.append((tracks.upper[i].point))
            clusters = cluster(arr, width, coef)
            number_of_clusters = str(max(clusters))
            self.headerFrame.infoTable.countOfClusters.setText(number_of_clusters)
            # print(f"Clusters looks like this: {clusters}")
            # clusters = cluster(arr, width)
            # print(f"Clusters looks like this: {clusters}")

            colors = []
            for i in range(max(clusters)):
                colors.append(list(np.random.choice(range(256), size=3)))
            # print(f"Focking colors are: {colors}")

            for i in range(len(tracks.paralels)):
                self.plot_upper(tracks.upper[i].point)

            for i in range(len(tracks.paralels)):
                # self.plot(tracks.paralels[i][0],tracks.paralels[i][1], 'k', 'paralels'+str(i))
                # print(f"cluster inner: {clusters[i]}")
                color = colors[clusters[i]-1]
                self.plot(tracks.paralels[i][0],tracks.paralels[i][1], color, 'paralels'+str(i))



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
        pen = pg.mkPen(color=color)
        self.contentFrame.graphWidget.plot(x, y, name=name, pen=pen)

    def plot_upper(self,point):
        # print(f"tady to dojde : {point[0]}")
        # pen = pg.mkPen(color="r")
        self.contentFrame.graphWidget.plot([point[0]],[point[1]], name="another", pen=None, symbol='o', symbolPen=pg.mkPen(color=(0, 0, 255), width=0),symbolBrush=pg.mkBrush(0, 0, 255, 255),symbolSize=7)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
