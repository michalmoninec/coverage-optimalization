from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class InfoTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fileName = QLabel("")
        self.width = QLabel("")
        self.countOfClusters = QLabel("")
        self.thresh = QLabel("")
        self.angle = QLabel("")
        self.build()
        self.setStyleSheet(
            """
        font-size: 15px;
        """
        )

    def build(self):
        layout = QVBoxLayout()
        layout.setSpacing(0)

        layout.addWidget(QLabel("Table of parameters:"))

        layoutWrapper = QHBoxLayout()
        layoutWrapper.setSpacing(0)

        Wrapper = QWidget()

        layoutVert1 = QVBoxLayout()
        layoutVert1.setSpacing(0)

        Column1 = QWidget()

        layoutVert1.addWidget(self.addRow("File name:", self.fileName))
        layoutVert1.addWidget(self.addRow("Width:", self.width))
        Column1.setLayout(layoutVert1)
        Column1.setContentsMargins(0, 0, 0, 0)
        layoutWrapper.addWidget(Column1)

        layoutVert2 = QVBoxLayout()
        layoutVert2.setSpacing(0)

        Column2 = QWidget()

        layoutVert2.addWidget(self.addRow("Number of clusters:", self.countOfClusters))
        # layoutVert2.addWidget(self.addRow('Thresh:', self.thresh))
        layoutVert2.addWidget(self.addRow("Angle:", self.angle))

        Column2.setLayout(layoutVert2)
        Column2.setContentsMargins(0, 0, 0, 0)
        layoutWrapper.addWidget(Column2)

        layout.setContentsMargins(0, 0, 0, 0)
        layoutWrapper.setContentsMargins(0, 0, 0, 0)
        layoutVert1.setContentsMargins(0, 0, 0, 0)
        layoutVert2.setContentsMargins(0, 0, 0, 0)

        Wrapper.setLayout(layoutWrapper)
        Wrapper.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(Wrapper)
        # self.setLayout(layout)

        # fileName = QWidget()
        # fileLayout = QHBoxLayout()
        # fileLayout.addWidget(QLabel('File name:'))
        # self.fileName = QLabel('')
        # fileLayout.addWidget(self.fileName)
        # fileName.setLayout(fileLayout)
        # layout.addWidget(fileName)

        self.setLayout(layout)

    def addRow(self, label_name, label_value):
        item = QWidget()
        item.setContentsMargins(0, 0, 20, 0)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(label_name))
        layout.addWidget(label_value, alignment=Qt.AlignRight)
        item.setLayout(layout)
        item.setStyleSheet(
            """
        margin:0;
        padding:0;
        """
        )
        return item
