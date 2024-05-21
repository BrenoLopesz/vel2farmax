from screens.load_fonts import FontsDict
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt

class SearchingDeliveriesScreen:
    def __init__(self, parent: QWidget, fonts: FontsDict):
        self.parent = parent
        self.fonts = fonts
        self.screen_width = 600
        self.searching_deliveries = None
        self.connected_to_both = None

    def show(self):
        self.searching_deliveries = QLabel("Buscando entregas...", self.parent)
        self.searching_deliveries.setAlignment(Qt.AlignCenter)
        self.searching_deliveries.setFont(self.fonts["bold"])
        self.searching_deliveries.setFixedWidth(self.screen_width)
        self.searching_deliveries.move(0, 304)
        self.searching_deliveries.show()

        self.connected_to_both = QLabel("Você está autenticado no <b>Velide</b><br/>e conectado com o <b>Farmax</b>.", self.parent)
        self.connected_to_both.setAlignment(Qt.AlignCenter)
        self.connected_to_both.setFont(self.fonts["bold"])
        self.connected_to_both.setFixedWidth(self.screen_width)
        self.connected_to_both.move(0, 202)
        self.connected_to_both.show()

    def close(self):
        if self.searching_deliveries:
            self.searching_deliveries.setParent(None)
        if self.connected_to_both:
            self.connected_to_both.setParent(None)