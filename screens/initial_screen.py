from PyQt5.QtWidgets import QPushButton, QLabel, QWidget
from .load_fonts import FontsDict
from PyQt5.QtCore import Qt

class InitialScreen:
    def __init__(self, fonts: FontsDict, onButtonPress, parent: QWidget):
        self.parent = parent

        self.button = QPushButton('Conectar com Velide')
        self.button.clicked.connect(onButtonPress)
        self.button.setFont(fonts["bold"])
        self.button.move(188, 375)

        self.explainer_label = QLabel("Configure o seu servidor do <b>Farmax</b><br/>para conectar-se com o <b>Velide</b>.")
        self.explainer_label.setFont(fonts["regular"])
        self.explainer_label.setAlignment(Qt.AlignCenter)
        self.explainer_label.setFixedWidth(600)
        self.explainer_label.move(0, 148)

        self.cta_label = QLabel("<br>Primeiro, conecte esse dispositivo<br/>com sua conta Velide.<b/>")
        self.cta_label.setFont(fonts["bold"])
        self.cta_label.setAlignment(Qt.AlignCenter)
        self.cta_label.setFixedWidth(600)
        self.cta_label.move(0, 278)

    def show(self):
        self.button.setParent(self.parent)
        self.explainer_label.setParent(self.parent)
        self.cta_label.setParent(self.parent)

    def close(self):
        self.button.setParent(None)
        self.explainer_label.setParent(None)
        self.cta_label.setParent(None)