import os
from PyQt5.QtCore import QThread, pyqtSignal
from utils.farmax import Farmax
from dotenv import load_dotenv
import sys

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# Load environment variables from .env file
load_dotenv(os.path.join(BUNDLE_DIR, "resources", ".env"))

host = os.getenv('HOST')
database = os.getenv('DATABASE')
user = os.getenv('USER')
password = os.getenv('PASSWORD')

class ConnectToFarmax(QThread):
    signal = pyqtSignal(Farmax)
    error = pyqtSignal(Exception)

    def __init__(self):
        super().__init__()

    def run(self):
        farmax_conn = Farmax(host, database, user, password)

        try: 
            farmax_conn.connect()
            self.signal.emit(farmax_conn)
        except Exception as e:
            self.error.emit(e)