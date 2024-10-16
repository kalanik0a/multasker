import concurrent.futures
import time
from multasker.process import ThreadPoolExecutor
from multasker.test.Test import Test

class TestThreadPoolExecutor(Test):
    def __init__(self, method):
        super(TestThreadPoolExecutor, self).__init__(method)
        info = self.logger.get_logging_level('info')
        self.logger.get_logger().setLevel(info)

    def task_with_delay(self):
        self.logger.log('debug', 'task_with_delay() called')
        time.sleep(0.5)
        return 11

    def test_a(self):
        pool = ThreadPoolExecutor(max_workers=50, thread_name_prefix='test-threadpoolexecutor')
        self.logger.log('info', 'Queueing 250 tasks to sleep for 0.5s and returning a number')
        time_a = time.time()
        futures = [ pool.submit(self.task_with_delay) for i in range(250) ]
        self.logger.log('info', 'Getting results from tasks')
        results = [ future.result() for future in concurrent.futures.as_completed(futures) ] 
        time_b = time.time()
        self.logger.log('info', f'Time elapsed: {time_b - time_a}')
        self.logger.log('debug', results)
        total = 0
        for result in results:
            total += result
        self.logger.log('info', 'Verifying work from 250 tasks with sleep in them')
        self.assertEqual(total, 2750)
        pool.shutdown()