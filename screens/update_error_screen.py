from PyQt5.QtWidgets import QPushButton, QLabel, QWidget
from .load_fonts import FontsDict
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, pyqtProperty, pyqtSignal
from PyQt5.QtGui import QPixmap, QTransform, QFont
from components.error_icon import ErrorIcon
from components.velide_icon import VelideIcon
import sys

class UpdateErrorScreen:
    def __init__(self, error, fonts: FontsDict, parent: QWidget, onRepeat):
        self.parent = parent
        self.fonts = fonts

        self.button = QPushButton('Tentar Novamente')
        self.button.clicked.connect(onRepeat)
        self.button.setFont(fonts["bold"])

        self.title_label = QLabel("Não foi possível atualizar.")
        self.title_label.setObjectName("title")
        self.title_label.setFont(fonts["bold"])
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFixedWidth(600)
        self.title_label.move(0, 138)

        self.error_label = QLabel("<span style=\"color: #dc2626\">{}</span>".format(error))
        self.error_label.setTextFormat(Qt.RichText)
        # self.info_label.setObjectName("title")
        self.error_label.setFont(fonts["light"])
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setFixedWidth(600)
        self.error_label.move(0, 376)

        self.skip_label = QLabel("<span style=\"text-decoration: underline\">Pular atualização</span>")
        self.skip_label.setTextFormat(Qt.RichText)
        # self.info_label.setObjectName("title")
        self.skip_label.setFont(fonts["light"])
        self.skip_label.setAlignment(Qt.AlignCenter)
        self.skip_label.setFixedWidth(600)
        self.skip_label.mousePressEvent = lambda x: sys.exit(0)
        self.skip_label.move(0, 502)

        self.velide_icon = VelideIcon()
        self.velide_icon.setAlignment(Qt.AlignCenter)
        self.velide_icon.setFixedWidth(600)
        self.velide_icon.move(0, 60)
        self.add_error_icon()

    def add_error_icon(self):
        self.image = ErrorIcon()

    def close(self):
        self.button.setParent(None)
        self.title_label.setParent(None)
        self.skip_label.setParent(None)
        self.velide_icon.setParent(None)
        self.error_label.setParent(None)
        self.image.setParent(None)

    def show(self):
        self.button.setParent(self.parent)
        self.button.show()
        self.button.move(round(300 - self.button.width() / 2), 432)
        self.title_label.setParent(self.parent)
        self.title_label.show()
        self.skip_label.setParent(self.parent)
        self.skip_label.show()
        self.velide_icon.setParent(self.parent)
        self.velide_icon.show()
        self.error_label.setParent(self.parent)
        self.error_label.show()
        self.image.setParent(self.parent)
        self.image.show()
        self.image.move(round(300 - self.image.width() / 2), 220)