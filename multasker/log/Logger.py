import json
import logging
import logging.handlers
import os
import sys
import uuid
import multiprocessing
import atexit
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

    def __init__(self, loglevel='debug', output=sys.stdout, logformat=None):
        self.guid = id(self)
        self.loglevel = self.get_logging_level(loglevel)
        self.output = output
        if logformat is None:
            self.log_format = '[%(asctime)s][%(processName)s][%(levelname)s] %(message)s'
        else:
            self.log_format = logformat
        self.output_format = '%(message)'
        self.config(level=self.loglevel, stream=self.output, format=self.log_format)
        atexit.register(self.stop_listener)

    def config(self, level=None, stream=None, format=''):
        with self._lock:
            logger_entry = self._loggers.get(self.guid)

            # Resolve the stream
            resolved_stream = None
            opened_file = None

            if isinstance(stream, str):
                # Treat as a path — ensure directory exists
                os.makedirs(os.path.dirname(os.path.abspath(stream)), exist_ok=True)
                opened_file = open(stream, 'a', encoding='utf-8')  # Open file for appending
                resolved_stream = opened_file
            elif hasattr(stream, 'write'):
                # Treat as file-like object
                resolved_stream = stream
            else:
                # Default fallback
                resolved_stream = sys.stdout

            if logger_entry is None:
                logger = logging.getLogger(str(self.guid))
            else:
                logger = logger_entry['logger']
                # Remove existing handlers
                for h in logger.handlers[:]:
                    logger.removeHandler(h)

            # Create new handler
            handler = logging.StreamHandler(resolved_stream)
            formatter = logging.Formatter(format or self.log_format)
            handler.setFormatter(formatter)
            handler.setLevel(level or self.loglevel)
            logger.addHandler(handler)
            logger.setLevel(level or self.loglevel)

            # Store logger and stream
            self._loggers[self.guid] = {
                "logger": logger,
                "stream": opened_file or resolved_stream
            }

    def stop_listener(self):
        with self._lock:
            for logger_entry in self._loggers.values():
                logger = logger_entry['logger']
                stream = logger_entry.get('stream')

                # Close and remove all handlers
                for handler in logger.handlers[:]:
                    try:
                        handler.close()
                    except Exception as e:
                        sys.stderr.write(f"Error closing handler: {e}")
                        sys.stderr.flush()
                    logger.removeHandler(handler)

                # Close the stream if it's a file we opened (not stdout/stderr)
                if stream and hasattr(stream, 'close') and not stream.closed:
                    if stream not in (sys.stdout, sys.stderr):
                        try:
                            stream.close()
                        except Exception as e:
                            sys.stderr.write(f"Error closing stream: {e}")
                            sys.stderr.flush()

            self._loggers.clear()

    def get_logger(self):
        return self._loggers[self.guid]

    def get_logging_level(self, level=None):
        level = level.lower()
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
        logger = self.get_logger()['logger']
        level = self.get_logging_level(level)
        logger.log(level, message)

    def log_error(self, header='ERROR', message='', error=None):
        if error is not None:
            self.log('ERROR', f'[{header}] {message} {type(error)}')
            self.log('ERROR', f'[{header}] {str(error)}')

    def write_out(self, header='', message=''):
        output = ''
        if header == '':
            output = f'{message}\n'
        else:
            output = f'{header} {message}\n'
        self.output.write(output)
        self.output.flush()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_listener()