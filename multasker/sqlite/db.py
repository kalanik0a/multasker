import os.path
import sqlite3
import sys
import inspect

from multasker.log import Logger
from multasker.util import Singleton

class DB(metaclass=Singleton):
    def log(self, level, message):
        self.logger.log(level, message)

    def __init__(self,  logger: Logger, logger_config=None, dbname="data.db", update=True):
        self.error_message = None
        self.connection = None
        self.logger = None
        self.cursor = None
        self.result = None
        self.set_logger(logger, logger_config=logger_config)
        self.open_connection(dbname)

    def __del__(self):
        self.connection.commit()
        self.connection.close()
        self.log('debug', 'Database connections closed')

    def handle_error(self, header: str,  message: str, error=None):
        if error is not None:
            self.log('error', f'{header} {message} {type(error)}')
            self.log('error', f'{header} {str(error)}')

    def set_logger(self, logger: Logger, logger_config: dict):
        if logger is not None:
            self.logger = logger
        else:
            self.logger = Logger()
        if logger_config is not None:
            if logger_config['level'] is None:
                logger_config['level'] = 'info'
            if logger_config['stream'] is None:
                logger_config['stream'] = sys.stdout
            self.logger.config(logger_config['level'], logger_config['stream'])

    def open_connection(self, dbname="data.db"):
        try:
            self.connection = sqlite3.connect(dbname)
            self.log('debug', 'Database connection opened')
        except Exception as e:
            self.handle_error(header='[DB.open_connection]', message='Could not open database', error=e)

    def execute(self, execute_query: str, parameters=None, execute_many=False, fetch=-1):
        try:
            if self.connection is None:
                    raise IOError('Connection is not initialized')
            if execute_query is None:
                    raise sqlite3.DataError('query not supplied')
            if parameters is not None:
                if not isinstance(parameters, list):
                    raise SyntaxError('Invalid argument supplied')
            self.cursor = self.connection.cursor()
            self.result = None
            if execute_many is False:
                if parameters is None:
                    self.cursor.execute(execute_query)
                else:
                    self.cursor.execute(execute_query, parameters)
            elif execute_many is True:
                self.cursor.executemany(execute_query, parameters)
            self.connection.commit()
            if fetch < 1:
                self.result = self.cursor.fetchall()
            elif fetch == 1:
                self.result = self.cursor.fetchone()
            elif fetch > 1:
                self.result = self.cursor.fetchmany(fetch)
            return True
        except Exception as e:
            self.handle_error(header='[DB.execute]', message='Could not execute query', error=e)
            return False

