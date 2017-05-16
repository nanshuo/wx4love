from copy import deepcopy
from logging import handlers
import logging
import os, json
import requests
import datetime
import hashlib
import traceback

import random, string

ObjectId = lambda i: i

epoch = datetime.datetime(1970, 1, 1)

buildJob = lambda r, i, n, m: {'RequestJob': r, 'Order': i, 'Type': '%s_%s'%(n, m)}
fakeJob = lambda i, t: {"ID": "active","Data": i, "Queue": t, "Nacks": 0, "AdditionalDeliveries": 0}


def gen_randomchars(count=32, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(count))

def get_timestamp(t):
    return (t-epoch).total_seconds()

def get_uid(url):
    try: url = url.encode('utf8')
    except: pass
    md5 = hashlib.new("md5", url).hexdigest()
    first_half_bytes = md5[:16]
    last_half_bytes = md5[16:]
    first_half_int = int(first_half_bytes, 16)
    last_half_int = int(last_half_bytes, 16)
    xor_int = first_half_int ^ last_half_int
    uid = "%x" % xor_int
    return uid

def get_logger(name, only_msg=False):
    name = os.path.join(os.getenv('COMPINFO_LOG_PREFIX', ''), name)
    x = os.path.dirname(name)
    if x and not os.path.isdir(x): os.makedirs(x)
    formater = logging.Formatter("%(message)s" if only_msg else "%(asctime)s %(module)s:%(lineno)dL %(process)d [%(levelname)s]%(message)s")
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    _handler = handlers.TimedRotatingFileHandler(name, when='D', backupCount=1000)
    _handler.setFormatter(formater)
    logger.addHandler(_handler)
    return logger

def snake_get(obj, key, default=None):
    if not isinstance(obj, dict): return default
    keys = key.split('.')
    res = deepcopy(obj)
    l = len(keys)
    for i in xrange(l):
        if not isinstance(res, dict) and i<l-1: return default
        res = res.get(keys[i])
        # if not isinstance(res, dict) and : return default
    return res


class Queue(object):

    redis = None
    queue = 'default'

    def __init__(self, redis, queue, *args, **kvs):
        self.redis = redis
        self.queue = queue
        for k, v in kvs.items(): setattr(self, k, v)

    def len(self):
        return self.redis.scard(self.queue)

    def empty(self):
        return True if self.redis.scard(self.queue)<=0 else False

    def get(self, *args, **kvs):
        x = self.redis.spop(self.queue)
        if not x: return x
        if not x.startswith('{') and not x.startswith('['): return x
        try: return eval(x)
        except: return x

    def put(self, data):
        return self.redis.sadd(self.queue, data)

    @classmethod
    def Queue(cls, *args, **kvs):
        return cls(*args, **kvs)

def initJobqe(**kvs):
    class _(object):

        base_api = None

        def __init__(self, **kv):

            for k, v in kv.items(): setattr(self, k, v)
            if not self.base_api: raise Exception('should offer base api')
            self.job_url = "{0}/job/%s".format(self.base_api)
            self.stat_url = "{0}/channel/%s".format(self.base_api)
            self.ack_url = "{0}/ack".format(self.base_api)

        def close(self):
            pass

        def _str(self, data):
            return json.dumps(data) if isinstance(data, dict) or isinstance(data, list) else data

        def _request(self, method, url, *args, **kwargs):
            try: _ = requests.request(method, url, *args, **kwargs)
            except: traceback.print_exc(); return None
            if not _.ok: return None
            return _.json()
            try: __ = _.json(); return __["data"] if isinstance(__.get("data", ""), dict) else None
            except: traceback.print_exc(); return None

        def _get_data(self, url, *args, **kwargs):
            return self._request("GET", url, *args, **kwargs)

        def _post_data(self, url, *args, **kwargs):
            return self._request("POST", url, *args, **kwargs)

        def get_job(self, queue):
            return self._get_data(self.job_url%queue)

        def add_job(self, queue, data):
            return self._post_data(self.job_url%queue, data={"data": self._str(data)})

        def ack_job(self, jobid, data=""):
            return self._post_data(self.ack_url, params={"id": jobid}, data={"data": self._str(data)})

        def query_stat(self, queue):
            return self._get_data(self.stat_url%queue)

    return _(**kvs)

if __name__ == '__main__':
    from rediscluster import StrictRedisCluster
    _nodes = [{"host": "192.168.207.187","port": "9100"}]
    redis = StrictRedisCluster(startup_nodes=_nodes, max_connections=120)
    q = Queue.Queue(redis, 'seed.tmp.qcc.invester')
    print(q.get().keys())
    print(q.empty())
