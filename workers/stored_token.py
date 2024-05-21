from PyQt5.QtCore import QThread, pyqtSignal
import base64
import json
from datetime import datetime
import time
import sys
import os

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
else:
    BUNDLE_DIR = os.path.join(os.path.dirname(os.path.realpath( __file__ )), "..")

class StoredToken(QThread):
    token = pyqtSignal(str)
    expired = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self): 
        try: 
            f = open(os.path.join(BUNDLE_DIR, "resources", "json.txt"), "r")
            storedAccess = base64.b64decode(f.read()).decode('utf-8')
            jsonStoredAccess = json.loads(storedAccess)
            print("token: ", jsonStoredAccess)
            if(jsonStoredAccess is None or jsonStoredAccess["access_token"] is None):
                return 
            
            print(jsonStoredAccess["expires_at"], time.time(), time.time() > jsonStoredAccess["expires_at"])
            if "expires_at" in jsonStoredAccess and time.time() > jsonStoredAccess["expires_at"]:
                print("Expired token.")
                # TODO: Refresh token
                self.expired.emit(jsonStoredAccess["refresh_token"])
                return
            
            self.token.emit(jsonStoredAccess["access_token"])
        except Exception as e:
            print("Cannot read file: ", e)