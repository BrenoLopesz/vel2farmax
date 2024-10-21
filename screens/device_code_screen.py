from PyQt5.QtWidgets import QPushButton, QLabel, QWidget
from .load_fonts import FontsDict
from PyQt5.QtCore import Qt, QTimer
from utils.device_code import DeviceCodeDict

class DeviceCodeScreen:
    def __init__(self, fonts: FontsDict, parent: QWidget):
        self.parent = parent
        self.fonts = fonts

        self.explainer_label = QLabel("Configure o seu servidor do <b>Farmax</b><br/>para conectar-se com o <b>Velide</b>.")
        self.explainer_label.setFont(fonts["regular"])
        self.explainer_label.setAlignment(Qt.AlignCenter)
        self.explainer_label.setFixedWidth(600)
        self.explainer_label.move(0, 148)

        self.cta_label = QLabel("<b>Acesse o link abaixo e<br/>insira o código informado.</b>")
        self.cta_label.setFont(fonts["bold"])
        self.cta_label.setAlignment(Qt.AlignCenter)
        self.cta_label.setFixedWidth(600)
        self.cta_label.move(0, 278)

        self.code_label = QLabel("Código")
        self.code_label.setFont(fonts["regular"])
        self.code_label.setAlignment(Qt.AlignCenter)
        self.code_label.setFixedWidth(600)
        self.code_label.move(0, 415)

    def show(self):
        self.explainer_label.setParent(self.parent)
        self.cta_label.setParent(self.parent)
        self.code_label.setParent(self.parent)

        self.explainer_label.show()
        self.cta_label.show()
        self.code_label.show()

    def close(self):
        self.explainer_label.setParent(None)
        self.cta_label.setParent(None)
        self.code_label.setParent(None) 

        if hasattr(self, "login_link"):
            self.login_link.setParent(None)
        if hasattr(self, "expire_label"):
            self.expire_label.setParent(None)
        if hasattr(self, "code_display"):
            self.code_display.setParent(None)

        if hasattr(self, "timer"):
            self.timer.stop()
            self.timer.setParent(None)

    def setDeviceCode(self, device_code: DeviceCodeDict):
        self.code_display = QLabel(device_code["user_code"], self.parent)
        self.code_display.setFont(self.fonts["bold"])
        self.code_display.setObjectName("codeDisplay")
        self.code_display.setAlignment(Qt.AlignCenter)
        self.code_display.setFixedWidth(600)
        self.code_display.move(0, 442)
        self.code_display.show()

        self.login_link = QLabel('<a href=\"{}\" style=\"color: #0EA5E9\">{}</a>'.format(device_code["verification_uri_complete"], device_code["verification_uri"]), self.parent)
        self.login_link.setTextFormat(Qt.RichText) 
        self.login_link.setObjectName("link")
        self.login_link.setFont(self.fonts["bold"])
        self.login_link.setOpenExternalLinks(True)
        self.login_link.setAlignment(Qt.AlignCenter)
        self.login_link.setFixedWidth(600)
        self.login_link.move(0, 346)
        self.login_link.show()

        self.remaining_time = device_code["expires_in"]

        # Used to update display (updates every second)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.setParent(self.parent)
        self.timer.start(1000)

        self.expire_label = QLabel("Expira em ----:----", self.parent)
        self.expire_label.setFont(self.fonts["light"])
        self.expire_label.setAlignment(Qt.AlignCenter)
        self.expire_label.setFixedWidth(600)
        self.expire_label.move(0, 559)
        self.expire_label.show()

        self.update_timer()

    def update_timer(self):
        if self.remaining_time > 0:
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            self.expire_label.setText("Expira em {:02d}:{:02d}".format(minutes, seconds))
            self.remaining_time -= 1
        else:
            self.expire_label.setText("Código expirado.")
            self.expire_label.setObjectName("error")
            self.timer.stop()
        