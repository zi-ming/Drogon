"""
    request.py
    ~~~~~~~
    Request module
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-15
    :python version: 3.6
"""

from drogon.settings import REQUEST_TIMEOUT

class Request(object):
    def __init__(self, url, spider=None, spider_id=None, data=None, headers=None,
                 method='GET', cookies=None, meta=None, callback=None, errback=None,
                 priority=0, allow_redirects=True, timeout=REQUEST_TIMEOUT, duplicate_remove=False):
        self.url = url
        self.data = data
        self.headers = headers
        self.method = method.upper()
        self.cookies = cookies or dict()
        self.meta = meta or dict()
        self.callback = callback
        self.errback = errback
        self.priority = priority
        self.allow_redirects = allow_redirects
        self.timeout = timeout
        self.duplicate_remove = duplicate_remove
        self.spider_id = spider_id
        if spider:
            self.spider_id = spider.spider_id
        if not self.spider_id:
            raise ValueError('spider_name and spider_id cat not be empty.')

    def __str__(self):
        return "<Request [%s] [%s]>"%(self.method, self.url)

    __repr__ = __str__
