from graph import GraphData
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, QRadioButton, QStackedWidget, QStackedLayout, QLabel
from PyQt5.QtGui import QIcon
from pathlib import Path
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
from copy import deepcopy


class PushButton(QtGui.QPushButton):
    def __init__(self, parent=None):
        super(PushButton, self).__init__(parent)

    #   self.clicked.connect(self.deleteLater)


class RadioButton(QtGui.QRadioButton):
    def __init__(self, parent=None):
        super(RadioButton, self).__init__(parent)
        self.selected = False
        self.toggled.connect(self.button_toggled)

    def button_toggled(self, selected):
        self.selected = selected
        # print(self.selected)


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
        self.singleFile = PushButton('Choose single file')
        layout = QHBoxLayout()
        layout.addWidget(self.singleFile)
        self.setLayout(layout)


class InputSeparatedFiles(QWidget):
    def __init__(self, parent=None):
        super(InputSeparatedFiles, self).__init__(parent)
        self.outerBorder = PushButton('Choose outer border')
        self.innerBorder = PushButton('Choose inner border')
        layout = QHBoxLayout()
        layout.addWidget(self.outerBorder)
        layout.addWidget(self.innerBorder)
        self.setLayout(layout)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.graph_data = GraphData(None)

        title = 'Foking automower'

        self.setWindowTitle(title)
        self.setGeometry(0, 0, 800, 400)
        self.setWindowIcon(QIcon('icon.png'))

        layout = QVBoxLayout()
        navbar = QHBoxLayout()
        navbar2 = QHBoxLayout()

        self.inputMethod = InputMethod()
        self.inputMethod.rb_one_file.toggled.connect(self.tryPrint)

        self.inputFile = QStackedLayout()

        self.inputSingleFile = InputSingleFile()
        self.inputSingleFile.singleFile.clicked.connect(self.set_complete_file)

        self.inputSeparatedFiles = InputSeparatedFiles()
        self.inputSeparatedFiles.outerBorder.clicked.connect(
            self.button_clicked_outer)
        self.inputSeparatedFiles.innerBorder.clicked.connect(
            self.button_clicked_inner)

        self.inputFile.addWidget(self.inputSingleFile)
        self.inputFile.addWidget(self.inputSeparatedFiles)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setAspectLocked()
        self.graphWidget.getPlotItem().hideAxis('bottom')
        self.graphWidget.getPlotItem().hideAxis('left')

        layout.addLayout(self.inputMethod)
        layout.addLayout(self.inputFile)
        # layout.addStretch(1)
        layout.addWidget(self.graphWidget)
        layout.addLayout(navbar)
        layout.addLayout(navbar2)

        self.setLayout(layout)
        self.set_location()

        self.show()

        # self.b1 = QtWidgets.QPushButton(self)
        # self.b1.setText("Outer border")
        # self.b1.clicked.connect(self.button_clicked_outer)

        # self.b2 = QtWidgets.QPushButton(self)
        # self.b2.setText("Inner border")
        # self.b2.clicked.connect(self.button_clicked_inner)
        # self.b2.setEnabled(False)

        # self.b3 = QtWidgets.QPushButton(self)
        # self.b3.setText("Clear all")
        # self.b3.clicked.connect(self.clear_graph)

        # self.b4 = QtWidgets.QPushButton(self)
        # self.b4.setText("Choose file with everything")
        # self.b4.clicked.connect(self.set_complete_file)

        # self.b5 = QtWidgets.QPushButton(self)
        # self.b5.setText('button shouldnt be here')
        # self.b5.clicked.connect(self.create_button)

        # navbar.addWidget(self.b1)
        # navbar.addWidget(self.b2)
        # navbar.addWidget(self.b3)

        # navbar2.addWidget(self.b4)
        # navbar2.addWidget(self.b5)

        # layout.addLayout(navbar2)
        # layout.addLayout(navbar)

    def tryPrint(self):
        if self.inputMethod.rb_one_file.selected:
            self.inputFile.setCurrentWidget(self.inputSingleFile)
        else:
            self.inputFile.setCurrentWidget(self.inputSeparatedFiles)

    def create_button(self):
        pass
        # self.layout().children()[0].addWidget(PushButton())
        # print(self.layout().children()[0].objectName())
        # self.b2.setText('changetext mothefucka')

    def clear_graph(self):
        self.graphWidget.clear()
        self.graph_data.coords.clear()
        self.graph_data.border_inner.clear()
        self.graph_data.border_outer.clear()
        self.b1.setEnabled(True)
        self.b2.setEnabled(False)

    def button_clicked_outer(self):
        if (self.get_graph_data()):
            coors = self.graph_data.coords
            if(self.graph_data.check_closed_loop(coors.x, coors.y)):
                self.plot(coors.x, coors.y, 'b')
                self.graph_data.border_outer.x = deepcopy(coors.x)
                self.graph_data.border_outer.y = deepcopy(coors.y)
                self.b1.setEnabled(False)
                self.b2.setEnabled(True)
            else:
                print('Incorrect input.')
                msg = QMessageBox()
                msg.setWindowTitle("Outer border")
                msg.setText("Outer border is not closed")
                msg.setIcon(QMessageBox.Information)
                msg.exec_()

    def button_clicked_inner(self):
        if (self.get_graph_data()):
            # kontrola jestli je smyčka uvnitř vnejsi smycky
            if(self.graph_data.check_inner_validity()):
                self.plot(self.graph_data.coords.x,
                          self.graph_data.coords.y, 'r')
                self.plot(self.graph_data.border_outer.x,
                          self.graph_data.border_outer.y, 'b')
                # print(self.graph_data.border_outer.x)
                self.update()
            else:
                print('Incorrect input.')
                msg = QMessageBox()
                msg.setWindowTitle("Inner border")
                msg.setText("Inner border is outside of outer border.")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()

    def set_complete_file(self):
        graph = self.graph_data
        if(self.get_graph_data()):
            graph.get_outer_inner()
            self.plot(self.graph_data.border_outer.x,
                      self.graph_data.border_outer.y, 'b')
            self.plot(self.graph_data.border_inner.x,
                      self.graph_data.border_inner.y, 'r')

    def get_graph_data(self):
        home_dir = str(Path.cwd())
        fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir)
        if fname[0]:
            self.graph_data.set_coords(fname[0])
            return fname[0]

    def update(self):
        pass

    def get_desktop_geometry(self):
        width = QDesktopWidget().screenGeometry().width()
        height = QDesktopWidget().screenGeometry().height()
        return width, height

    def get_window_geometry(self):
        width = self.geometry().width()
        height = self.geometry().height()
        return width, height

    def set_location(self):
        screen_width, screen_height = self.get_desktop_geometry()
        window_width, window_height = self.get_window_geometry()
        x = int((screen_width - window_width)/2)
        y = int((screen_height - window_height)/2)
        self.move(x, y)

    def plot(self, x, y, color):
        pen = pg.mkPen(color=color)
        self.graphWidget.plot(x, y, name=None, pen=pen)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
