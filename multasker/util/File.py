import os
import hashlib

from multasker.log import Logger

class File:
    @staticmethod
    def get_read_size(file_size_bytes: int, chunk_size: int):
        output = None
        read_size = None
        file_size = None
        if file_size_bytes < chunk_size:
            read_size = file_size_bytes
            file_size  = 'tiny'
        elif (1024 * 1024 * 16) < file_size_bytes < (1024 * 1024 * 1024):
            read_size = file_size_bytes if file_size_bytes < (1024 * 1024 * 16) else 1024 * 1024 * 16
            file_size = 'small'
        elif file_size_bytes >= (1024 * 1024 * 1024 * 10):
            read_size = 1024 * 1024 * 64
            file_size = 'huge'
        elif file_size_bytes >= (1024 * 1024 * 1024):
            read_size = 1024 * 1024 * 32
            file_size = 'large'
        output = { 'file_size' : file_size, 'read_size' : read_size }
        return output

    @staticmethod
    def hash_file(file_path: str, chunk_size=4096, digest_algorithm='sha256', logger=None):
        try:
            file_object = File(file_path=file_path, file_mode='rb')
            file_handle = file_object.open()
            if isinstance(file_handle, dict):
                return None
            else:
                hasher = hashlib.new(digest_algorithm)
                file_size_bytes = os.path.getsize(file_path)
                size_data = File.get_read_size(file_size_bytes=file_size_bytes, chunk_size=chunk_size)
                for chunk in iter(lambda: file_object.read(size_data['read_size']), b""):
                    hasher.update(chunk)
                return hasher.hexdigest()
        except Exception as  e:
            if isinstance(logger, Logger):
                logger.log_error(header='File.hash_file', message=f'Error hashing file {file_path}', error=e)
            return None

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

    def read(self, read_size=None):
        do_not_continue = self.check_params()
        if do_not_continue is None:
            do_not_continue = self.handle_readable()
        if do_not_continue is None:
            if isinstance(read_size, int):
                return self.file_handle.read(read_size)
            else:
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