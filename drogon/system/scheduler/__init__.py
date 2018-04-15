"""
    scheduler
    ~~~~~~~
    redis operator and the base class of scheduler
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-15
    :python version: 3.6
"""

import redis
import pickle

from drogon.settings import REDIS_HOST, REDIS_PORT, DB
from drogon.system.scheduler.bloom_filter import BloomFilter
from drogon.system.utils.http import request_to_dict, request_from_dict
from drogon.system.utils import to_unicode


class BaseRedis(object):
    def __init__(self, db):
        self._server = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=db)

    def get_pipeline(self):
        return self._server.pipeline()

    def push(self, obj):
        raise NotImplementedError

    def pop(self):
        raise NotImplementedError

    def set(self, key, value):
        raise NotImplementedError

    @staticmethod
    def get(key, server=None, db=DB):
        _server = server or BaseRedis.get_server(db)
        value = to_unicode(_server.get(key))
        return value

    @staticmethod
    def get_server(db=DB):
        return redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=db)

    @staticmethod
    def set(key, value, server=None, db=DB):
        _server = server or BaseRedis.get_server(db)
        _server.set(key, value)

    @staticmethod
    def delete(key, server=None, db=DB):
        _server = server or BaseRedis.get_server(db)
        _server.delete(key)


class BaseScheduler(BaseRedis):
    def __init__(self, spider, db=DB):
        super(BaseScheduler, self).__init__(db)
        self.task_id = spider.spider_id
        self.spider = spider
        self._filter = BloomFilter(key=self.task_id)

    def clear_queue(self):
        self._server.delete(self.task_id)

    def clear_filter(self):
        keys = self._server.keys(self.task_id + '*')
        for key in keys:
            if key != self.task_id:
                self._server.delete(key)

    def clear(self):
        keys = self._server.keys(self.task_id + '*')
        for key in keys:
            self._server.delete(key)