from PyQt5.QtCore import QThread, pyqtSignal
from utils.velide import Velide
import asyncio

VELIDE_SERVER="https://srv436689.hstgr.cloud/"

class DeliverymanConfigData(QThread):
    data = pyqtSignal(list, list, Velide)
    error = pyqtSignal(Exception)

    def __init__(self, farmax_conn, access_token):
        super().__init__()
        self.farmax_conn = farmax_conn
        self.access_token = access_token

    def run(self):
        try:
            asyncio.run(self.getData())
        except Exception as e:
            self.error.emit(e)

    async def getData(self):
        try:
            farmax_deliverymen = self.farmax_conn.fetchDeliverymen()

            velide = Velide(VELIDE_SERVER, self.access_token)
            velide_deliverymen = await velide.getDeliverymen()
            
            self.data.emit(farmax_deliverymen, velide_deliverymen, velide)
        except Exception as e:
            self.error.emit(e)