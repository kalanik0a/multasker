from .FileHasher import FileHasher
from multasker.test import Test

class TestTwoQueue(Test):
    def __init__(self, method):
      super(TestTwoQueue, self).__init__(method)
      info = self.logger.get_logging_level('info')
      self.logger.get_logger().setLevel(info)
      
    def test_twoqueue_filehash_demo(self):
      print('called')
      FileHasher.set_num_workers(6)
      FileHasher.set_worker(FileHasher.worker,  FileHasher.load_existing_paths('DB-name.db'))
      FileHasher.set_batch(FileHasher.db_writer, 'DB-name.db')
      FileHasher.set_path('/mnt/d/Code/Python')
      FileHasher.process_data(FileHasher.queue_callback)