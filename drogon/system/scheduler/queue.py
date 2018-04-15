"""
    queue.py
    ~~~~~~~
    the core of scheduler module
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-15
    :python version: 3.6
"""

import pickle

from drogon.system.scheduler import BaseScheduler, BaseRedis
from drogon.system.utils.http import request_to_dict, request_from_dict
from drogon.system.utils import to_unicode


class PriorityRequestQueue(BaseScheduler):
    def push_pipe(self, request, pipe):
        score = -request.priority
        data = pickle.dumps(request_to_dict(request, self.spider), protocol=-1)
        if not request.duplicate_remove:
            pipe.execute_command('ZADD', self.task_id, score, data)
        elif not self._filer.is_contains(data):
            pipe.execute_command('ZADD', self.task_id, score, data)
            self._filter.insert(data)

    def push(self, request):
        score = -request.priority
        data = pickle.dumps(request_to_dict(request, self.spider), protocol=-1)
        if not request.duplicate_remove:
            self._server.execute_command('ZADD', self.task_id, score, data)
        elif not self._filter.is_contains(data):
            self._server.execute_command('ZADD', self.task_id, score, data)
            self._filter.insert(data)

    def pop(self):
        pipe = self._server.pipeline()
        pipe.multi()
        pipe.zrange(self.task_id, 0, 0).zremrangebyrank(self.task_id, 0, 0)
        results, count = pipe.execute()
        if results:
            return request_from_dict(pickle.loads(results[0]), self.spider)
        else:
            return None

    def __len__(self):
        return self._server.zcard(self.task_id)

class FIFORequestQueue(BaseScheduler):
    def push(self, obj):
        self._server.execute_command('lpush', self.task_id, obj)

    def push_pipe(self, obj, pipe):
        pipe.execute_command('lpush', self.task_id, obj)

    def pop(self):
        pipe = self._server.pipeline()
        pipe.multi()
        results, count = pipe.execute()
        if results:
            return request_from_dict(cPickle.loads(results[0]), self.processor)
        else:
            return None

class ProxyQueue(BaseRedis):
    def __init__(self):
        super(ProxyQueue, self).__init__(db=0)
        self.key = 'PROXIES'

    def batch_push(self, proxies):
        self._server.sadd(self.key, *proxies)

    def pop(self):
        return self._server.spop(self.key)

    def is_empty(self):
        return len(self) == 0

    @staticmethod
    def clean():
        BaseRedis.delete('PROXIES')

    def __len__(self):
        return self._server.scard(self.key)

class SpiderStats(object):
    @staticmethod
    def set_started_stats(spider_id):
        key = '{}_STATS'.format(spider_id)
        BaseRedis.set(key, 'started')

    @staticmethod
    def set_stop_stats(spider_id):
        key = '{}_STATS'.format(spider_id)
        BaseRedis.set(key, 'stopped')

    @staticmethod
    def is_started_stats(spider_id):
        key = '{}_STATS'.format(spider_id)
        return BaseRedis.get(key) == 'started'

    @staticmethod
    def is_stop_stats(spider_id):
        key = '{}_STATS'.format(spider_id)
        return BaseRedis.get(key) == 'stopped'

    @staticmethod
    def clean(spider_id):
        key = '{}_STATS'.format(spider_id)
        BaseRedis.delete(key)

class CrawlStatus(object):
    def __init__(self, spider, db=0):
        super(CrawlStatus, self).__init__(db)
        self.task_id = spider.spider_id

    @staticmethod
    def increase(spider_id):
        key = '{}_CRAWL_STATUS'.format(spider_id)
        crawl_count = int((BaseRedis.get(key) or 0)) + 1
        BaseRedis.set(key, crawl_count)
        return crawl_count

    @staticmethod
    def get_status(spider_id):
        key = '{}_CRAWL_STATUS'.format(spider_id)
        return BaseRedis.get(key) or 0

    @staticmethod
    def clean(spider_id):
        key = '{}_CRAWL_STATUS'.format(spider_id)
        BaseRedis.delete(key)

