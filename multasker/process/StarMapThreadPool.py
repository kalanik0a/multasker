# based on the threading and process model from DFScanner.py in DupllicateFinder

import multiprocessing
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import time

from multasker.log import Logger

def init_lock(lock):
    global global_lock
    global_lock = lock

def thread_execute_wrapper(data, batch_function, logger):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(safe_execute, batch_function, item, logger) for item in data]
        return [future.result() for future in futures]

def safe_execute(batch_function, item, logger):
    return batch_function(item)

class StarMapThreadPool():
    pool_data = []

    def __init__(self, task_limit=10):
        self.logger = Logger().get_logger()
        self.process_limit = multiprocessing.cpu_count()
        self.task_limit = task_limit
        self.thread_results = []
        self.manager = multiprocessing.Manager()
        self.lock = self.manager.Lock()  # Initialize the lock

    
    def pool_execute(self, batch_function, exec_iter):
        StarMapThreadPool.pool_data = exec_iter  # Initialize pool_data with exec_iter
        with multiprocessing.Pool(processes=self.process_limit, initializer=init_lock, initargs=(self.lock,)) as pool:
            pool_results = pool.starmap(
                thread_execute_wrapper,
                [(StarMapThreadPool.pool_data[i:i+self.task_limit], batch_function, self.logger) for i in range(0, len(StarMapThreadPool.pool_data), self.task_limit)]
            )
        return pool_results
