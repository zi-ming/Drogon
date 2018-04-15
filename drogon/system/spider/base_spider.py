"""
    base_spider.py
    ~~~~~~~
    the base class of spider module
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-15
    :python version: 3.6
"""

import types

from copy import deepcopy

from drogon.system.logger import Logger
from drogon.system.downloader.modules.request import Request
from drogon.system.utils import read_line_from_start_url_files

class BaseSpider(object):
    spider_id = None
    start_requests = []

    def __init__(self, spider_id):
        self.logger = Logger(spider_id).logger

    def fetch(self, **kwargs):
        _spider_settings = deepcopy(kwargs)
        _spider_settings.update({'spider': self})
        _spider_settings.update(**kwargs)
        return Request(**_spider_settings)

    def on_message(self):
        for line in read_line_from_start_url_files(self.spider_id) or []:
            tasks = self.on_start(line)
            if isinstance(tasks, types.GeneratorType):
                for task in tasks:
                    yield task
            else:
                yield tasks

    def on_start(self, data):
        pass

    def parse(self, response):
        raise NotImplementedError

    def retry_get(self, response):
        meta = response.request.meta
        retry_times = meta.get('retry_times', 0)
        if retry_times < getattr(self, 'MAX_RETRY_TIMES', 0):
            retry_times += 1
            self.logger.info('[RETRY] {} {}'.format(retry_times, response.request.url))
            meta.update({
                'retry_times': retry_times,
                'change_proxy': True
            })
            return response.request
        else:
            self.logger.info('[DROP] {}'.format(response.request.url))

    def retry_post(self, response):
        pass