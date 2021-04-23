from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QComboBox, QGraphicsDropShadowEffect, QHBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import Qt, QTimer, QRegExp

class ComboBox(QWidget):
    def __init__(self, options, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()
        self.cb = QComboBox()
        for option in options:
            self.cb.addItem(option)


        self.cb.setStyleSheet('''
        QComboBox{
            background-color: darkgray;
            padding-left: 5px;
            padding-right: 50px;
            min-height: 30px;
            border-radius: 10px;
            border: none;
            font-size: 15px;
        }

        ''')




        layout.addWidget(self.cb)
        self.setLayout(layout)

        

        
