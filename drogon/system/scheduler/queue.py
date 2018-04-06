
import redis
import pickle

from drogon.settings.default_settings import REDIS_HOST, REDIS_PORT
from drogon.system.scheduler.bloom_filter import BloomFilter
from drogon.system.utils.http import request_to_dict, request_from_dict

class Base(object):
    def __init__(self, spider):
        self.task_id = spider.spider_id
        self.spider = spider
        self._filter = BloomFilter(key=self.task_id)
        self._server = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

    def _get_pipeline(self):
        return self._server.pipeline()

    def push(self, obj):
        raise NotImplementedError

    def pop(self):
        raise NotImplementedError

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

class PriorityQueue(Base):
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

class FIFOQueue(Base):
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