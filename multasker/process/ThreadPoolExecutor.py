import concurrent.futures
from multasker.log import Logger

class ThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    def __init__(self, max_workers=None, thread_name_prefix=''):
        super().__init__(max_workers, thread_name_prefix)
        self._max_workers = max_workers
        self._thread_name_prefix = thread_name_prefix
        self.logger = Logger()

    def submit(self, fn, *args, **kwargs):
        self.logger.log('debug', f"ThreadPoolExecutor.submit() called with {fn} and {args}")
        return super().submit(fn, *args, **kwargs)

    def map(self, fn, *iterables, timeout=None, chunksize=1):
        self.logger.log('debug', f"ThreadPoolExecutor.map() called with {fn} and {iterables}")
        return super().map(fn, *iterables, timeout=timeout, chunksize=chunksize)

    def shutdown(self, wait=True):
        return super().shutdown(wait=wait)