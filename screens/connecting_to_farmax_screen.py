from PyQt5.QtWidgets import QLabel, QWidget
from .load_fonts import FontsDict
from PyQt5.QtCore import Qt

class ConnectingToFarmaxScreen:
    def __init__(self, fonts: FontsDict, parent: QWidget):
        self.parent = parent
        self.fonts = fonts
        self.screen_width = 600

        self.authenticated_label = QLabel("Você está autenticado no <b>Velide</b>.", self.parent)
        self.authenticated_label.setObjectName("success")
        self.authenticated_label.setFont(self.fonts["regular"])
        self.authenticated_label.setAlignment(Qt.AlignCenter)
        self.authenticated_label.setFixedWidth(self.screen_width)
        self.authenticated_label.move(0, 242)

        self.connecting_farmax_label = QLabel("Conectando com o Farmax,<br/>por favor aguarde...", self.parent)
        self.connecting_farmax_label.setAlignment(Qt.AlignCenter)
        self.connecting_farmax_label.setFont(self.fonts["bold"])
        self.connecting_farmax_label.setFixedWidth(self.screen_width)
        self.connecting_farmax_label.move(0, 304)

    def show(self):
        self.authenticated_label.show()
        self.connecting_farmax_label.show()

    def close(self):
        self.authenticated_label.setParent(None)
        self.connecting_farmax_label.setParent(None)

    def setError(self):
        self.connecting_farmax_label.setText("Falha ao conectar com Farmax.")
        self.connecting_farmax_label.setObjectName("error")

    def setConnected(self):
        self.connecting_farmax_label.setText("Conectado com Farmax.")