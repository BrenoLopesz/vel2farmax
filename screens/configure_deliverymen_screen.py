from screens.load_fonts import FontsDict
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt
from components.list_item import ListItem
import traceback

class ConfigureDeliverymenScreen:
    def __init__(self, parent: QWidget, fonts: FontsDict, deliverymen, farmax_deliverymen, on_button_click, enable_return_button=False, on_return=None):
        self.parent = parent
        self.fonts = fonts
        self.deliverymen = deliverymen
        self.farmax_deliverymen = farmax_deliverymen
        self.screen_width = 600
        self.on_button_click = on_button_click
        self.enable_return_button = enable_return_button
        self.on_return = on_return

    def show(self):
        try:
            self.configure_deliverymen_label = QLabel("Configure seus entregadores<br/>com os correspondentes do Velide.", self.parent)
            self.configure_deliverymen_label.setAlignment(Qt.AlignCenter)
            self.configure_deliverymen_label.setFont(self.fonts["bold"])
            self.configure_deliverymen_label.setFixedWidth(self.screen_width)
            self.configure_deliverymen_label.move(0, 56)
            self.configure_deliverymen_label.show()

            self.scroll_area = QScrollArea(self.parent)

            widget = QWidget(self.parent)
            scroll_layout = QVBoxLayout(self.parent)
            widget.setLayout(scroll_layout)

            listItems = []

            # Add some sample items to the list
            for deliveryman in self.deliverymen:
                item = ListItem(deliveryman["name"], self.farmax_deliverymen)
                listItems.append(item)
                scroll_layout.addWidget(item)

            self.scroll_area.setWidget(widget)
            self.scroll_area.setFixedSize(568, 340)
            self.scroll_area.move(16, 162)
            self.scroll_area.show()

            self.button = QPushButton('Salvar', self.parent)
            self.button.clicked.connect(lambda: self.on_button_click(listItems))
            self.button.setFont(self.fonts["bold"])
            self.button.setFixedWidth(100)
            if self.enable_return_button:
                self.button.move(492, 524)
            else:
                self.button.move(250, 524)
            self.button.show()

            if self.enable_return_button:
                self.return_button = QPushButton('Voltar', self.parent)
                self.return_button.clicked.connect(self.on_return)
                self.return_button.setFont(self.fonts["bold"])
                self.return_button.setObjectName("neutral")
                self.return_button.setFixedWidth(100)
                self.return_button.move(16, 524)
                self.return_button.show()
        except Exception as e:
            # self.connecting_farmax_label.setText("Não foi possível buscar os<br/>entregadores no Velide.")
            # self.connecting_farmax_label.setObjectName("error")
            self.parent.setWindowTitle(f"{type(self.farmax_deliverymen)} {self.farmax_deliverymen}")
            print("error:", e)

    def close(self):
        if hasattr(self, "configure_deliverymen_label") and self.configure_deliverymen_label is not None:
            self.configure_deliverymen_label.setParent(None)
        if hasattr(self, "scroll_area") and self.scroll_area is not None:
            self.scroll_area.setParent(None)
        if hasattr(self, "button") and self.button is not None:
            self.button.setParent(None)
        if hasattr(self, "return_button") and self.return_button is not None:
            self.return_button.setParent(None)



