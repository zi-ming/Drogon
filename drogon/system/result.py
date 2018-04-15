"""
    result.py
    ~~~~~~~
    a result module
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-15
    :python version: 3.6
"""

import os
import requests
from hashlib import md5
from drogon.settings import RESULT_PATH

class Result(object):
    def __init__(self, response, spider, encoding=True):
        self.encoding = 'utf-8'
        if encoding:
            self.response = response.encode_response(response.response)
        else:
            self.response = response.response
        self.text = self.response.text
        self.content = self.response.content
        self.url = response.request.url
        self.request = response.request
        self.spider = spider
        self.result_id = md5(self.content).hexdigest()
        path = os.path.join(RESULT_PATH, self.spider.spider_id)
        self.path = os.path.join(path, self.result_id)

    def decode(self, encoding='utf-8'):
        self.content.decode(encoding)
        return self
