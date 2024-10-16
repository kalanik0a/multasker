import os
import sys
import unittest

sys.path.append(os.path.abspath('../../multasker'))

from multasker.log import Logger

class Test(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
        self.logger = Logger(loglevel='DEBUG', output=sys.stdout)