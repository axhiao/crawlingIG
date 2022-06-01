# coding: utf-8

import uuid

from db.db import Db
from pymysql.err import IntegrityError

class Model(object):
    def __init__(self):
        super().__init__()
        self.db = Db()

    # We choose hashtags which have not been blocked by IG yet.
    def get_tagname(self, good=True):
        if good:
            sql = "select name, is_broken from hashtag where is_broken=0 order by prob desc, update_gmt desc"
            #sql = "select name, is_broken from hashtag where is_broken = 0 order by update_gmt asc, prob desc"
        else:
            sql = "select name, is_broken from hashtag order by prob, update_gmt desc"
        return self.db.fetch_all(sql)


    def update_tag_status(self, tagname, broken = 1):
        sql = 'update hashtag set is_broken=%s where name=%s'
        if self.db.execute_sql(sql, [broken, tagname]) == 0:
            insert = 'insert ignore into hashtag(name, is_broken) values(%s,%s)'
            return self.db.execute_sql(insert, [tagname, broken])
        return 1

    def insert_hashtags(self, taglist):
        # for tag in taglist:
        sql = "insert ignore into hashtag(id, name) values(%s,%s)"
        values = [ [uuid.uuid4().int>>80, x] for x in taglist]
        self.db.execute_many(sql, values)


    def insert_hashtag(self, **kwargs):
        lst = [ (k, v) for k, v in kwargs.items()]
        s1 = ','.join([x[0] for x in lst])
        s2 = ','.join([x[0]+r'=%s' for x in lst])
        values = (r'%s,'*len(lst)).strip(',')
        sql = "insert into hashtag({}) values({}) on duplicate key update {}".format(
            s1, values, s2
        )
        vals = [ x[1] for x in lst] * 2
        self.db.execute_sql(sql, vals)

        # sql = "select count(1) as count from hashtag where name=%s"
        # params = kwargs['name']
        # data = self.db.exists(sql, [params])
        # if data['count'] == 0:
        #     self.db.insert('hashtag', **kwargs)
        # else:
        #     sql = "update hashtag set "
        #     lst = []
        #     for k, v in kwargs.items():
        #         sql += (k + r'=%s,')
        #         lst.append(v)
        #     sql = sql.strip(',')
        #     sql += r' where name=%s'
        #     lst.append(kwargs['name'])
        #     self.db.execute_sql(sql, lst)


    def insert_post(self, **kwargs):
        self.db.insert('posts', **kwargs)
    
    def insert_comment(self, **kwargs):
        try:
            self.db.insert('comments', **kwargs)
            return 1
        except IntegrityError:
            return 0
        except Exception:
            return -1
    
    def insert_user(self, **kwargs):
        self.db.insert('users', **kwargs)
    
    def insert_user_duplicate_update(self, **kwargs):
        lst = [ (k, v) for k, v in kwargs.items()]
        s1 = ','.join([x[0] for x in lst])
        s2 = ','.join([x[0]+r'=%s' for x in lst])
        values = (r'%s,'*len(lst)).strip(',')
        sql = "insert into users({}) values({}) on duplicate key update {}".format(
            s1, values, s2
        )
        vals = [ x[1] for x in lst] * 2
        return self.db.execute_sql(sql, vals)


    def exist_post(self, postid):
        return self._exist('posts', postid)

    def exist_post_by_shortcode(self, shortcode):
        sql = "select count(1) as count from posts where shortcode=%s"
        data = self.db.exists(sql, [shortcode])
        if data['count'] > 0:
            return True
        else:
            return False


    def exist_user(self, userid):
        return self._exist('users', userid)
    
    def get_comments(self, post_id):
        sql = f"""
        select id, text, from_unixtime(created_at) as created_at, owner_id, user_name, post_id from comments
        where post_id = {post_id};
        """
        return self.db.fetch_all(sql)

    def _exist(self, tbl, id):
        sql = "select count(1) as count from {} where id=%s".format(tbl)
        data = self.db.exists(sql, [id])
        if data['count'] > 0:
            return True
        else:
            return False


    def insert_relation(self, **kwargs):
        try:
            self.db.insert('relation', **kwargs)
            return 1
        except IntegrityError as ie:
            return 0
        except:
            return -1




    def test(self):
        pass
    