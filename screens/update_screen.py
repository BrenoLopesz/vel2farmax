from PyQt5.QtWidgets import QPushButton, QLabel, QWidget
from .load_fonts import FontsDict
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, pyqtProperty, pyqtSignal, QTimer
from components.loading_icon import LoadingIcon
from components.velide_icon import VelideIcon
import sys

class UpdateScreen:
    valueChanged = pyqtSignal(int)

    def __init__(self, fonts: FontsDict, parent: QWidget):
        self.parent = parent
        self.fonts = fonts
        self._rotation = 0

        # self.button = QPushButton('Conectar com Velide')
        # self.button.clicked.connect(onButtonPress)
        # self.button.setFont(fonts["bold"])
        # self.button.move(188, 375)
        self.update_label = QLabel("Buscando atualizações...")
        self.update_label.setObjectName("title")
        self.update_label.setFont(fonts["bold"])
        self.update_label.setAlignment(Qt.AlignCenter)
        self.update_label.setFixedWidth(600)
        self.update_label.move(0, 138)

        self.info_label = QLabel("A aplicação irá iniciar em alguns segundos,<br/>por favor aguarde.")
        # self.info_label.setObjectName("title")
        self.info_label.setFont(fonts["light"])
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setFixedWidth(600)
        self.info_label.move(0, 412)

        self.new_version_label = QLabel("")
        self.new_version_label.setFont(self.fonts["regular"])
        self.new_version_label.setAlignment(Qt.AlignCenter)
        self.new_version_label.setFixedWidth(600)
        self.new_version_label.move(0, 234)

        self.velide_icon = VelideIcon()
        self.velide_icon.setAlignment(Qt.AlignCenter)
        self.velide_icon.setFixedWidth(600)
        self.velide_icon.move(0, 60)

        self.add_loading_icon()

    @pyqtProperty(int)
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, rotation):
        self._rotation = rotation
        self.valueChanged.emit(rotation)

    def add_loading_icon(self):
        self.image = LoadingIcon()
        self.image.move(round(300 - self.image.width() / 2), round(300 - self.image.height() / 2))
        self.anim = QPropertyAnimation(self.image, b"rotation")
        self.anim.setDuration(2250)  
        self.anim.setStartValue(0)   
        self.anim.setEndValue(360)   
        self.anim.setLoopCount(-1)
        self.anim.start()

    def close(self):
        self.update_label.setParent(None)
        self.info_label.setParent(None)
        self.new_version_label.setParent(None)
        self.image.setParent(None)
        self.velide_icon.setParent(None)

    def finish(self, new_version, new_version_date, old_version):
        self.update_label.setText("Atualização concluída.")

        self.new_version_label.setText("Nova versão adquirida:<br/><b>{}</b><br/>{}<br/><br/>Versão anterior:<br/><b>{}</b>".format(new_version, new_version_date, "Nenhuma" if old_version is None or old_version == "" else old_version))
        self.new_version_label.setFont(self.fonts["regular"])
        self.new_version_label.setAlignment(Qt.AlignCenter)
        self.new_version_label.setFixedWidth(600)
        self.new_version_label.move(0, 234)
        self.new_version_label.adjustSize()

        self.info_label.setText("A aplicação iniciará agora.")
        # self.info_label.setObjectName("title")
        self.info_label.setFont(self.fonts["regular"])
        self.info_label.move(0, 506)

        self.image.setParent(None)

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: sys.exit(0))
        self.timer.setParent(self.parent)
        self.timer.start(5000)



    def show(self):
        self.new_version_label.setParent(self.parent)
        self.update_label.setParent(self.parent)
        self.info_label.setParent(self.parent)
        self.image.setParent(self.parent)
        self.velide_icon.setParent(self.parent)