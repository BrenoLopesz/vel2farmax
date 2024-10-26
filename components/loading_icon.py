import sys
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty
from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtGui import QPainter, QTransform, QPixmap

class LoadingIcon(QLabel):
    def __init__(self):
        super().__init__()
        self._rotation = 0  # Store the rotation angle
        self.pixmap = QPixmap('resources/loading.png')
        self.pixmap.scaledToHeight(96)
        # self.pixmap.scaledToWidth(96)
        self.setPixmap(self.pixmap)
        self.resize(self.pixmap.width() + 5, self.pixmap.height() + 5)

    def setRotation(self, angle):
        """Sets the rotation angle."""
        self._rotation = angle
        self.update()  # Trigger a repaint

    def getRotation(self):
        """Gets the rotation angle."""
        return self._rotation

    # Define a Q_PROPERTY for rotation, so QPropertyAnimation can use it
    rotation = pyqtProperty(float, getRotation, setRotation)

    def paintEvent(self, event):
         # Create a QPainter object to handle drawing
        painter = QPainter(self)
        
        # Calculate the center point of the QLabel
        center = self.rect().center()

        # Apply rotation transform
        transform = QTransform()
        transform.translate(center.x(), center.y())
        transform.rotate(self._rotation)
        transform.translate(-center.x(), -center.y())

        # Set the transform to the painter
        painter.setTransform(transform)

        # Draw the pixmap centered in the label
        pixmap_center = self.pixmap.rect().center()
        x = center.x() - pixmap_center.x()
        y = center.y() - pixmap_center.y()
        painter.drawPixmap(x, y, self.pixmap)

        painter.end()