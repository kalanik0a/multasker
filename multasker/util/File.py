import os

from multasker.log import Logger

class File:
    def __init__(self, file_path=None, file_mode='r', logger=None):
        if isinstance(logger, Logger):
            self.logger = logger
        else:
            self.logger = None
        self.file_path = file_path
        self.file_mode = file_mode
        self.file_handle = None

    def log(self, level='', message=''):
        if (self.logger is not None) and (level != '') and (message != ''):
            self.logger.log(level, message)

    def log_error(self, header='ERROR', message='', error=None):
        if error is not None:
            self.log('ERROR', f'[{header}] {message} {type(error)}')
            self.log('ERROR', f'[{header}] {str(error)}')

    def mode_check(self):
        if self.file_mode is None:
            return { 'message': 'File mode is not set', 'error': ValueError('self.file_mode is not defined') }
        else:
            return None

    def path_check(self):
        if (self.file_path is None):
            return { 'message': 'No file path', 'error': ValueError('self.file_path is not defined') }
        else:
            return None


    def path_exists(self):
        if os.path.exists(os.path.abspath(self.file_path)):
            return None
        else:
            return { 'message': 'File path does not exist', 'error': FileNotFoundError(f'{self.file_path} does not exist')}

    def handle_available(self):
        if self.file_handle is None:
            return None
        else:
            return {'message': 'File handle already open', 'error': IOError('self.file_handle is already open') }

    def handle_readable(self):
        if (self.file_handle is not None) and (self.file_handle.read is not None):
            return None
        else:
            return { 'message': 'File handle not readable', 'error': ValueError('self.file_handle has no read method') }

    def check_params(self):
        do_not_continue = None
        do_not_continue = self.path_check()
        if do_not_continue is None:
            do_not_continue = self.mode_check()
        if do_not_continue is None:
            do_not_continue = self.path_check()
        if do_not_continue is None:
            do_not_continue = self.path_exists()
        return do_not_continue

    def open(self):
        do_not_continue = self.check_params()
        if do_not_continue is None:
            do_not_continue = self.handle_available()
        if do_not_continue is None:
            self.file_handle = open(self.file_path, self.file_mode)
            return self.file_handle
        else:
            self.log_error(header='File.open', message=do_not_continue['message'], error=do_not_continue['error'])
            return do_not_continue

    def read(self):
        do_not_continue = self.check_params()
        if do_not_continue is None:
            do_not_continue = self.handle_readable()
        if do_not_continue is None:
            return self.file_handle.read()
        else:
            self.log_error(header='File.read', message=do_not_continue['message'], error=do_not_continue['error'])
            return do_not_continue

    def close(self):
        if self.file_handle is not None:
            self.file_handle.flush()
            self.file_handle.close()
            self.file_handle = None

    def __del__(self):
        self.close()