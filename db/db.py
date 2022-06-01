# coding: utf-8
import pymysql
from DBUtils.PooledDB import PooledDB, SharedDBConnection
# from DBUtils.PersistentDB import PersistentDB, PersistentDBError, NotSupportedError

import sys 
sys.path.append("..") 
from igcrawler.utils import Singleton

config = {
    'host' : '157.182.212.97',
    'port' : 3306,
    'database' : 'drug',
    'user' : 'root',
    'password' : 'eT*&ExBQ:sC+Je9',
    'charset' : 'utf8',
    'cursorclass' : pymysql.cursors.DictCursor,
}

@Singleton
class Db(object):
    def __init__(self):
        super().__init__()
        self.pool = PooledDB(
            creator=pymysql,
            maxconnections=8,
            mincached=2,           
            maxcached=5,
            maxshared=3,
            blocking=True,
            setsession=['SET AUTOCOMMIT = 1;','set names utf8mb4;'],
            ping = 1,
            **config
        )

    def execute_sql(self, sql, params=[]):
        conn = self.pool.connection()
        with conn.cursor() as cursor:
            n = cursor.execute(sql, params)
        conn.close()
        return n

    def execute_many(self, sql, params):
        conn = self.pool.connection()
        with conn.cursor() as cursor:
            n = cursor.executemany(sql, params)
        conn.close()
        return n

    def exists(self, sql, params=[]):
        conn = self.pool.connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            data = cursor.fetchone()
        conn.close()
        return data


    def insert(self, table, **kwargs):
        fields = list(kwargs.keys())
        values = list(kwargs.values())
        occu = r'%s,' * len(values)
        occu = occu[:len(occu)-1]
        conn = self.pool.connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO " + table + " ( " + ",".join(fields) + " ) VALUES ( " + occu + " );"
            cursor.execute(sql, values)
        conn.close()
    

    def fetch_all(self, sql, parameters=[]):
        conn = self.pool.connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, parameters)
            lst = cursor.fetchall()
        conn.close()
        return list(lst)





# For testing this db operation class.
if __name__ == "__main__":
    db = Db()
    # db2 = Db(host = '157.182.212.97', user = 'root', pwd = 'eT*&ExBQ:sC+Je9', dbname = 'drug')
    # assert id(db) == id(db2), 'db != db2'
    # db.insert('test', **{'name':'zhangsan', 'age':222})
    # db.insert('test',  name='111++===', age= 222)
    # db2.insert('test', name='222++===', age= 222)
    l = db.fetch_all('select * from test where name=%s ', ['zhangsan', ])
    n = db.execute_sql("insert into test(name, age) values('hahh', 666) ")
    print(n)

    pass            