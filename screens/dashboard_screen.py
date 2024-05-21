from screens.load_fonts import FontsDict
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
from PyQt5.QtCore import Qt, QTimer
from workers.log_updater import LogUpdater

class DashboardScreen:
    def __init__(self, parent: QWidget, fonts: FontsDict, logger, onEditDeliverymen):
        self.logger = logger
        self.parent = parent
        self.fonts = fonts
        self.screen_width = 600
        self.integration_active = None
        self.deliveries_area = None
        self.log_area = None
        self.onEditDeliverymen = onEditDeliverymen

    def show(self):
        # Show integration active label
        self.integration_active = QLabel("Integração ativa<br/>e operando.", self.parent)
        self.integration_active.setObjectName("success")
        self.integration_active.setFont(self.fonts["regular"])
        self.integration_active.setAlignment(Qt.AlignCenter)
        self.integration_active.setFixedWidth(self.screen_width)
        self.integration_active.move(0, 24)

        # Show scroll area for deliveries
        self.deliveries_area = QScrollArea(self.parent)
        self.deliveries_layout = QVBoxLayout(self.deliveries_area)
        self.deliveries_area.setLayout(self.deliveries_layout)
        self.deliveries_area.setFixedSize(568, 232)
        self.deliveries_area.move(16, 94)
        self.deliveries_area.show()

        self.deliveries_table = QTableWidget()
        self.deliveries_table.setColumnCount(4)  # Set the number of columns
        self.deliveries_table.setHorizontalHeaderLabels(["Venda", "Endereço", "Em rota?", "Entregador"])  # Set column headers
        self.deliveries_table.setSelectionBehavior(QTableWidget.SelectRows)  # Set selection behavior to select entire rows
        self.deliveries_layout.addWidget(self.deliveries_table)

        # Set stretch last section
        header = self.deliveries_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.deliveries_table.resizeColumnsToContents()
        self.deliveries_table.resizeRowsToContents()

        # Show scroll area for log
        self.log_area = QScrollArea(self.parent)
        self.log_area.setFixedSize(568, 158)
        self.log_area.move(16, 345)
        self.log_area.show()

        self.timer = QTimer(self.parent)
        self.timer.timeout.connect(self.updateLog)
        self.timer.start(500) 

        self.edit_deliverymen_button = QPushButton('Configurar Entregadores', self.parent)
        self.edit_deliverymen_button.clicked.connect(self.onEditDeliverymen)
        self.edit_deliverymen_button.setFont(self.fonts["bold"])
        self.edit_deliverymen_button.setObjectName("black")
        self.edit_deliverymen_button.move(159, 524)
        self.edit_deliverymen_button.show()

    def updateLog(self):
        def onUpdate(text):
            if not hasattr(self, "label") or self.label.parent is None:
                self.log_content_widget = QWidget()
                self.log_content_layout = QVBoxLayout(self.log_content_widget)
                self.label = QLabel()
                self.log_content_layout.addWidget(self.label)
                self.log_area.setWidget(self.log_content_widget)
                
                # Adjust size policy to Expanding for the label to fill the layout size
                self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            self.label.setText(text)
            # Set word wrap to True for line wrapping
            self.label.setWordWrap(True)

            self.label.adjustSize()
            self.log_content_widget.adjustSize()
            self.label.show()

        self.log_updater = LogUpdater(self.logger)
        self.log_updater.signal.connect(onUpdate)
        self.log_updater.start()

    def updateTracker(self, data):
        previous_count = self.deliveries_table.rowCount

        self.deliveries_table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                self.deliveries_table.setItem(i, j, QTableWidgetItem(item))  # Set item in the table

        # If data has not changed, don't resize
        if previous_count == len(data):
            return
        
        self.deliveries_table.resizeRowsToContents()

        # Initial resize should update columns too.
        if previous_count == 0:
            self.deliveries_table.resizeColumnsToContents()

    def close(self):
        if hasattr(self, "integration_active") and self.integration_active is not None:
            self.integration_active.setParent(None)
        if hasattr(self, "deliveries_area") and self.deliveries_area is not None:
            self.deliveries_area.setParent(None)
        if hasattr(self, "log_area") and self.log_area is not None:
            self.log_area.setParent(None)
        if hasattr(self, "timer") and self.timer is not None:
            self.timer.stop()
            self.timer.setParent(None)
        if hasattr(self, "edit_deliverymen_button") and self.edit_deliverymen_button is not None:
            self.edit_deliverymen_button.setParent(None)


