# -*- coding:utf-8 -*-
from flask import render_template
from flask.ext.login import current_user
import hashlib
import sys
import xml.etree.ElementTree as ET

from flask import Flask, request, make_response, current_app
from flask.ext.script import Manager


reload(sys)
sys.setdefaultencoding('utf-8')
from . import main

MAX_SEARCH_RESULTS = 50


@main.route('/', methods=['GET', 'POST'])
def wechat_auth():
    app = current_app._get_current_object()
    if request.method == 'GET':
        print 'coming Get'
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

    if request.method == 'POST':
        xml_str = request.stream.read()
        xml = ET.fromstring(xml_str)
        toUserName = xml.find('ToUserName').text
        fromUserName = xml.find('FromUserName').text
        createTime = xml.find('CreateTime').text
        msgType = xml.find('MsgType').text
        msgId = xml.find('MsgId').text
        if msgType != 'text':
            return render_template('text.html', toUserName=toUserName, fromUserName=fromUserName, createTime=createTime,
                                   msgType=msgType, msgId=msgId, Content='')

        content = xml.find('Content').text

        if type(content).__name__ == "unicode":
            content = content[::-1]
            content = content.encode('UTF-8')
        elif type(content).__name__ == "str":
            print type(content).__name__
            content = content.decode('utf-8')
            content = content[::-1]
        return render_template('text.html', toUserName=toUserName, fromUserName=fromUserName, createTime=createTime,
                               msgType=msgType, msgId=msgId, Content=content)
