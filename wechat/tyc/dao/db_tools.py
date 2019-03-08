import datetime
import logging
import traceback
from collections import Iterable
from functools import wraps

from sqlalchemy import exc
from sqlalchemy.ext.declarative import declarative_base


def _declarative_constructor(self, **kwargs):
    cls_ = type(self)
    for k, v in kwargs.items():
        if not hasattr(cls_, k):
            raise TypeError("{} is an invalid keyword argument for {}".format(k, cls_.__name__))
        setattr(self, k, v)
    now = datetime.datetime.now()
    for time_key in ["create_time"]:
        if hasattr(cls_, time_key) and not getattr(self, time_key):
            setattr(self, time_key, now)
    for time_key in ["update_time"]:
        if hasattr(cls_, time_key):
            setattr(self, time_key, datetime.datetime.now())


_declarative_constructor.__name__ = "__init__"


class ToolMixin(object):
    def to_dict(self):
        _dic = {key: getattr(self, key) for key in self.__table__.columns.keys()}
        return _dic


BaseModel = declarative_base(cls=ToolMixin, constructor=_declarative_constructor)  # 创建一个类，这个类的子类可以自动与一个表关联


def try_commit_rollback(expunge=None):
    """ 装饰继承自DB的类的对象方法
        :param expunge: bool,将SQLAlchemy的数据对象实例转为一个简单的对象（切断与数据库会话的联系）
                         只在且在查询时尽量使用，做查询且返回sqlalchemy对象时使用，不知道就是用不到
    """

    def out_wrapper(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            res = None
            db_session = self.session
            try:
                res = func(self, *args, **kwargs)
                if expunge and res is not None:
                    if isinstance(res, Iterable):
                        [db_session.expunge(_data) for _data in res if isinstance(_data, BaseModel)]
                    elif isinstance(res, BaseModel):
                        db_session.expunge(res)
                    else:
                        raise TypeError("Please ensure object(s) is instance(s) of BaseModel")
                db_session.commit()
            except exc.IntegrityError as e:  # duplicate key
                db_session.rollback()
                logging.error("sqlalchemy.exc.IntegrityError: {}".format(e))
            except exc.DataError as e:  # invalid input syntax for uuid: "7ae16-ake"
                db_session.rollback()
                logging.error("sqlalchemy.exc.DataError: {}".format(e))
            except Exception:
                db_session.rollback()
                logging.error(traceback.format_exc())
            return res

        return wrapper

    return out_wrapper if isinstance(expunge, bool) else out_wrapper(expunge)


try_commit_rollback_expunge = try_commit_rollback(expunge=True)


def try_commit_rollback_dbsession(func):
    """装饰传入db_session对象的方法"""

    @wraps(func)
    def wrapper(self, db_session, *args, **kwargs):
        res = None
        try:
            res = func(self, db_session, *args, **kwargs)
            db_session.commit()
        except exc.IntegrityError as e:  # duplicate key
            db_session.rollback()
            logging.error("sqlalchemy.exc.IntegrityError: {}".format(e))
        except exc.DataError as e:  # invalid input syntax for uuid: "7ae16-ake"
            db_session.rollback()
            logging.error("sqlalchemy.exc.DataError: {}".format(e))
        except Exception:
            db_session.rollback()
            logging.error(traceback.format_exc())
        return res

    return wrapper
