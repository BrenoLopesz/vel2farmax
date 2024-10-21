import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QComboBox, QScrollArea, QTableWidget, QTableWidgetItem, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt, QTimer
from screeninfo import get_monitors
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import asyncio
from screens.load_fonts import loadFonts
from screens.initial_screen import InitialScreen
from screens.device_code_screen import DeviceCodeScreen
from screens.connecting_to_farmax_screen import ConnectingToFarmaxScreen
from screens.configure_deliverymen_screen import ConfigureDeliverymenScreen
from screens.searching_deliveries_screen import SearchingDeliveriesScreen 
from screens.dashboard_screen import DashboardScreen 
from screens.error_screen import ErrorScreen
from utils.device_code import DeviceCode, DeviceCodeDict
from utils.access_token import AccessToken, storeTokenAtFile
from utils.logger import Logger
from utils.sqlite_manager import SQLiteManager 
from workers.authorization_flow import AuthorizationFlow
from workers.connect_to_farmax import ConnectToFarmax
from workers.deliveryman_config_data import DeliverymanConfigData
from workers.integration_worker import IntegrationWorker
from workers.deliveries_tracker import DeliveriesTracker
from workers.stored_token import StoredToken
from workers.refresh_token import RefreshToken
import traceback

load_dotenv(os.path.join("resources", ".env"))

DB_NAME = "resources/vel2farmax.db"

WINDOW_SIZE = [600, 600]
# TODO: Fetch this from Velide (can it change?)
DOMAIN = os.getenv("DOMAIN")
CLIENT_ID = os.getenv("CLIENT_ID")
SCOPE =  os.getenv("SCOPE")
AUDIENCE = os.getenv("AUDIENCE")

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))


host = os.getenv('HOST')
database = os.getenv('DATABASE')
user = os.getenv('USER')
password = os.getenv('PASSWORD')

error_logger = Logger("errorlog", "resources/errors.log")
debug_logger = Logger("debuglog", "resources/debug.log")

def loadCSS():
     # Load the CSS file
    with open(os.path.join(BUNDLE_DIR, 'resources', 'style.css'), 'r') as f:
        return f.read()
    
class ModernGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.loop = asyncio.get_event_loop()
        self.tasks = list()
        self.logger = Logger("log", "resources/vel2farmax.log")
        self.run_integration = False
        self.is_on_error = False

        self.initUI()

    def setupTrayMenu(self):
        # Create a system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.path.join(BUNDLE_DIR, "resources", "velide_white.png")))  # Use an appropriate icon path

        # Create a menu for the tray icon
        tray_menu = QMenu()

        show_action = QAction("Abrir Tela", self)
        show_action_font = show_action.font()
        show_action_font.setBold(True)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)

        exit_action = QAction("Desativar", self)
        exit_action.triggered.connect(self.exit_app)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        if self.is_on_error or not hasattr(self, "tray_icon"):
            return

        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Vel2Farmax",
            "Integração Velide e Farmax está ativa.",
            QSystemTrayIcon.Information,
            2000
        )

    def show_window(self):
        self.showNormal()  # Restore the window if it was minimized
        self.activateWindow()  # Bring the window to the front
        self.show()  # Show the window

    def exit_app(self):
        QApplication.instance().quit()

    def initUI(self):
        self.setWindowTitle('Vel2Farmax')
        self.fonts = loadFonts()
        
        # Set the window icon
        icon_path = os.path.join(BUNDLE_DIR, "resources", "velide.png")  # Use an appropriate icon path
        self.setWindowIcon(QIcon(icon_path))

        self.sqlite = SQLiteManager(DB_NAME)
        self.sqlite.connect()

        self.initialScreen = InitialScreen(self.fonts, self.startAuthorizationFlow, self)
        self.initialScreen.show()

        def onGetStoredToken(token):
            self.initialScreen.close()
            self.access_token = token
            self.tryToConnectToFarmax()

        def onRefreshToken(token):
            storeTokenAtFile(token)
            self.access_token = token["access_token"]
            self.initialScreen.close()
            self.tryToConnectToFarmax()

        def onExpiredToken(refresh_token):
            self.refresh_token = RefreshToken(DOMAIN, CLIENT_ID, SCOPE, refresh_token)
            self.refresh_token.token.connect(onRefreshToken)
            self.refresh_token.error.connect(lambda e: print(e))
            self.refresh_token.start()

        self.stored_token_worker = StoredToken()
        self.stored_token_worker.token.connect(onGetStoredToken)
        self.stored_token_worker.expired.connect(onExpiredToken)
        self.stored_token_worker.start()

        self.setGeometry(round((get_monitors()[0].width / 2) - (WINDOW_SIZE[0] / 2)), round((get_monitors()[0].height / 2) - (WINDOW_SIZE[1] / 2)), WINDOW_SIZE[0], WINDOW_SIZE[1])
        self.setFixedSize(WINDOW_SIZE[0], WINDOW_SIZE[1])
        self.logger.info("Vel2Farmax iniciado.")

    def startAuthorizationFlow(self):
        """
        Generate device token to login into Velide.
        """
        self.initialScreen.close()

        def onError(error: str):
            error_label = QLabel(error, self)
            error_label.setFont(self.regular_font)
            error_label.setAlignment(Qt.AlignCenter)
            error_label.move(184, 381)
            error_label.setObjectName("error")
            return
        
        def onSuccess(access_token):
            self.access_token = access_token
            self.device_code_screen.close()
            self.tryToConnectToFarmax()

        self.device_code_screen = DeviceCodeScreen(fonts=self.fonts, parent=self)
        self.device_code_screen.show()

        self.authorization_flow = AuthorizationFlow(self.logger)
        self.authorization_flow.error.connect(onError)
        self.authorization_flow.signal.connect(onSuccess)
        self.authorization_flow.device_code.connect(self.device_code_screen.setDeviceCode)
        self.authorization_flow.start() 
        

    def tryToConnectToFarmax(self):
        self.connecting_to_farmax_screen = ConnectingToFarmaxScreen(self.fonts, self)
        self.connecting_to_farmax_screen.show()

        def onConnect(farmax_conn):
            # At this point, also start tray menu 
            self.setupTrayMenu()

            self.farmax_conn = farmax_conn
            self.logger.info("Conectado com o Farmax.")
            self.connecting_to_farmax_screen.setConnected()
            QTimer.singleShot(2000, self.onEditDeliverymen)

        def onError(e):
            print(e)
            self.connecting_to_farmax_screen.setError()

        self.connect_to_farmax = ConnectToFarmax()
        self.connect_to_farmax.signal.connect(onConnect)
        self.connect_to_farmax.error.connect(onError)
        self.connect_to_farmax.start()

    def saveDeliverymenMatches(self, listItems, velideDeliverymen):
        deliverymen = [
            (velideDeliverymen[i]["id"], listItem.getCurrentId(), velideDeliverymen[i]["name"])
            for i, listItem in enumerate(listItems)
        ]

        self.sqlite.saveDeliverymen(deliverymen)
    
    def startIntegration(self):
        if(hasattr(self, "configure_deliverymen_screen") and self.configure_deliverymen_screen is not None):
            self.configure_deliverymen_screen.close()

        self.searching_deliveries_screen = SearchingDeliveriesScreen(self, self.fonts)
        self.searching_deliveries_screen.show()

        QTimer.singleShot(1000, self.showDashboard)

    def showDashboard(self):
        self.searching_deliveries_screen.close()
        self.dashboard_screen = DashboardScreen(self, self.fonts, self.logger, lambda: self.onEditDeliverymen(True))
        self.dashboard_screen.show()

        if hasattr(self, "sqlite") and self.sqlite is not None:
            self.sqlite.close_connection()
            self.sqlite = None

        self.run_integration = True
        self.pullDeliveries()
    
    def onEditDeliverymen(self, skip_verification=False):
        self.run_integration = False
        if hasattr(self, "dashboard_screen") and self.dashboard_screen is not None:
            self.dashboard_screen.close()

        def onButtonClick(list_items: list, velide_deliverymen):
            if not hasattr(self, "sqlite") or self.sqlite is None:
                self.sqlite = SQLiteManager(DB_NAME)
                self.sqlite.connect()

            self.saveDeliverymenMatches(list_items, velide_deliverymen)
            self.logger.info("Entregadores correspondentes definidos e salvos localmente.")
            self.startIntegration()

        def onReturn():
            self.configure_deliverymen_screen.close()
            self.showDashboard()

        def showDeliverymenConfigurationScreen(farmax_deliverymen, velide_deliverymen, velide):
            if skip_verification:
                self.configure_deliverymen_screen = ConfigureDeliverymenScreen(self, self.fonts, velide_deliverymen, farmax_deliverymen, lambda list_items: onButtonClick(list_items, velide_deliverymen), True, onReturn)
                self.configure_deliverymen_screen.show()
                return
            
            self.connecting_to_farmax_screen.close()
            self.velide = velide

            if(self.sqlite.areDeliverymenUpToDate([velide_deliveryman["id"] for velide_deliveryman in velide_deliverymen])):
                self.startIntegration()
                return

            self.configure_deliverymen_screen = ConfigureDeliverymenScreen(self, self.fonts, velide_deliverymen, farmax_deliverymen, lambda list_items: onButtonClick(list_items, velide_deliverymen))
            self.configure_deliverymen_screen.show()

        self.deliveryman_config_data = DeliverymanConfigData(self.farmax_conn, self.access_token)
        self.deliveryman_config_data.data.connect(showDeliverymenConfigurationScreen)
        # self.deliveryman_config_data.debug.connect(lambda e: self.setWindowTitle(f"{e}"))
        self.deliveryman_config_data.error.connect(lambda e: self.setWindowTitle(f"{e}"))
        self.deliveryman_config_data.start()

    def pullDeliveries(self):
        # Used to prevent being called while not in the dashboard screen
        if not self.run_integration:
            return
        
        def displayError(e):
            error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
            error_logger.critical(error_message)
            self.dashboard_screen.close()
            self.showErrorScreen()
        
        self.integration_worker = IntegrationWorker(self.farmax_conn, self.velide, self.logger)
        # Restart only after finishing
        self.integration_worker.end.connect(lambda: QTimer.singleShot(4500, self.updateTracker))
        self.integration_worker.error.connect(displayError)
        self.integration_worker.debug.connect(debug_logger.debug)
        self.integration_worker.start()

    def updateTracker(self):
         # Used to prevent being called while not in the dashboard screen
        if not self.run_integration:
            return
        
        def displayError(e):
            error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
            error_logger.critical(error_message)
            self.dashboard_screen.close()
            self.showErrorScreen()
        
        self.deliveries_tracker = DeliveriesTracker(self.velide)
        self.deliveries_tracker.on_update.connect(lambda data_list: self.dashboard_screen.updateTracker([(f"{data[0]}", data[1], "Sim" if data[2] is not None else "Não", data[2]) for data in data_list]))
        self.deliveries_tracker.end.connect(lambda: QTimer.singleShot(500, self.pullDeliveries))
        self.deliveries_tracker.error.connect(displayError)
        self.deliveries_tracker.start()

    def showErrorScreen(self):
        self.is_on_error = True
        self.tray_icon.showMessage(
            "Vel2Farmax",
            "Ocorreu um erro! A integração será reiniciada em breve...",
            QSystemTrayIcon.Critical,
            5000
        )

        self.error_screen = ErrorScreen(self.fonts, self)
        self.error_screen.show()
        self.run_integration = False

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app.setStyleSheet(loadCSS())
        window = ModernGUI()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        error_logger.critical(e)
        raise
