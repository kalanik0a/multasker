from multasker.process import StarMapThreadPool
from multasker.test import Test
from multasker.log import Logger
import os
import json
import time

total_files = []

def test_submit(data):
    return data

def print_filename(filename):
    # This could be practically any function that processes a file
    return filename

def flat_walk(root):
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            file_paths.append(os.path.join(dirpath, filename))
    file_paths = list(set(file_paths))
    return file_paths

class TestStarMapThreadPool(Test):
    total_files = []

    def __init__(self, *args, **kwargs):
        super(TestStarMapThreadPool, self).__init__(*args, **kwargs)
        self.logger.log('debug', 'TestStarMapThreadPool.__init__()')

    def test_map(self):
        self.logger.log('debug', 'TestStarMapThreadPool.test_map()')
        self.starmap = StarMapThreadPool(task_limit=250)
        results = self.starmap.pool_execute(test_submit, [ (f"{hex(int(i))}",) for i in range(0,65535) ])
        flat = [ item for sublist in results for item in sublist ]
        flat = [ item for sublist in flat for item in sublist ]
        flat = [ int(i, 16) for i in flat ]
        for i in range(0,65535):
            self.assertEqual(flat[i], i)
        self.logger.log('debug', len(flat))
        self.assertEqual(len(flat), 65535)
        
    def test_walk(self):
        self.starmap = StarMapThreadPool(task_limit=250)
        self.logger.log('debug', 'Calling os.walk on root')
        scan_path = "C:\\"
        os_walk_time = time.time()
        paths = flat_walk(scan_path)
        os_walk_end_time = time.time()
        self.logger.log('debug', f'Called os.walk() in: {os_walk_end_time - os_walk_time}')
        start_time = time.time()
        self.logger.log('debug', f'f{len(paths)} directory entries in "/"')
        results = self.starmap.pool_execute(print_filename, paths)
        end_time = time.time()
        flat = [ item for sublist in results for item in sublist ]
        count = 0
        for a,b,c in os.walk(scan_path):
            print(c)
            for d in c:
                count += 1
        self.assertEqual(len(flat), count)
        
        
                
