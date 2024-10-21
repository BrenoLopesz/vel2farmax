from PyQt5.QtCore import QThread, pyqtSignal
import base64
import json
from datetime import datetime
import time
import sys
import os
import jwt

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

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
            
            accessTokenDecoded = jwt.decode(jsonStoredAccess["access_token"], options={ "verify_signature": False})
            print("Decoded access token: {}".format(accessTokenDecoded))
            
            print(accessTokenDecoded["exp"], time.time(), time.time() > accessTokenDecoded["exp"])
            if not "exp" in accessTokenDecoded or time.time() > accessTokenDecoded["exp"]:
                print("Expired token.")
                # TODO: Refresh token
                self.expired.emit(jsonStoredAccess["refresh_token"])
                return
            
            self.token.emit(jsonStoredAccess["access_token"])
        except Exception as e:
            print("Cannot read file: ", e)