from graph import GraphData
from paralel_tracks import ParalelTracks

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, QRadioButton, QStackedWidget, QStackedLayout, QLabel
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
        self.setLayout(layout)

class InputSeparatedFiles(QWidget):
    def __init__(self, parent=None):
        super(InputSeparatedFiles, self).__init__(parent)
        layout = QHBoxLayout()
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

        # self.setStyleSheet("background-color: gray;")
        style = """
        background-color: lightgray;
        """

        self.setStyleSheet(style)

        layout = QVBoxLayout()
        # navbar = QHBoxLayout()
        # navbar2 = QHBoxLayout()

        # self.inputMethod = InputMethod()
        # self.inputMethod.rb_one_file.toggled.connect(self.tryPrint)

        self.inputFile = QStackedLayout()

        self.inputSingleFile = InputSingleFile()
        self.inputSingleFile.selectFile.clicked.connect(self.set_complete_file)

        # self.inputSeparatedFiles = InputSeparatedFiles()
        # self.inputSeparatedFiles.selectOuter.clicked.connect(self.button_clicked_outer)
        # self.inputSeparatedFiles.selectInner.clicked.connect(self.button_clicked_inner)

        self.inputFile.addWidget(self.inputSingleFile)
        # self.inputFile.addWidget(self.inputSeparatedFiles)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setAspectLocked()
        self.graphWidget.getPlotItem().hideAxis('bottom')
        self.graphWidget.getPlotItem().hideAxis('left')

        # layout.addLayout(self.inputMethod)
        layout.addLayout(self.inputFile)
        layout.addWidget(self.graphWidget,2)
        # layout.addLayout(navbar)
        # layout.addLayout(navbar2)

        self.setLayout(layout)
        self.set_location()

        self.graphWidget.setBackground(None)

        self.show()

    #looks good
    def tryPrint(self):
        if self.inputMethod.rb_one_file.selected:
            self.inputFile.setCurrentWidget(self.inputSingleFile)
        else:
            self.inputFile.setCurrentWidget(self.inputSeparatedFiles)

    #not used
    def create_button(self):
        pass

    #not used
    def clear_graph(self):
        pass
        # self.graphWidget.clear()
        # self.graph_data.coords.clear()
        # # self.graph_data.border_inner.clear()
        # # self.graph_data.border_outer.clear()
        # self.b1.setEnabled(True)
        # self.b2.setEnabled(False)

    #add consequencecy logic to select outer at first
    def button_clicked_outer(self):
        pass
        # if (self.get_graph_data()):
        #     coors = self.graph_data.coords
        #     if(self.graph_data.check_closed_loop(coors.x,coors.y)):
        #         self.plot(coors.x,coors.y, 'b')
        #         self.graph_data.border_outer.x = deepcopy(coors.x)
        #         self.graph_data.border_outer.y = deepcopy(coors.y)
        #         self.b1.setEnabled(False)
        #         self.b2.setEnabled(True)               
        #     else:
        #         print('Incorrect input.')
        #         msg = QMessageBox()
        #         msg.setWindowTitle("Outer border")
        #         msg.setText("Outer border is not closed")
        #         msg.setIcon(QMessageBox.Information)
        #         msg.exec_()

    #change outer, inner - after graph validity check
    def button_clicked_inner(self):
        pass
        # if (self.get_graph_data()):
        #     #inner polygon check
        #     if(self.graph_data.check_inner_validity()):
        #         self.plot(self.graph_data.coords.x,self.graph_data.coords.y, 'r')
        #         self.plot(self.graph_data.border_outer.x,self.graph_data.border_outer.y, 'b')
        #         # print(self.graph_data.border_outer.x)
        #         self.update()
        #     else:
        #         print('Incorrect input.')
        #         msg = QMessageBox()
        #         msg.setWindowTitle("Inner border")
        #         msg.setText("Inner border is outside of outer border.")
        #         msg.setIcon(QMessageBox.Warning)
        #         msg.exec_()

    #check data types
    def set_complete_file(self):    
        graph = self.graph_data

        if(self.get_graph_data()):
            graph.get_outer_inner()
            self.plot(graph.outer_plot.x,graph.outer_plot.y, 'b')

            for i in range(len(self.graph_data.inner_plot)):
                self.plot(self.graph_data.inner_plot[i].x, self.graph_data.inner_plot[i].y, 'r')

            tracks = ParalelTracks(self.graph_data.outer, self.graph_data.inner, 0.5)
            tracks.getUpperPoints()
            
            
            for i in range(len(tracks.paralels)):
                self.plot_upper(tracks.upper[i].point)

            for i in range(len(tracks.paralels)):
                self.plot(tracks.paralels[i][0],tracks.paralels[i][1], 'k')

            arr = []
            for i in range(len(tracks.upper)):
                arr.append((tracks.upper[i].point))
            cluster(arr)

            

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
    def plot(self, x, y, color):
        pen = pg.mkPen(color=color)
        self.graphWidget.plot(x, y, name=None, pen=pen)

    def plot_upper(self,point):
        # print(f"tady to dojde : {point[0]}")
        # pen = pg.mkPen(color="r")
        self.graphWidget.plot([point[0]],[point[1]], name="another", pen=None, symbol='o', symbolPen=pg.mkPen(color=(0, 0, 255), width=0),symbolBrush=pg.mkBrush(0, 0, 255, 255),symbolSize=7)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
