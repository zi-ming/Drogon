"""
    proxy.py
    ~~~~~~~
    is mainly used for set request proxies and fill in proxy queue
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-15
    :python version: 3.6
"""

import time
import json
import traceback

from drogon.system.utils import to_unicode
from drogon.settings import PROXY_POOL_API
from drogon.system.logger import sys_logger as logger
from drogon.system.scheduler.queue import ProxyQueue
from drogon.system.scheduler.queue import SpiderStats
from drogon.system.downloader.base_downloader import BaseDownloader as Downloader

def handle_request_proxy(request):
    if not request:
        raise ValueError('request can not be None object.')
    proxy_queue = ProxyQueue()
    meta = request.meta
    set_proxy_confirm = not meta.get('proxies', None) and meta.get('use_proxy', False)
    if not set_proxy_confirm:
        set_proxy_confirm = meta.get('change_proxy', False)
    if set_proxy_confirm and proxy_queue.is_empty():
        retry_count = 0
        while True:
            try:
                resp = Downloader.get(PROXY_POOL_API)
                logger.debug(resp.text)
                _proxies = json.loads(resp.text)['proxyes']
                proxies = []
                for p in _proxies:
                    if len(p) != 4:
                        continue
                    proxies.append('http://{}:{}@{}:{}'.format(
                        p['user'], p['password'], p['host'], p['port']))
                if not proxies:
                    raise ValueError('proxy api return empty value')
            except Exception as e:
                logger.error('[{}]: {}'.format(request.spider_id, e))
                retry_count += 1
                time.sleep(2)
            else:
                proxy_queue.batch_push(proxies)
                break
            if retry_count == 5:
                SpiderStats.set_stop_stats(request.spider_id)
                logger.error( '[{}] proxy api connect error'.format(request.spider_id))
                return request

    if set_proxy_confirm:
        meta.pop('change_proxy', None)
        proxy = proxy_queue.pop()
        if not proxy:
            SpiderStats.set_stop_stats(request.spider_id)
            logger.error('[{}] proxy api connect error'.format(request.spider_id))
        else:
            proxy = to_unicode(proxy)
            meta['proxies'] = {
                'http': proxy,
                'https': proxy
            }
            request.meta.update(meta)
    return request