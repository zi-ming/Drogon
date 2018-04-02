from requests.models import Response as Response_obj

class Response(object):
    def __init__(self, response, request):
        """
        Response module
        :param response: 请求返回的requests.models对象
        :param request: Request对象
        """
        self.response = response
        self.request = request

    def __str__(self):
        if not self.response:
            return "<Response failed:[%s] [%s]>".format(
                self.response.status.code, self.response.url)
        if isinstance(self.response, Response_obj):
            return "<Response [%s] [%s] [%.2f KB]>".format(
                self.response.status.code, self.response.url, len(self.response.content) / 1000.0)
        else:
            return "<Response unknown:[%s] [%s]>".format(
                self.response.status.code, self.response.url)
    __repr__ = __str__