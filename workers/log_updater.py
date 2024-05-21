from PyQt5.QtCore import QThread, pyqtSignal

class LogUpdater(QThread):
    signal = pyqtSignal(str)

    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def run(self):
        log_content = self.logger.get_log_data()
        log_content.reverse()
        text = "".join(log_content)
        self.signal.emit(text)