# multasker
A multitasking library with a logging facility and test driven development

# API

```
multasker.log.Logger - A logging facility using the logging module
multasker.test.Test - A test driven development facility using the unittest module
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

# Todo

```
Multithreading with the threading module
Multiprocessing with the multiprocessing module
```