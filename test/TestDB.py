from sqlite3.dbapi2 import paramstyle
from multiprocessing import Process
from multasker.log import Logger
from multasker.sqlite import DB
from multasker.test import Test
import time
from uuid import uuid4

def db_worker(index):
    logger = Logger()
    db = DB(logger=logger, dbname='test.db')
    db.execute('INSERT INTO test VALUES (?, ?)', parameters=[[f"path_{index}", f"hash_{index}"]], execute_many=True)
    db.close()

def delayed_insert(index, delay=0.1):
    logger = Logger()
    db = DB(logger=logger, dbname='test.db')
    time.sleep(index * delay)
    unique_id = uuid4().hex
    db.execute('INSERT OR IGNORE INTO test VALUES (?, ?)', parameters=[[f"path_{unique_id}", f"hash_{unique_id}"]], execute_many=True)
    db.close()

def log_test_start(logger, name):
    logger.log('info', '=' * 50)
    logger.log('info', f"STARTING TEST: {name}")
    logger.log('info', '=' * 50)

class TestDB(Test):
    def __init__(self, method):
        super(TestDB, self).__init__(method)

    def test_20_drop_table(self):
        logger = Logger()
        db = DB(logger=logger, dbname='test.db')
        result = db.execute('DROP TABLE test')
        self.assertTrue(result)

    def test_10_concurrent_read_after_write(self):
        logger = Logger()
        log_test_start(logger, "test_10_concurrent_read_after_write")
        db = DB(logger=logger, dbname='test.db')
        db.execute('SELECT COUNT(*) FROM test', fetch=1)
        logger.log('info', f"Row count after concurrent writes: {db.result[0]}")
        self.assertTrue(db.result[0] >= 12)  # assuming previous writes ran
        db.close()

    def test_09_lock_contention_insert(self):
        logger = Logger()
        log_test_start(logger, "test_09_lock_contention_insert")
        processes = [Process(target=delayed_insert, args=(i,)) for i in range(8)]
        for p in processes:
            p.start()
        for p in processes:
            p.join()
        self.database = DB(logger=logger, dbname='test.db')
        self.database.execute('SELECT COUNT(*) FROM test', fetch=1)
        self.assertTrue(self.database.result[0] >= 20)

    def test_08_check_wal_mode(self):
        logger = Logger()
        log_test_start(logger, "test_08_check_wal_mode")
        db = DB(logger=logger, dbname='test.db')
        mode = db.get_journal_mode()
        logger.log('info', f"WAL Mode = {mode}")
        self.assertEqual(mode.upper(), 'WAL')
        db.close()

    def test_07_multiprocess_insert(self):
        logger = Logger()
        log_test_start(logger, "test_07_multiprocess_insert")
        processes = [Process(target=db_worker, args=(i,)) for i in range(12)]
        for p in processes:
            p.start()
        for p in processes:
            p.join()
        self.database = DB(logger=logger, dbname='test.db')
        self.database.execute('SELECT COUNT(*) FROM test', fetch=1)
        self.assertTrue(self.database.result[0] >= 12)

    def test_06_do_blob(self):
        logger = Logger()
        log_test_start(logger, "test_06_do_blob")
        self.database = DB(dbname='file:shared_mem?mode=memory&cache=shared', uri=True, logger=logger)
        self.database.log('info', 'test_06_do_blob')
        result = self.database.execute_script('''   
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS test_b(blob_col blob);
            INSERT INTO test_b(blob_col) VALUES(zeroblob(13));
            PRAGMA locking_mode = NORMAL;
        ''')
        self.assertTrue(result)
        self.blob = self.database.open_blob('test_b', 'blob_col')
        if self.blob is False:
            print('Could not open blob')
        else:
            self.blob.write(b'hello, ')
            self.blob.write(b'world.')
            self.blob[0] = ord('H')
            self.blob[-1] = ord('!')
            self.database.connection.commit()
            self.database.close_blob()
        self.database.execute('DROP TABLE test_b')
        self.database.close()

    def test_05_execute_script(self):
        logger = Logger()
        log_test_start(logger, "test_05_execute_script")
        self.database = DB(dbname='test.db', logger=logger)
        self.database.log('info', 'test_05_execute_script')
        self.database.execute_script('''
            CREATE TABLE IF NOT EXISTS test_02 ( id INT PRIMARY KEY, text STRING );
            CREATE TABLE IF NOT EXISTS test_03 ( id INT PRIMARY KEY, text STRING );
            CREATE TABLE IF NOT EXISTS test_04 ( id INT PRIMARY KEY, text STRING );
        ''')
        self.database.execute_script('''
            DROP TABLE test_02;
            DROP TABLE test_03;
            DROP TABLE test_04;
        ''')
        self.database.close()

    def test_04_do_select(self):
        logger = Logger()
        log_test_start(logger, "test_04_do_select")
        self.database = DB(dbname='test.db', logger=logger)
        self.database.execute('SELECT * FROM test', fetch=2)
        logger.log('info', 'SELECT * FROM test')
        logger.log('info', f'Results {self.database.result}')
        self.assertEqual(len(self.database.result), 2)
        self.database.close()

    def test_03_insert_many(self):
        logger = Logger()
        log_test_start(logger, "test_03_insert_many")
        self.database = DB(dbname='test.db', logger=logger)
        parameters = [('path.txt', 'abcd'), ('second.txt', 'bcde'), ('third.txt', 'ecdfg')]
        result = self.database.execute('''INSERT OR REPLACE INTO test VALUES (?, ?)''', parameters=parameters, execute_many=True)
        self.database.close()
        self.assertTrue(result)

    def test_02_param(self):
        logger = Logger()
        log_test_start(logger, "test_02_param")
        self.database = DB(dbname='test.db', logger=logger)
        result = self.database.execute('''
            SELECT path FROM test WHERE hash = ?
        ''', parameters=True)
        logger.log('info', 'Database execute query')
        self.database.close()
        self.assertFalse(result)

    def test_01_open(self):
        logger = Logger()
        log_test_start(logger, "test_01_open")
        self.database = DB(dbname='test.db', logger=logger)
        result = self.database.execute('''CREATE TABLE IF NOT EXISTS test (
            path TEXT PRIMARY KEY,
            hash TEXT
        )''')
        self.database.execute_script('PRAGMA journal_mode=WAL;')
        self.database.close()
        self.assertTrue(result)

    def __del__(self):
        print('-' * 20)