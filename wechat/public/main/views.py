# -*- coding:utf-8 -*-
import hashlib
from xml.etree import ElementTree as ET

from flask import request, make_response, current_app, g

from wechat.public import db
from wechat.public.models import User, Message
from wechat.public.tools import message_response
from . import main


@main.route('/', methods=['GET'])
def wechat_auth():
    "接入微信平台时需要的验证; 验证消息确实来自微信服务器"
    app = current_app._get_current_object()
    data = request.args
    token = app.config.get('TOKEN')
    signature = data.get('signature', '')
    timestamp = data.get('timestamp', '')
    nonce = data.get('nonce', '')
    echostr = data.get('echostr', '')
    s = [timestamp, nonce, token]
    s.sort()
    s = ''.join(s)
    if (hashlib.sha1(s).hexdigest() == signature):
        return make_response(echostr)


@main.before_app_request
def before_request():
    """
    保存用户发送来的消息
    """
    xml_str = request.stream.read()
    xml = ET.fromstring(xml_str)
    request_arg = {chirld.tag: xml.find(chirld.tag).text or '' for chirld in xml.getchildren()}
    # 语音转换为位文字
    if request_arg['MsgType'] == 'voice':
        # 语音识别，res['Recognition'] 为识别结果
        request_arg['Content'] = request_arg['Recognition']
        request_arg['MsgType'] = 'text'
        print('voive--- ', request_arg['Content'])
    g.request_arg = request_arg


@main.after_app_request
def after_request(response):
    """
    保存返回消息
    :param response:
    :return:
    """
    # response_dict = g.response_dict
    msg = Message(**g.response_dic)
    user = User.query.filter_by(wx_unique_id=msg.FromUserName).first()
    if not user:
        user = User(wx_unique_id=msg.FromUserName, CreateTime=msg.CreateTime)
        db.session.add(user)
    db.session.add(msg)
    db.session.commit()
    return response


@main.route('/', methods=['POST'])
@message_response
def main():
    "主逻辑，微信用户发送的所有消息均在此处理"
    request_arg = g.request_arg
    msg_type = request_arg['MsgType']
    res = {}
    if msg_type == "text":
        res = ""  # 调用对应函数处理
    g.response_dict = res
    return res
