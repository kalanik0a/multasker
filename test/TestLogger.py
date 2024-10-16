import sys
import os
import threading
import multiprocessing

from multasker.log import Logger
from multasker.test import Test

def thread_function(thread_id):
    logger = Logger(loglevel='DEBUG', output=sys.stdout).get_logger()
    logger.debug(f'Thread {thread_id} started')
    logger.debug(f'Thread {thread_id} finished')

def process_function(process_id):
    threads = []
    for i in range(11):  # Create 5 threads per process
        thread = threading.Thread(target=thread_function, args=(f'{process_id}-{i}',))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

class TestLogger(Test):
    def __init__(self, method):
        super(TestLogger, self).__init__(method)

    def test_b(self):
        logging_level = self.logger.get_logging_level('critical')
        debug_level = self.logger.get_logging_level('debug')
        self.logger.get_logger().setLevel(logging_level)
        self.logger.log('debug', 'this should not be seen')
        self.logger.log('critical', 'this should be seen')
        self.logger.get_logger().setLevel(debug_level)
        self.logger.log('debug', 'this should be seen')

    def test_a(self):
        self.logger.log('debug', 'This is a debug message')
        self.logger.log('info', 'This is an info message')
        self.logger.log('warning', 'This is a warning message')
        self.logger.log('error', 'This is an error message')
        self.logger.log('critical', 'This is a critical message')

    def test_c(self):
        processes = []
        for i in range(11):  # Create 3 processes
            process = multiprocessing.Process(target=process_function, args=(i,))
            processes.append(process)
            process.start()
        for process in processes:
            process.join()

        Logger().stop_listener()
        
    def test_barecall_logger(self):
        logger = Logger().get_logger()
        logger.debug('(empty call) This is a debug message')
        logger.info('(empty call) This is an info message')
        logger.warning('(empty call) This is a warning message')
        logger.error('(empty call) This is an error message')
        logger.critical('(empty call) This is a critical message')