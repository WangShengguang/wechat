from uuid import UUID

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, SMALLINT

from wechat.tyc.dao.db_tools import ToolMixin, BaseModel


class WxUser(BaseModel, ToolMixin):
    __tablename__ = 'wx_user'  # CHARSET=utf8mb4 COMMENT='用户信息';
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'schema': 'wechat'
    }
    id = Column(UUID, primary_key=True, comment="用户id")
    wechat = Column(VARCHAR(32), default="", comment="微信号")
    wx_name = Column(VARCHAR(32), default="", comment="微信用户名")
    user_name = Column(VARCHAR(32), default="", comment="真实姓名")
    gender = Column(SMALLINT, default=0, comment="性别[0-未填写，1-男，2-女，3-其他]")
    birthday = Column(DateTime, default="", comment="生日")
    description = Column(String(150), comment="描述")
    phone = Column(VARCHAR(32), comment="电话号码")
    email = Column(VARCHAR(100), default="", comment="邮箱")
    province = Column(VARCHAR(20), default="", comment="省")
    city = Column(VARCHAR(20), default="", comment="市")
    county = Column(VARCHAR(20), default="", comment="县")
    geo_location = Column(VARCHAR(128), default="", comment="地理定位经纬坐标")
    configuration = Column(TEXT, default="", comment="配置，基础命令")
    command = Column(TEXT, default="", comment="指令，json数据")
    last_operation_time = Column(DateTime(6), default="", comment="上次操作时间")
    update_time = Column(DateTime(6), default="", comment="资料更新时间")
    create_time = Column(DateTime(6), default="", comment="注册时间")

    def __str__(self):
        return '<WxUser> object,  id:{}'.format(self.id)


def create_all():
    from wechat.tyc.dao.db import mysql_db_engine
    BaseModel.metadata.create_all(mysql_db_engine)  # 创建表
