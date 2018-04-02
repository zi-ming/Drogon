
class Request(object):
    def __init__(self, url, data=None, headers=None, method='GET',
                 cookies=None, meta=None, callback=None, errback=None, priority=0,
                 allow_redirects=False, timeout=60, duplicate_remove=True, ignore_error=False):
        """
        请求对象
        :param url: 请求url
        :param form_data:   请求参数，POST情况下才用到，字典类型
        :param body: 请求参数，POST情况下才用到，字符串类型
        :param headers: 请求头信息
        :param method: 请求方法
        :param cookies: cookies值
        :param meta: meta值
        :param callback: 请求后回调的方法
        :param errback: 请求失败回调的方法
        :param priority: 请求优先级
        :param allow_redirects: 是否运行跳转重定向
        :param timeout: 请求超时时间
        :param duplicate_remove: 是否去重
        :param ignore_error: 是否无视错误（无论请求成功还是失败都回调callback，该值为Ture，则无视errback）
        """
        self.url = url
        self.form_data = form_data
        self.body = body
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
        self.ignore_error = ignore_error
        if self.ignore_error:
            self.errback = self.callback

    def str(self):
        return "<Request [%s] [%s]>"%(self.method, self.url)

    __repr__ = __str__
