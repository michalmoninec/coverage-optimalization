from components.infoTable import InfoTable
from components.pushButton import PushButton

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QFileDialog, \
    QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, QFrame, QRadioButton, QStackedWidget, \
    QStackedLayout, QLabel, QSizePolicy, QGraphicsDropShadowEffect, QGroupBox, QFormLayout, QLineEdit, QComboBox, QSpinBox
from PyQt5.QtCore import Qt, QTimer, QRegExp
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator, QRegExpValidator


class HeaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settingsButton = PushButton('Settings')
        self.deleteGraphButton = PushButton('Delete graph')
        self.backButton = PushButton("Back to graph")
        self.advancedOptions = PushButton('Advanced options')
        self.settingsToggle = QStackedWidget()
        self.infoTable = InfoTable()
        self.settingsButtons = QWidget()
        self.backButtonWidget = QWidget()
        self.backToLoaderButton = PushButton('Back to loader')
        self.backToLoaderWidget = QWidget()
        
        
        self.build()

    def build(self):
        settingsArea = QHBoxLayout(self)

        
        settingsButtonsLayout = QHBoxLayout()
        settingsButtonsLayout.addWidget(self.infoTable)
        settingsButtonsLayout.addStretch(1)
        settingsButtonsLayout.addWidget(self.deleteGraphButton, alignment=Qt.AlignRight | Qt.AlignTop)
        settingsButtonsLayout.addWidget(self.settingsButton, alignment=Qt.AlignRight | Qt.AlignTop)
        self.settingsButtons.setLayout(settingsButtonsLayout)

        
        backButtonlayout = QHBoxLayout()
        backButtonlayout.addWidget(self.advancedOptions, alignment=Qt.AlignLeft | Qt.AlignTop)
        backButtonlayout.addStretch(1)
        backButtonlayout.addWidget(self.backButton, alignment=Qt.AlignRight | Qt.AlignTop)
        self.backButtonWidget.setLayout(backButtonlayout)

        backToLoaderLayout = QHBoxLayout()
        backToLoaderLayout.addStretch(1)
        backToLoaderLayout.addWidget(self.backToLoaderButton)
        self.backToLoaderWidget.setLayout(backToLoaderLayout)

        self.settingsToggle.addWidget(self.backButtonWidget)
        self.settingsToggle.addWidget(self.settingsButtons)
        self.settingsToggle.addWidget(self.backToLoaderWidget)

        settingsArea.addWidget(self.settingsToggle)

        self.setLayout(settingsArea)
