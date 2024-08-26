from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QPushButton
from PyQt5.QtCore import Qt, QTimer, QRegExp


class PushButton(QPushButton):
    def __init__(self, parent=None):
        super(PushButton, self).__init__(parent)
        self.setStyleSheet(
            "background-color: darkgray; border-radius: 10px; border: none; font-size: 15px;"
        )
        #   self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.setFixedSize(120, 30)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        effect.setOffset(3, 3)
        self.setGraphicsEffect(effect)

    def mousePressEvent(self, event):
        self.fade()
        super().mousePressEvent(event)

    def fade(self):
        self.move(self.x(), self.y() + 3)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        effect.setOffset(0, 0)
        self.setGraphicsEffect(effect)
        self.setStyleSheet(
            "background-color: gray; border-radius: 15px;border: none;font-size: 15px;"
        )
        # print('should fade')
        QTimer.singleShot(500, self.unfade)

    def unfade(self):
        self.setStyleSheet(
            "background-color: darkgray; border-radius: 15px;border: none;font-size: 15px;"
        )
        self.move(self.x(), self.y() - 3)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        effect.setOffset(3, 3)
        self.setGraphicsEffect(effect)
        # print('end of fade')
