
import six
from drogon.system.downloader.http.request import Request

def request_to_dict(request, spider):
    cb = request.callback
    if callable(cb):
        cb = _find_method(spider, cb)
    eb = request.errback
    if callable(eb):
        eb = _find_method(spider, eb)
    d = {
        'url': request.url,
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
        'priority': request.priority,
    }
    return d

def request_from_dict(d, spider):
    cb = _get_method(spider, d['callback'])
    eb = _get_method(spider, d['errback'])
    return Request(
        url=d['url'],
        data=d['data'],
        allow_redirects=d['allow_redirects'],
        duplicate_remove=d['duplicate_remove'],
        timeout=d['timeout'],
        callback=cb,
        errback=eb,
        method=d['method'],
        headers=d['headers'],
        cookies=d['cookies'],
        meta=d['meta'],
        priority=d['priority'],
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
        'Function %s is not a method of %s'%(func, obj))

def _get_method(obj, name):
    if obj:
        try:
            return getattr(obj, name)
        except:
            pass
    raise AttributeError('method %s not found in %s' % (name, obj))