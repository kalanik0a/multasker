import os.path
import sqlite3
import sys
import inspect

from multasker.log import Logger
from multasker.util import Singleton

class DB:
    def log(self, level, message):
        self.logger.log(level, message)

    def __init__(self,  logger: Logger, logger_config=None, dbname="data.db", uri=False, update=True):
        self.error_message = None
        self.connection = None
        self.logger = None
        self.cursor = None
        self.result = None
        self.blob = None
        self.dbname = dbname
        self.set_logger(logger, logger_config=logger_config)
        self.open_connection(dbname, uri=uri)

    def close_blob(self):
        if self.blob:
            try:
                self.blob.close()
            except Exception:
                self.log("warning", "Blob already closed or invalid")
            self.blob = None

    def close(self):
        if self.connection:
            if self.cursor:
                try:
                    self.cursor.close()
                except sqlite3.ProgrammingError:
                    self.log("warning", "Cursor already closed or invalid")
            try:
                self.connection.commit()
            except Exception:
                self.log("warning", "Commit failed; maybe already closed")
            try:
                self.connection.close()
            except Exception:
                self.log("warning", "Connection already closed")
            self.log('debug', 'Connection manually closed')

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

    def open_connection(self, dbname="data.db", uri=False):
        try:
            self.connection = sqlite3.connect(
                dbname,
                uri=uri,
                check_same_thread=False,
                isolation_level=None,  # autocommit mode is safer for WAL
                timeout=10  # wait for locks
            )
            self.connection.execute("PRAGMA journal_mode=WAL;")
            self.connection.execute("PRAGMA synchronous=NORMAL;")  # or FULL for safety
            self.log('debug', 'Database connection opened')
        except Exception as e:
            self.handle_error('[DB.open_connection]', 'Could not open database', e)

    def get_journal_mode(self):
        try:
            cursor = self.connection.cursor()
            mode = cursor.execute("PRAGMA journal_mode;").fetchone()[0]
            cursor.close()
            return mode
        except Exception as e:
            self.handle_error("[DB.get_journal_mode]", "Could not get journal mode", e)
            return None

    def set_journal_mode(self, mode='WAL'):
        try:
            cursor = self.connection.cursor()
            result = cursor.execute(f"PRAGMA journal_mode={mode};").fetchone()[0]
            cursor.close()
            self.log('info', f"Journal mode set to {result}")
            return result
        except Exception as e:
            self.handle_error("[DB.set_journal_mode]", "Failed to set journal mode", e)
            return None

    def open_blob(self, blob_name="blob_000", blob_column="blob_000_col", length=1):
        try:
            if self.connection is None:
                raise IOError('Connection is not initialized')
            else:
                self.blob = self.connection.blobopen(blob_name, blob_column, length)
                return self.blob
        except Exception as e:
            self.handle_error(header='[DB.open_blob]', message='Could not open blob on SQLite3 connection', error=e)
            return False

    def init_query_arguments(self, query: str, parameters=None):
        try:
            if self.connection is None:
                    self.open_connection(self.dbname)
            if query is None:
                    raise sqlite3.DataError('query not supplied')
            if parameters is not None:
                if not isinstance(parameters, list):
                    raise SyntaxError('Invalid argument supplied')
        except Exception as e:
            self.handle_error(header='[DB.init_query_arguments]',
                              message='Could not start query. Invalid arguments',
                              error=e)

    def fetch_results(self, result_count=-1):
        try:
            if result_count < 1:
                self.result = self.cursor.fetchall()
            elif result_count == 1:
                self.result = self.cursor.fetchone()
            elif result_count > 1:
                self.result = self.cursor.fetchmany(result_count)
        except Exception as e:
            self.handle_error(header='[DB.fetch_results]', message='Could not fetch results from cursor', error=e)

    def execute(self, execute_query: str, parameters=None, execute_many=False, fetch=-1):
        try:
            self.init_query_arguments(query=execute_query, parameters=parameters)
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
            self.fetch_results(fetch)
            return True
        except sqlite3.IntegrityError as e:
            self.handle_error('[DB.execute]', 'Constraint violation (e.g., duplicate primary key)', e)
            return False
        except Exception as e:
            self.handle_error(header='[DB.execute]', message='Could not execute query', error=e)
            return False

    def execute_script(self, script: str):
        try:
            self.init_query_arguments(query=script)
            self.cursor = self.connection.cursor()
            self.result = self.cursor.executescript(script)
            self.connection.commit()
            self.fetch_results()
            return True
        except Exception as e:
            self.handle_error(header='[DB.execute_script]', message='Could not execute SQLite script', error=e)
            return False
