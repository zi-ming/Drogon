"""
    proxy_pool.py
    ~~~~~~~
    read proxies from proxy file
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-02
    :python version: 3.6
"""

import sys
import os
from queue import Queue
from drogon.settings.default_settings import PROXY_PATH

class ProxyPool(object):
    def __init__(self):
        self._queue = Queue()
        if not os.path.exists(PROXY_PATH):
            return
        for line in open(PROXY_PATH):
            info = line.split(':')
            if len(info) == 2:
                proxy = {"http": "http://%s:%s" % (info[0], info[1]),
                         "https": "http://%s:%s" % (info[0], info[1])}
            elif len(info) == 4:
                proxy = {"http": "http://%s:%s@%s:%s/" % (info[2], info[3], info[0], info[1]),
                         "https": "http://%s:%s@%s:%s/" % (info[2], info[3], info[0], info[1])}
            else:
                continue
            self._queue.put(proxy)

    def __len__(self):
        return len(self._queue)

    def get(self):
        if not len(self):
            return None
        proxy = self._queue.get()
        self._queue.put(proxy)
        return proxy
