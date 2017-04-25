# coding: utf8

import datetime
import sys
import time
import random
import traceback

from helper import get_logger
from helper import initJobqe

from love_msg import get_msg_content

import settings

def wechat():
    logger = get_logger('logs/wechat.log')

    import time

    import itchat
    from itchat.content import TEXT

    @itchat.msg_register([TEXT])
    def text_reply(msg):
        logger.info('{0}: [{1}]{2}'.format(msg['FromUserName'], msg['Type'], msg['Text'].encode('utf8')))

    itchat.auto_login(enableCmdQR=True, hotReload=True)
    itchat.run(blockThread=False)

    logger.info("wechat login success.")

    while True:
        time.sleep(10)
        x = jobqe.get_job(settings.msg_queue_name)
        if not isinstance(x, dict): continue
        data = x.get('data')
        if not data or not isinstance(data, dict): continue
        try:
            msg = data.get('Data')
            touser = msg.get('to')
            content = msg.get('msg')
            if not touser or not content: continue
            touser = touser.strip()
            us = itchat.search_friends(name=touser)
            if len(us)==0: logger.info('no such user named: {0}'.format(touser)); continue
            u = us[0]
            itchat.send(content, toUserName=u["UserName"])
            logger.info('send "{0}" to "{1}".'.format(content.encode('utf8'), touser.encode('utf8')))
        except: logger.error(traceback.format_exc())
        jobqe.ack_job(x.get('ID'))

def add_msg():
    logger = get_logger('logs/add_msg.log')
    logger.info("run add msg.")

    # touser = "@36a15d89cf46b02ce81d353e50760a43"
    touser = "sisi-9209"

    _send_hour = []
    _send_day = 0

    while True:
        now = datetime.datetime.now()
        day = now.day
        hour = now.hour
        if _send_day != day: _send_hour = []
        if hour not in _send_hour:
            _send_day = day
            content = get_msg_content()
            _send_hour.append(hour)
            if content:
                msg = {"to": touser, "msg": content}
                logger.debug('msg: {0}'.format(content.encode('utf8')))
                logger.info("will send '{0}' to '{1}'".format(content.encode('utf8'), touser))
                jobqe.add_job(settings.msg_queue_name, msg)
        time.sleep(random.randint(1, 10) * 60)


def main():

    global jobqe
    jobqe = initJobqe(base_api=settings.queue_api_base)

    if len(sys.argv) > 1:
        if sys.argv[1] == 'wechat':
            wechat()
        elif sys.argv[1] == 'add':
            add_msg()
        else: print('unknow command.')
    else: print('must offer 1 argument.')


if __name__ == '__main__':
    main()
