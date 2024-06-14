from PyQt5.QtWidgets import QPushButton, QLabel, QWidget
from .load_fonts import FontsDict
from PyQt5.QtCore import Qt, QTimer
from utils.device_code import DeviceCodeDict

class ErrorScreen:
    def __init__(self, fonts: FontsDict, parent: QWidget):
        self.parent = parent
        self.fonts = fonts

        self.error_label = QLabel("<b>Ocorreu um erro inesperado!</b>")
        self.error_label.setObjectName("error")
        self.error_label.setFont(fonts["bold"])
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setFixedWidth(600)
        self.error_label.move(0, 187)

        self.explainer_label = QLabel("A integração foi interrompida e será<br/><b>reiniciada em breve</b>, por favor aguarde.")
        self.explainer_label.setFont(fonts["regular"])
        self.explainer_label.setAlignment(Qt.AlignCenter)
        self.explainer_label.setFixedWidth(600)
        self.explainer_label.move(0, 259)

        self.close_this = QLabel("Caso deseje que isso não aconteça,<br/>feche esta janela.")
        self.close_this.setFont(fonts["regular"])
        self.close_this.setAlignment(Qt.AlignCenter)
        self.close_this.setFixedWidth(600)
        self.close_this.move(0, 343)


    def show(self):
        self.error_label.setParent(self.parent)
        self.explainer_label.setParent(self.parent)
        self.close_this.setParent(self.parent)

        self.error_label.show()
        self.explainer_label.show()
        self.close_this.show()

        self.setRestartTime()

    def close(self):
        if hasattr(self, "error_label"):
            self.error_label.setParent(None)
        if hasattr(self, "explainer_label"):
            self.explainer_label.setParent(None)
        if hasattr(self, "close_this"):
            self.close_this.setParent(None)
        if hasattr(self, "restarting_in_label"):
            self.restarting_in_label.setParent(None)

        if hasattr(self, "timer"):
            self.timer.stop()
            self.timer.setParent(None)

    def setRestartTime(self):
        self.remaining_time = 15

        # Used to update display (updates every second)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.setParent(self.parent)
        self.timer.start(1000)

        self.restarting_in_label = QLabel("Reiniciando em 00:15")
        self.restarting_in_label.setFont(self.fonts["regular"])
        self.restarting_in_label.setAlignment(Qt.AlignCenter)
        self.restarting_in_label.setFixedWidth(600)
        self.restarting_in_label.move(0, 559)
        self.restarting_in_label.setParent(self.parent)
        self.restarting_in_label.show()

        self.update_timer()

    def update_timer(self):
        if self.remaining_time > 0:
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            self.restarting_in_label.setText("Reiniciando em {:02d}:{:02d}".format(minutes, seconds))
            self.remaining_time -= 1
        else:
            self.timer.stop()
            raise
        