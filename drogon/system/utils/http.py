"""
    http.py
    ~~~~~~~
    http commonly used tools
    :author: Max
    :copyright: (c) 2018
    :date created: 2018-04-15
    :python version: 3.6
"""

import six
from drogon.system.downloader.modules.request import Request
from drogon.system.utils import to_unicode

def request_to_dict(request, spider):
    cb = request.callback
    if callable(cb):
        cb = _find_method(spider, cb)
    eb = request.errback
    if callable(eb):
        eb = _find_method(spider, eb)
    d = {
        'url': to_unicode(request.url),
        'spider_id': request.spider_id,
        'callback': cb,
        'errback': eb,
        'data': request.data,
        'allow_redirects': request.allow_redirects,
        'duplicate_remove': request.duplicate_remove,
        'timeout': request.timeout,
        'method': request.method,
        'headers': request.headers,
        'cookies': request.cookies,
        'meta': request.meta,
        'priority': request.priority
    }
    return d

def request_from_dict(d, spider):
    cb = d['callback']
    if cb:
        cb = _get_method(spider, cb)
    eb = d['errback']
    if eb:
        eb = _get_method(spider, eb)
    return Request(
        url=to_unicode(d['url']),
        data=d['data'],
        spider_id=d['spider_id'],
        allow_redirects=d['allow_redirects'],
        duplicate_remove=d['duplicate_remove'],
        timeout=d['timeout'],
        callback=cb,
        errback=eb,
        method=d['method'],
        headers=d['headers'],
        cookies=d['cookies'],
        meta=d['meta'],
        priority=d['priority']
    )

def _find_method(obj, func):
    if obj:
        try:
            fun_self = six.get_method_self(func)
        except: # func has no __self__
            pass
        else:
            if fun_self is obj:
                return six.get_method_function(func).__name__
    raise AttributeError(
        'Function {} is not a method of {}'.format(func, obj))

def _get_method(obj, name):
    if obj:
        try:
            return getattr(obj, name)
        except:
            pass
    raise AttributeError('method {} not found in {}'.format(name, obj))