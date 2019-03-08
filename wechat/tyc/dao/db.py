# -*-coding:utf-8 -*-
"""
在此管理数据库连接
在连接池启用的情况下，session 只是对连接池中的连接进行操作：
session = Session() 将 Session 实例化的过程只是从连接池中取一个连接，在用完之后
使用 session.close()，session.commit(),session.rooback()还回到连接池中，而不是真正的关闭连接。
连接池禁用之后，sqlalchemy 会在查询之前创建连接，在查询结束，调用 session.close() 的时候关闭数据库连接。
 http://qinfei.glrsmart.com/2017/11/17/python-sqlalchemy-shu-ju-ku-lian-jie-chi/
"""
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from local_config import config  # 根目录下的配置文件

# sqlalchemy 一次只允许操作一个数据库，必须指定database
whiski_db_uri = 'mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8'.format(**config.whiski_db)
postgresql_db_uri = 'postgresql://{user}:{password}@{host}:{port}/{db}'.format(**config.postgresql)

# db_pool_config = {
#     "pool_pre_ping": True,  # 检查连接,无效则重置
#     "pool_size": 5,  # 连接数， 默认5
#     "max_overflow": 10,  # 超出pool_size后最多达到几个连接，超过部分使用后直接关闭，不放回连接池，默认为10，-1不限制
#     "pool_recycle": 7200,  # 连接重置周期，默认-1，推荐7200，表示连接在给定时间之后会被回收,勿超过mysql 默认8小时
#     "pool_timeout": 30  # 等待 pool_timeout 秒，没有获取到连接之后，放弃从池中获取连接
#     "echo": False 显示执行的SQL语句 #想查看语句直接print str(session.query(UserProfile).filter_by(user_id='xxxx'))
# }
mysql_db_engine = create_engine(whiski_db_uri, pool_size=5, pool_recycle=7200, pool_pre_ping=True, max_overflow=-1)
postgresql_db_engine = create_engine(postgresql_db_uri, pool_size=5, pool_recycle=7200, pool_pre_ping=True,
                                     max_overflow=-1)


class DB(object):
    def __init__(self, db='mysql'):
        self.__db = db
        session_factory = sessionmaker(bind=self.db_engine)  # autocommit=True若无开启Transaction，会自动commit
        # self.session = session_factory()
        self.session = scoped_session(session_factory)  # 多线程安全,每个线程使用单独数据库连接

    @property
    def db_engine(self):
        db_engine = {"mysql": mysql_db_engine, "postgresql": postgresql_db_engine}.get(self.__db)
        if db_engine:
            return db_engine
        raise ValueError("Please ensure your database is set up correctly")

    def select(self, sql, params=None):
        """
        :param sql: type str
        :param params: Optional dictionary, or list of dictionaries
        :return: result = session.execute(
                        "SELECT * FROM user WHERE id=:user_id",
                        {"user_id":5}
                    )
        """
        cursor = self.session.execute(sql, params)
        res = cursor.fetchall()
        self.session.commit()
        return res

    def execute(self, sql, params=None):
        """
        :param sql: type str
        :param params: Optional dictionary or list of dictionaries
        :return: result = session.execute(
                        "SELECT * FROM user WHERE id=:user_id",
                        {"user_id":5}
                    )
        """
        self.session.execute(sql, params)
        self.session.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            logging.info('save stage final,save error, session rollback ')
        finally:
            self.session.close()
        if exc_type is not None or exc_val is not None or exc_tb is not None:
            logging.info('exc_type: {}, exc_val: {}, exc_tb: {}'.format(exc_type, exc_val, exc_tb))

    def __del__(self):
        self.session.close()

# # redis
# redis_pool = redis.ConnectionPool(**config.redis, decode_responses=True)  # 公用连接池
#
#
# class Redis(object):
#     def __init__(self):
#         self.redis = redis.StrictRedis(connection_pool=redis_pool)  # 连接自动放回连接池
#
#
# # mongodb
# class Mongo(object):
#     # pass
#     connect(**config.mongodb)
#     # # 连接数据库，不存在则会自动创建
#     register_connection("whiski_db", "whiski", host=config.mongodb['host'])
#     register_connection("recommend_db", "recommend", host=config.mongodb['host'])
