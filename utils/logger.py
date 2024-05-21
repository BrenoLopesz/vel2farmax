import os
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import sys

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
else:
    BUNDLE_DIR = os.path.join(os.path.dirname(os.path.realpath( __file__ )), "..")
    
class Logger:
    def __init__(self, name, log_file):
        log_dir = os.path.dirname(os.path.join(BUNDLE_DIR, log_file))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        file_handler = TimedRotatingFileHandler(os.path.join(BUNDLE_DIR, log_file), when='midnight', interval=1, backupCount=7, encoding='utf-8')
        file_handler.suffix = '%Y-%m-%d.log'
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s', '%d/%m/%y (%H:%M:%S)')
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        
        self.log_file = log_file

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def get_log_data(self):
        log_data = []
        with open(os.path.join(BUNDLE_DIR, self.log_file), 'r', encoding='utf-8') as file:
            log_data = file.readlines()
        return log_data