import requests
import os
import shutil
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QComboBox, QScrollArea, QTableWidget, QTableWidgetItem, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from workers.update_worker import UpdateWorker
from screens.load_fonts import loadFonts
from screens.update_screen import UpdateScreen
from screens.update_error_screen import UpdateErrorScreen
from screeninfo import get_monitors

WINDOW_SIZE = [600, 600]
REPO = 'BrenoLopesz/vel2farmax'

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))

def loadCSS():
     # Load the CSS file
    with open(os.path.join(BUNDLE_DIR, 'resources', 'style.css'), 'r') as f:
        return f.read()

class UpdateGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Vel2Farmax')
        self.fonts = loadFonts()

         # Set the window icon
        icon_path = os.path.join(BUNDLE_DIR, "resources", "velide.png")  # Use an appropriate icon path
        self.setWindowIcon(QIcon(icon_path))

        self.update_screen = UpdateScreen(self.fonts, self)
        self.update_screen.show()

        self.setGeometry(round((get_monitors()[0].width / 2) - (WINDOW_SIZE[0] / 2)), round((get_monitors()[0].height / 2) - (WINDOW_SIZE[1] / 2)), WINDOW_SIZE[0], WINDOW_SIZE[1])
        self.setFixedSize(WINDOW_SIZE[0], WINDOW_SIZE[1])

    def startUpdateWorker(self):
        def onRepeat():
            self.error_screen.close()
            self.update_screen.show()
            self.startUpdateWorker()

        def onError(error):
            print(error)
            self.update_screen.close()
            self.error_screen = UpdateErrorScreen(error, self.fonts, self, onRepeat)
            self.error_screen.show()


        self.updateWorker = UpdateWorker(repo=REPO)
        self.updateWorker.success.connect(self.update_screen.finish)
        self.updateWorker.error.connect(onError)
        self.updateWorker.end.connect(lambda: sys.exit(0))
        self.updateWorker.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(loadCSS())
    window = UpdateGUI()
    window.show()
    window.startUpdateWorker()
    sys.exit(app.exec_())