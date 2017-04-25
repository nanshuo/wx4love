# coding: utf8
from pymongo import MongoClient
import datetime
import random

WORK_DAY_GETUP = 0
WORK_DAY_GETOUT = 1
WORK_DAY_TAKEON = 2
WORK_DAY_ARRIVE = 3
WORK_DAY_EATBREAKFEST = 4
WORK_DAY_EATLAUNCH = 5
WORK_DAY_EATDINNER = 6
WORK_DAY_OFFWORK = 7
WORK_DAY_TAKEOFFONNIGHT = 8

FRIDAY_NIGTH = 9

CALLS = [u'傻妞', u'妞', u'亲爱的', 'si', u'姐姐', u'小傻妞']
DEFAULT_WORDS = [u"我好想你", u"miss u", u"好想你", u"你人呢", u"想你哇"]

SPLITERS = [u'，', '', ',', ' ', u'、', '   ']

GETUP =  [u'我起床啦', u'起床了', u'我起来了', u'爬起来了我']
GETOUT = [u'我现在出门', u'已经出门啦', u'出门', u'下楼了']
TAKEON = [u'上车了', u'坐上了', u'上了', u'车上了']
ARRIVE = [u'到了', u'快到了', u'已经到了', u'已到', u'到啦']
EATB = [u'我在吃早饭', u'我在吃早餐', u'买早点中', u'我在买包子', u'买早餐吃我', u'我在万家买早餐']
EATL = [u'饭点啦', u'我们出去吃', u'我吃中饭了', u'lunch time', u'午饭了', u'正下食堂']
EATD = [u'吃晚饭了', u'下班了你', u'夜饭开始', u'dinner time', u'吃饭了', u'去食堂']
OFFWORK = [u'下班了', u'正下班', u'打卡中', u'等电梯下楼', u'正回去', u'上车了']
TAKEOF = [u'下车了', u'刚下车', u'到站了', u'下车了', u'刚下车']

FRIDAY_NIGTH = [u'今天早点回去', u'下班回去吃饭', u'现在下班', u'现在就回去', u'现在回']

WEEKEND_MON = [u'今天去哪里玩哇', u'今天天气咋样去哪玩呢', u'出去玩吧', u'出去玩吧', u'走 出去']

WORK_DAY_WORDS = [GETUP, GETOUT, TAKEON, ARRIVE, EATB, EATL, EATD, OFFWORK, TAKEOF]

friday_event_configuration = {
    7: WORK_DAY_WORDS[0],
    18: FRIDAY_NIGTH,
}

work_event_configuration = {
    7: WORK_DAY_WORDS[0],
    21: WORK_DAY_WORDS[7]
}

wend_event_configuration = {
    9: WEEKEND_MON,
}

def get_content():
    is_work_day, weekindex, hour, minute = get_time_info()
    if is_work_day:
        if weekindex==4:
            x = friday_event_configuration(hour)
        else:
            x = work_event_configuration.get(hour)
    else:
        x = wend_event_configuration.get(hour)
    return random.choice(x) if x else None

def get_msg_content(default=False):
    x = get_content()
    u = x if x else random.choice(DEFAULT_WORDS) if default else None
    if not u: return None
    s = random.choice(SPLITERS)
    c = random.choice(CALLS)
    return u'{0}{2}{1}'.format(c, u, s)

def get_calendar():
    import requests

    ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"
    url = "http://api.m.sm.cn/rest?method=sc.rili&request_sc=shortcut_searcher::rili&q={year}%E5%B9%B4{month}%E6%9C%8801%E6%97%A5"

    mongo_conn = MongoClient('mongodb://192.168.207.213:27016')
    mongo_db = mongo_conn['calendar']

    weeks = [u'一', u'二', u'三', u'四', u'五', u'六', u'日']

    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    todayv = None
    _url = url.format(year=now.strftime("%Y"), month=now.strftime("%m"))
    x = requests.get(_url, headers={'User-Agent': ua}).json()
    months = x.get('data', {}).get('month', [])
    for m in months:
        keys = m.keys()
        keys.sort(key=lambda i: datetime.datetime.strptime(i, "%Y-%m-%d"))
        for di in range(len(keys)):
            _ = m[keys[di]]
            vs = {k: v for k, v in _.items()}
            vs['weekIndex'] = di
            vs['week'] = weeks[di]
            if keys[di]==today: todayv = vs
            key = {'date': _['date']}
            print(_['date'])
            mongo_db['days'].update(key, {'$set': vs}, upsert=True)
    mongo_conn.close()
    return todayv

def get_day_info():
    mongo_conn = MongoClient('mongodb://192.168.207.213:27016')
    mongo_db = mongo_conn['calendar']

    d = datetime.datetime.now().strftime('%Y-%m-%d')
    d = d.replace('-0', '-')
    x = mongo_db['days'].find_one({'date': d})
    mongo_conn.close()
    if not x: return get_calendar()
    return x

def get_time_info():
    """
    return:
        (isWorkDay, timeSpace)
    """
    day_info = get_day_info()
    if not day_info: return None

    is_work_day = False if day_info['weekIndex']>=5 else True
    if day_info.get('worktime')==2: is_work_day = False

    now = datetime.datetime.now()

    return is_work_day, day_info['weekIndex'], now.hour, now.minute
    # x = event_configuration.get(hour)
    # return (isWorkDay, x) if x else None

if __name__ == '__main__':
    print(get_msg_content().encode('utf8'))
