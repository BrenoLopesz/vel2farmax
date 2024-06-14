from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from utils.device_code import DeviceCode, DeviceCodeDict
from utils.sqlite_manager import SQLiteManager
from utils.velide import Velide
from utils.logger import Logger
from datetime import datetime, timedelta
import asyncio
import sys
import os

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

DB_NAME = os.path.join(BUNDLE_DIR, "resources", "vel2farmax.db")

class DeliveriesTracker(QThread):
    on_update = pyqtSignal(list)
    end = pyqtSignal()
    error = pyqtSignal(Exception)

    def __init__(self, velide: Velide):
        super().__init__()
        self.velide = velide
        
    def run(self):
        try:
            self.sqlite = SQLiteManager(DB_NAME)
            self.sqlite.connect()

            deliverymen = self.sqlite.get_data("Deliverymen")
            deliveries = self.sqlite.get_data_where_multi("Deliveries", (("done", 0),))

            asyncio.run(self.runTracker(deliveries, deliverymen))
        except Exception as e:
            self.error.emit(e)

    async def runTracker(self, deliveries, deliverymen):
        current_date = datetime.now()
        day_before = current_date - timedelta(hours=24)
        velide_deliveries = await self.velide.getDeliveries(day_before.timestamp(), current_date.timestamp())

        print(velide_deliveries)
        print(deliveries)

        self.on_update.emit(
            [
                (
                    delivery[1], 
                    next((velide_delivery["location"]["properties"]["name"] for velide_delivery in velide_deliveries if velide_delivery["id"] == delivery[0]), None), 
                    next((deliveryman[2] for deliveryman in deliverymen if deliveryman[0] == delivery[2]), None)
                )
                for delivery in deliveries
            ])

        self.sqlite.close_connection()
        self.sqlite = None
        self.end.emit()