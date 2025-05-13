from sqlite3.dbapi2 import paramstyle

from multasker.log import Logger
from multasker.sqlite import DB
from multasker.test import Test

class TestDB(Test):
    def __init__(self, method):
        super(TestDB, self).__init__(method)

    def test_04_do_select(self):
        logger = Logger()
        self.database = DB(dbname='test.db', logger=logger)
        self.database.execute('SELECT * FROM test', fetch=2)
        logger.log('info', 'SELECT * FROM test')
        logger.log('info', f'Results {self.database.result}')
        self.assertEqual(len(self.database.result), 2)

    def test_03_insert_many(self):
        logger = Logger()
        self.database = DB(dbname='test.db', logger=logger)
        parameters = [('path.txt', 'abcd'), ('second.txt', 'bcde'), ('third.txt', 'ecdfg')]
        result = self.database.execute('''INSERT OR REPLACE INTO test VALUES (?, ?)''', parameters=parameters, execute_many=True)
        logger.log('info', 'INSERT many test')
        self.assertTrue(result)

    def test_02_param(self):
        logger = Logger()
        self.database = DB(dbname='test.db', logger=logger)
        self.database.log('debug', 'test_bad_param')
        result = self.database.execute('''
            SELECT path FROM test WHERE hash = ?
        ''', parameters=True)
        logger.log('info', 'Database execute query')

        self.assertFalse(result)

    def test_01_open(self):
        logger = Logger()
        self.database = DB(dbname='test.db', logger=logger)
        logger.log('debug', 'test_open')
        result = self.database.execute('''CREATE TABLE IF NOT EXISTS test (
            path TEXT PRIMARY KEY,
            hash TEXT
        )''')
        self.assertTrue(result)

    def __del__(self):
        print('-' * 20)