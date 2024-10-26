from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap

class ErrorIcon(QLabel):
    def __init__(self):
        super().__init__()
        pixmap = QPixmap('resources/error.png')
        pixmap = pixmap.scaledToWidth(128)
        pixmap = pixmap.scaledToHeight(128)
        self.setPixmap(pixmap)