from graph import GraphData
from paralel_tracks import ParalelTracks

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, QFrame, QRadioButton, QStackedWidget, QStackedLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import QIcon
from pathlib import Path
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
from copy import deepcopy

from hirearchial_clustering import hierarichial_cluster as cluster




class PushButton(QtGui.QPushButton):
    def __init__(self, parent=None):
      super(PushButton, self).__init__(parent)
      self.setStyleSheet('background-color: darkgray; border-radius: 5px; height: 50px; width: 100px')
    #   self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
      self.setFixedSize(100,50)

class RadioButton(QtGui.QRadioButton):
    def __init__(self,parent=None):
        super(RadioButton, self).__init__(parent)
        self.selected = False
        self.toggled.connect(self.button_toggled)

    def button_toggled(self, selected):
        self.selected = selected

class InputMethod(QtGui.QHBoxLayout):
    def __init__(self, parent=None):
        super(InputMethod, self).__init__(parent)
        self.rb_one_file = RadioButton('Input from one file')
        self.rb_one_file.setChecked(True)
        self.rb_seperated_files = RadioButton('Input separatedly')
        self.input_label = QLabel('Choose input options:')
        self.addWidget(self.input_label)
        self.addWidget(self.rb_one_file)
        self.addWidget(self.rb_seperated_files)

class InputSingleFile(QWidget):
    def __init__(self, parent=None):
        super(InputSingleFile, self).__init__(parent)
        layout = QHBoxLayout()
        self.selectFile = PushButton('Choose file')
        layout.addWidget(self.selectFile)
        self.changeGraph = PushButton('Delete data')
        layout.addWidget(self.changeGraph)
        self.setLayout(layout)

class InputSeparatedFiles(QWidget):
    def __init__(self, parent=None):
        super(InputSeparatedFiles, self).__init__(parent)
        layout = QHBoxLayout(parent)
        self.selectOuter = PushButton('Choose outer')
        self.selectInner = PushButton('Choose inner')
        layout.addWidget(self.selectOuter)
        layout.addWidget(self.selectInner)
        self.setLayout(layout)

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.graph_data = GraphData(None)
        title = 'Foking automower'

        self.setWindowTitle(title)
        self.setGeometry(0, 0, 1000, 600)
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

        self.headerFrame = QFrame(self)
        self.headerFrame.setStyleSheet('''
        background-color: magenta;
        ''')


        
        self.settingsArea = QHBoxLayout(self.headerFrame)
        # self.settingsArea.setSpacing(0)
        self.settingsArea.setAlignment(Qt.AlignLeft)

        self.settingsToggle = QStackedWidget()

        self.settingsButton = PushButton('Settings')
        self.settingsButton.clicked.connect(self.showsettings)

        # self.settingsButton.setAlignment(Qt.AlignRight)
        
 

        self.backButton = PushButton("Back to graph")
        self.backButton.clicked.connect(self.backtograph)

        
        # self.backButton.setAlignment(Qt.AlignRight)

        self.settingsToggle.addWidget(self.settingsButton)
        self.settingsToggle.addWidget(self.backButton)

        # self.settingsArea.setAlignment(Qt.AlignRight)
        self.settingsArea.addStretch(1)
        self.settingsArea.addWidget(self.settingsToggle)
        # self.settingsArea.addStretch(1)

        self.contentFrame = QFrame()
        self.contentFrame.setStyleSheet('background: green;')

        self.contentLayout = QHBoxLayout(self.contentFrame)
        self.contentLayout.setContentsMargins(0,0,0,0)

        self.contentStack = QStackedLayout()
        # self.contentStack.setSpacing(0)
        


        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setAspectLocked()
        self.graphWidget.getPlotItem().hideAxis('bottom')
        self.graphWidget.getPlotItem().hideAxis('left')
        self.graphWidget.setMenuEnabled(False)
        self.graphWidget.setStyleSheet('''
        border: 5px solid blue;
        ''')
        self.graphWidget.setBackground(None)

        self.settingsMenu = QWidget()
        self.settingsWrapper = QWidget()
        settingsWrapperLayout = QHBoxLayout()
        settingsLayout = QVBoxLayout()

        
        # self.startButton = QLabel('Plot the fucking area!')
        # self.startButton.setAlignment(Qt.AlignHCenter)
        # self.startButton.setAlignment(Qt.AlignCenter)

        self.startButton = PushButton('Start fucking ploting')
        self.startButton.clicked.connect(self.set_complete_file)
        self.testButton = PushButton("fockkin")

        # settingsLayout.addStretch(1)
        settingsLayout.addWidget(self.startButton)
        settingsLayout.addWidget(self.testButton)
        # settingsLayout.addStretch(1)
        

        settingsWrapperLayout.addStretch(1)
        settingsWrapperLayout.addLayout(settingsLayout)
        settingsWrapperLayout.addStretch(1)

        self.settingsMenu.setLayout(settingsWrapperLayout)


        self.contentStack.addWidget(self.graphWidget)
        self.contentStack.addWidget(self.settingsMenu)

        self.contentLayout.addLayout(self.contentStack)


        layout.addWidget(self.headerFrame)
        layout.addWidget(self.contentFrame,1)

        self.setLayout(layout)
        self.set_location()

        

        self.show()

    def backtograph(self):
        print('Helo there')
        self.settingsToggle.setCurrentWidget(self.settingsButton)
        self.contentStack.setCurrentWidget(self.graphWidget)

    def showsettings(self):
        print('General Kenobi')
        self.settingsToggle.setCurrentWidget(self.backButton)
        self.contentStack.setCurrentWidget(self.settingsMenu)


    #remove outer bounds 
    def change_graph (self):
        self.graph_data.set_default()
        print(self.graphWidget)
        print(self.graphWidget.listDataItems()[0])
        for item in self.graphWidget.listDataItems():
            # if item.name() == 'outer':
            self.graphWidget.removeItem(item)

    #check data types
    def set_complete_file(self):    
        graph = self.graph_data

        if(self.get_graph_data()):
            graph.get_outer_inner()

            self.plot(graph.outer_plot[0],graph.outer_plot[1], 'b', 'outer')

            for i in range(len(self.graph_data.inner_plot)):
                self.plot(self.graph_data.inner_plot[i][0], self.graph_data.inner_plot[i][1], 'r', 'inner'+str(i))

            tracks = ParalelTracks(self.graph_data.outer, self.graph_data.inner, 0.5)
            tracks.getUpperPoints()
            
            
            for i in range(len(tracks.paralels)):
                self.plot_upper(tracks.upper[i].point)

            for i in range(len(tracks.paralels)):
                self.plot(tracks.paralels[i][0],tracks.paralels[i][1], 'k', 'paralels'+str(i))

            arr = []
            for i in range(len(tracks.upper)):
                arr.append((tracks.upper[i].point))
            cluster(arr)

            #tady nastavit, ze to ma prehodit obe okna
            self.backtograph()

            

    #looks good
    def get_graph_data(self):
        #add last opened location - if it is possible
        home_dir = str(Path.cwd()) + "/maps"
        fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir)
        if fname[0]:
            self.graph_data.set_coords(fname[0])
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
        self.graphWidget.plot(x, y, name=name, pen=pen)

    def plot_upper(self,point):
        # print(f"tady to dojde : {point[0]}")
        # pen = pg.mkPen(color="r")
        self.graphWidget.plot([point[0]],[point[1]], name="another", pen=None, symbol='o', symbolPen=pg.mkPen(color=(0, 0, 255), width=0),symbolBrush=pg.mkBrush(0, 0, 255, 255),symbolSize=7)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
