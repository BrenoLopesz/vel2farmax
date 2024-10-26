from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from utils.device_code import DeviceCode, DeviceCodeDict
import requests
import json
import base64
from datetime import datetime

class RefreshToken(QThread):
    error = pyqtSignal(Exception)
    token = pyqtSignal(dict)

    def __init__(self, domain, client_id, scope, refresh_token):
        super().__init__()
        self.url = 'https://{_domain}/oauth/token'.format(_domain = domain)
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.data = {
            'client_id': client_id,
            'grant_type': "refresh_token",
            'scope': scope,
            'refresh_token': refresh_token
        }

    def run(self):
        try:
            response = requests.post(self.url, headers=self.headers, data=self.data, verify=False)

            if response.status_code != 200:
                raise Exception(f"Failed to refresh token with status code {response.status_code}: {response.text}")
            
            jsonResponse = json.loads(response.text)

            jsonResponse["refresh_token"] = self.data["refresh_token"]
            print("Refreshed token: ", jsonResponse)
            self.token.emit(jsonResponse)
        except Exception as e:
            print(e)
            self.error.emit(e)