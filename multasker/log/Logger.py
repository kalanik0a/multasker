import logging
import logging.handlers
import os
import sys
import uuid
import multiprocessing
from multiprocessing import Lock

class Logger():
    _instance = None
    _loggers = {}
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._queue = multiprocessing.Queue()
            cls._instance._loggers = {}
            if os.getpid() == os.getppid():  # Check if this is the main process
                cls._instance._listener_process = multiprocessing.Process(target=cls._instance._listener)
                cls._instance._listener_process.start()
            else:
                cls._instance._listener_process = None
        return cls._instance

    def __init__(self, loglevel='debug', output=sys.stdout):
        self.guid = id(self)
        self.loglevel = self.get_logging_level(loglevel)
        self.output = output
        self.config()

    def config(self, level=None, stream=None):
        with self._lock:
            if self.guid not in self._loggers:
                logger = logging.getLogger(str(self.guid))
                handler = logging.StreamHandler(stream)
                formatter = logging.Formatter('[%(asctime)s][%(processName)s][%(levelname)s] %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(self.loglevel)
                self._loggers[self.guid] = logger

    def stop_listener(self):
        with self._lock:
            for logger in self._loggers.values():
                for handler in logger.handlers:
                    handler.close()
                logger.handlers.clear()
            self._loggers.clear()

    def get_logger(self):
        return self._loggers[self.guid]

    def get_logging_level(self, level=None):
        if level == 'debug':
            # Most messages
            # Lowest level, such as 10
            level = logging.DEBUG
        elif level == 'info':
            level = logging.INFO
        elif level == 'warning':
            level = logging.WARNING
        elif level == 'error':
            level = logging.ERROR
        elif level == 'critical':
            # Least messages
            # Highest level, such as 50
            level = logging.CRITICAL
        else:
            level = logging.DEBUG
        return level

    def log(self, level, message):
        logger = self.get_logger()
        level = self.get_logging_level(level)
        logger.log(level, message)