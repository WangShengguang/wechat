from wechat.tyc.dao.db import DB
from wechat.tyc.dao.db_tools import try_commit_rollback_expunge
from wechat.tyc.dao.models.wx_models import WxUser


class MysqlDB(DB):
    def __init__(self, db='mysql'):
        super(MysqlDB, self).__init__(db)

    @try_commit_rollback_expunge
    def get_all_wx_users(self):
        wx_users = self.session.query(WxUser).all()
        return wx_users

    @try_commit_rollback_expunge
    def get_wx_user_by_name(self, user_name):
        wx_user = self.session.query(WxUser).filter_by(user_name=user_name).first()
        return wx_user
