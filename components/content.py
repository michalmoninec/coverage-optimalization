from graph import GraphData
from paralel_tracks import ParalelTracks
# from components.infoTable import InfoTable
from components.pushButton import PushButton
from components.header import HeaderWidget

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QFileDialog, \
    QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, QFrame, QRadioButton, QStackedWidget, \
    QStackedLayout, QLabel, QSizePolicy, QGraphicsDropShadowEffect, QGroupBox, QFormLayout, QLineEdit, QComboBox, QSpinBox
from PyQt5.QtCore import QPersistentModelIndex, Qt, QTimer, QRegExp
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator, QRegExpValidator

from pathlib import Path
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import numpy as np

from copy import deepcopy

from hirearchial_clustering import hierarichial_cluster as cluster

class ContentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.contentStack = QStackedWidget()

        self.graphWrapper = QWidget()
        self.graphWidget = pg.PlotWidget()
        self.graphWidget2 = pg.PlotWidget()

        self.settingsMenu = QWidget()
        self.startButton = PushButton('Start plot')
        self.widthInput = QLineEdit('0.5')
        self.threshInput = QLineEdit('0,1')
        self.angleInput = QLineEdit('135')

        

        self.build()

    def build(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        graphWrapperLayout = QVBoxLayout()
        graphWrapperLayout.setContentsMargins(0,0,0,0)

        graphLabel = QLabel('Visualization of the computed area:')
        graphLabel.setContentsMargins(10,0,0,0)
        graphLabel.setStyleSheet('''
        font-size: 15px;
        ''')

        # self.graphWidget.setAspectLocked()
        self.graphWidget.getPlotItem().hideAxis('bottom')
        self.graphWidget.getPlotItem().hideAxis('left')
        self.graphWidget.setMenuEnabled(False)
        self.graphWidget.setStyleSheet('''
        border-top: 5px solid darkgray;
        ''')
        self.graphWidget.setBackground(None)
        self.graphWidget.setContentsMargins(0,0,0,0)

        self.graphWidget2.getPlotItem().hideAxis('bottom')
        self.graphWidget2.getPlotItem().hideAxis('left')
        self.graphWidget2.setMenuEnabled(False)
        self.graphWidget2.setStyleSheet('''
        border-top: 5px solid darkgray;
        ''')
        self.graphWidget2.setBackground(None)
        self.graphWidget2.setContentsMargins(0,0,0,0)


        graphWrapperLayout.addWidget(graphLabel)
        graphWrapperLayout.addWidget(self.graphWidget)
        graphWrapperLayout.addWidget(self.graphWidget2)
        self.graphWrapper.setLayout(graphWrapperLayout)

        settingsWrapperLayout = QHBoxLayout()
        settingsLayout = QVBoxLayout()

        formGroupBox = QGroupBox()
        formLayout = QFormLayout()

        onlyDouble = QDoubleValidator()
        self.widthInput.setValidator(onlyDouble)
        self.widthInput.setAlignment(Qt.AlignHCenter)

        reg_ex = QRegExp("[0]+[,]+[0-9]{,2}")
        threshValidator = QRegExpValidator(reg_ex,self.threshInput)
        self.threshInput.setValidator(threshValidator)
        self.threshInput.setAlignment(Qt.AlignHCenter)

        angle_regex = QRegExp("[0-9]|[1-9][0-9]|[1][0-7][0-9]|180")
        angleValidator = QRegExpValidator(angle_regex, self.angleInput)
        self.angleInput.setValidator(angleValidator)
        self.angleInput.setAlignment(Qt.AlignHCenter)

        # formLayout.addRow(QLabel("Thresh [m (<1)]:"), self.threshInput)
        
        formLayout.addRow(QLabel("Angle [Deg (0-180)]:"), self.angleInput)
        formLayout.addRow(QLabel("Width [m]:"), self.widthInput)
        formGroupBox.setLayout(formLayout)
        formGroupBox.setStyleSheet('''
        background: darkgrey;
        border-radius: 10px;
        font-size: 15px;
        ''')

        settingsLayout.addStretch(1)
        settingsLayout.addWidget(formGroupBox)
        settingsLayout.addWidget(self.startButton, alignment=Qt.AlignHCenter)
        settingsLayout.addStretch(1)


        settingsWrapperLayout.addStretch(1)
        settingsWrapperLayout.addLayout(settingsLayout)
        settingsWrapperLayout.addStretch(1)

        self.settingsMenu.setLayout(settingsWrapperLayout)

        self.contentStack.addWidget(self.settingsMenu)
        self.contentStack.addWidget(self.graphWrapper)


        layout.addWidget(self.contentStack)

        self.setLayout(layout)

