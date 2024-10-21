from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from utils.device_code import DeviceCode, DeviceCodeDict
from utils.access_token import AccessToken
import time
import os

DOMAIN = os.getenv('DOMAIN')
CLIENT_ID = os.getenv('CLIENT_ID')
SCOPE = os.getenv('SCOPE')
AUDIENCE = os.getenv('AUDIENCE')

class AuthorizationFlow(QThread):
    signal = pyqtSignal(str)
    error = pyqtSignal(str)
    device_code = pyqtSignal(dict)

    def __init__(self, logger) -> None:
        super().__init__()
        self.logger = logger
    
    def run(self):
        """
        Generate device token to login into Velide.
        """
        device_code = DeviceCode(domain=DOMAIN, client_id=CLIENT_ID, scope=SCOPE, audience=AUDIENCE)
        device_code.request()

        if(device_code.getStatusCode() != 200):
            self.error.emit("Ocorreu um erro inesperado.<br/>Tente novamente.")
            return

        responseJSON = device_code.getResponseJSON()
        self.device_code.emit(responseJSON)
        expires_at = time.time() + responseJSON["expires_in"]

        access_token_handler = AccessToken(domain=DOMAIN, client_id=CLIENT_ID, device_code=responseJSON["device_code"])
        access_token = None
        while access_token is None and not time.time() > expires_at:
            access_token = self.tryToGetToken(access_token_handler)
            # Sleeps on the interval to prevent 'Too many requests' error
            time.sleep(responseJSON["interval"])
        
        # Device code has expired
        if access_token is None:
            self.error.emit("Código do dispositivo expirado.<br/>Tente novamente.")
            return
        
        # Success
        self.signal.emit(access_token)
    
    def tryToGetToken(self, access_token_handler):
            access_token_handler.request()
            if("error" in access_token_handler.getResponseJSON()):
                return None
            access_token_handler.storeAtFile()
            return access_token_handler.getResponseJSON()["access_token"]