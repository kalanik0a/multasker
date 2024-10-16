# multasker
A multitasking library with a logging facility and test driven development

# Classes

```
multasker.log.Logger - A logging facility using the logging module
multasker.test.Test - A test driven development facility using the unittest module
multasker.StarMapThreadPool - A batch processing multiprocessing facility using the multiprocessing module
multasker.ThreadPoolExecutor - A batch processing multithreading facility using the concurrent.futures module
```

# Tests

```
test.TestLogger - Tests the logging facility and confirms unittest is functioning
test.TestStarMapThreadPool - Tests the multiprocessing facility
test.TestThreadPoolExecutor - Tests the multithreading facility
```

# Installation

```bash
git clone <clone_url>
cd /path/to/multasker
python3 setup.py install
```

# Uninstallation

```
pip uninstall multasker
```


# Logging Usage

```python
# First 
from multasker.log import Logger

# One way of doing it
logger = Logger().get_logger()
logger.debug('(empty call) This is a debug message')
logger.info('(empty call) This is an info message')
logger.warning('(empty call) This is a warning message')
logger.error('(empty call) This is an error message')
logger.critical('(empty call) This is a critical message')

# Another way of doing it
logger = Logger()
logger.log('debug', 'This is a debug message')
logger.log('info', 'This is an info message')
logger.log('warning', 'This is a warning message')
logger.log('error', 'This is an error message')
logger.log('critical', 'This is a critical message')
```

# Multithreading Usage Example

```python
import concurrent.futures
import time
from multasker.process.ThreadPoolExecutor import ThreadPoolExecutor

def task_with_delay():
    self.logger.log('debug', 'task_with_delay() called')
    time.sleep(0.5)
    return 11

pool = ThreadPoolExecutor(max_workers=50, thread_name_prefix='test-threadpoolexecutor')
time_a = time.time()
futures = [ pool.submit(task_with_delay) for i in range(250) ]
results = [ future.result() for future in concurrent.futures.as_completed(futures) ] 
time_b = time.time()
self.logger.log('info', f'Time elapsed: {time_b - time_a}')
total = 0
for result in results:
    total += result
print(total)
pool.shutdown()
```

# Multiprocessing Usage Example - Processes and Threads

```python
from multitasker.process import StarMapThreadPool

def print_filename(filename):
    # Process data on file path here
    return filename

def flat_walk(root):
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            file_paths.append(os.path.join(dirpath, filename))
    file_paths = list(set(file_paths))
    return file_paths

paths = flat_walk('/')
starmap = StarMapThreadPool(task_limit=250)
starmap.pool_execute(print_filename, paths)
flat = [ item for sublist in results for item in sublist ]

for file in flat:
	print(file)

```


# Test Usage

```python

# First
from multasker.test import Test


class TestClass(Test):
	def __init__(self):
		super().__init__()

	def test_method(self):
		self.assertEqual(1, 1)
		self.assertNotEqual(1, 2)
		self.assertTrue(True)
		self.assertFalse(False)
		self.assertIsNone(None)
		self.assertIsNotNone(1)
		self.assertIn(1, [1, 2, 3])
		self.assertNotIn(4, [1, 2, 3])
		self.assertIsInstance(1, int)
		self.assertNotIsInstance(1, str)

# One way of doing it
if __name__ == '__main__':
	test = TestClass()
	test.test_method()

# Another way of doing it
if __name__ == '__main__':
	test = TestClass()
	test.run()

# Or with the test suite itself 
import unittest
if __name__ == '__main__':
	unittest.main()
```
