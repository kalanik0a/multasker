import os.path
import yaml

from multasker.log import Logger
from multasker import util

class Configuration:
    def log(self, level='', message=''):
        if (level != '') and (message != ''):
            self.logger.log(level, message)

    def log_error(self, header='ERROR', message='', error=None):
        if error is not None:
            self.log('ERROR', f'[{header}] {message} {type(error)}')
            self.log('ERROR', f'[{header}] {str(error)}')

    def __init__(self, config_path='conf.yaml'):
        self.logger = Logger()
        if os.path.exists(os.path.abspath(config_path)):
            self.log('INFO', f'Loading configuration: {config_path}')
            self.config = self.open_config_file(config_path)
        else:
            self.log('INFO', 'Opening with no configuration')
            self.log('DEBUG', f'Basepath: {os.path.abspath(config_path)}')
            self.config = None

    def open_file_path(self, file_path=None):
        try:
            file_object = util.File(file_path=file_path, file_mode='r', logger=self.logger)
            file_handle = file_object.open()
            if isinstance(file_handle, dict):
                raise file_handle['error']
            else:
                file_contents = file_object.read()
                return file_contents
        except Exception as e:
            self.log_error('Configuration.open_file_path', 'Could not open file path for reading', e)
            return None

    def open_config_file(self, config_path=None):
        try:
            config_file = util.File(file_path=config_path, file_mode='r')
            if isinstance(config_file, dict):
                raise config_file['error']
            else:
                self.config = yaml.safe_load(config_file.open())
                return self.get_config()
        except Exception as e:
            self.log_error('Configuration.open_config_file', f'Could not open config file {config_path}', e)
            return None

    def get_config(self):
        return self.config