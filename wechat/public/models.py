# -*- coding:utf-8 -*-

from . import db


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    ToUserName = db.Column(db.String(length=64), index=True)  # 微信原始id：gh_5xxxxx
    FromUserName = db.Column(db.String(length=64), index=True)
    MsgType = db.Column(db.String(length=64), index=True)
    MsgId = db.Column(db.String(length=64), index=True)
    Content = db.Column(db.Text)  # text  变长不可建索引
    recontent = db.Column(db.Text)  # text
    Title = db.Column(db.String(length=128), index=True)  # music
    Description = db.Column(db.String(length=128), index=True)  # music
    MusicUrl = db.Column(db.String(length=128), index=True)  # music
    HQMusicUrl = db.Column(db.String(length=128), index=True)  # music
    ThumbMediaId = db.Column(db.String(length=128), index=True)  # music
    PicUrl = db.Column(db.String(length=128), index=True)  # image
    MediaId = db.Column(db.String(length=128), index=True)  # image
    Encrypt = db.Column(db.Text)
    URL = db.Column(db.String(length=128))
    other = db.Column(db.Text)  # 其他信息
    CreateTime = db.Column(db.String(length=64), index=True)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    wx_unique_id = db.Column(db.String(length=64), db.ForeignKey('messages.FromUserName'), unique=True)
    name = db.Column(db.String(length=64), index=True)  # 微信原始id：gh_5xxxxx
    avatars = db.Column(db.String(length=128), index=True)
    location = db.Column(db.String(length=128), index=True)
    wecheat = db.Column(db.String(length=64), index=True)
    qq = db.Column(db.String(length=64), index=True)
    phone = db.Column(db.String(length=64), index=True)
    email = db.Column(db.String(length=64), index=True)
    messages = db.relationship('Message', backref='user')
    other = db.Column(db.Text)  # 其他信息
    CreateTime = db.Column(db.Text)


class Joke(db.Model):
    __tablename__ = 'jokes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(length=128))
    content = db.Column(db.Text)
    url = db.Column(db.String(length=128))
    web_site = db.Column(db.String(length=128))
    other = db.Column(db.Text)  # 其他信息
    createtime = db.Column(db.Text)
